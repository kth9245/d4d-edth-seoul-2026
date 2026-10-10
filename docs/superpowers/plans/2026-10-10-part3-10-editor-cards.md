# Part3-10 편집기 카드 열(읽기 전용) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** cop-ui에 편집기 탭을 추가해 예시 작전(op1)과 플레이 8개를 읽기 전용 카드로 그린다.

**Architecture:** 계산은 `features/editor/`의 순수 함수 5개(vitest TDD), 화면은 그 결과를 그리기만 하는 컴포넌트 5개. 데이터는 `GET /operation`·`GET /plays`를 먼저 부르고 실패하면 번들된 시나리오 JSON으로 대체하며 화면에 표시한다. 탭은 `location.hash`.

**Tech Stack:** React 19, TypeScript 6, Vite 8, Vitest 3. 새 의존성 없음.

**Spec:** `docs/superpowers/specs/2026-10-10-part3-10-editor-cards-design.md`

## Global Constraints

- 작업 위치: worktree `/home/kth9245/HACKERTON/KDTH2026/.claude/worktrees/Part3-10`. 명령은 `modules/cop-ui`에서 `npm test`, `npm run build`. `cd`로 메인 폴더에 가지 않는다.
- 타입은 `src/contracts.gen.ts`만 쓴다(직접 수정 금지).
- `.ts`/`.tsx` 파일마다 200줄 이하(guard).
- 시간 제한 10/10 12:00 KST. Task 7(작전 개요)이 남으면 멈추고 Task 8로 마무리한다.
- 커밋은 `--no-verify` 없이. 커밋 메시지 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- 예시 데이터 대체는 개발용 스텁. 통합 2(10/11 00:00) 전에 걷어낸다(09 4.5절).
- 화면 문구는 한국어. 시나리오 JSON 경로(테스트·코드 공통): `src/features/editor/`에서 `../../../../../demo/scenarios/baengnyeong_night.json`.

## Review Focus

1. gateway 없이 `npm run dev`를 띄우면 `/operation`이 proxy 오류(500)나 index.html(200, JSON 아님)로 온다 → 예시 데이터로 대체되고 "예시 데이터(서버 없음)"가 보여야 한다. Task 5 테스트가 HTML 200을 다룬다.
2. 선택지·assign이 목록에 없는 플레이 id를 가리킴 → 화면이 깨지지 않고 빨간 자리표시. Task 3 테스트.
3. 선택지가 서로를 가리키는 순환(A → B → A) → `reachablePlays`가 끝나야 한다. Task 3 테스트.
4. `op.vehicle_ids`에 있지만 `assign`이 없는 기체 → 빈 열, 오류 없음. Task 3 테스트.
5. `domains`가 비었거나 둘 이상인 플레이 → "공통" 묶음. Task 2 테스트.

---

### Task 1: 행동·조건 한 줄 설명

**Files:**
- Create: `modules/cop-ui/src/features/editor/describe.ts`
- Test: `modules/cop-ui/src/features/editor/describe.test.ts`

**Interfaces:**
- Produces: `describeAction(a: Action): string`, `describeCondition(c: Condition): string`, `DOMAIN_LABEL: Record<Domain, string>`

- [ ] **Step 1: Write the failing test**

```ts
import { describe, expect, it } from "vitest";
import { describeAction, describeCondition } from "./describe";

describe("describeAction", () => {
  it("counts route points", () => {
    const route = [{ lat: 37.98, lon: 124.66 }, { lat: 37.98, lon: 124.74 }];
    expect(describeAction({ kind: "patrol_route", params: { route } })).toBe("순찰 경로 2점");
  });
  it("names the target rule and distance", () => {
    expect(describeAction({ kind: "watch_target", params: { target: "nearest", distance_m: 150 } }))
      .toBe("표적 감시 · 가장 가까운 표적 · 150m 거리");
    expect(describeAction({ kind: "watch_target", params: { target: "operator" } })).toBe("표적 감시 · 운용자가 고름");
    expect(describeAction({ kind: "approach_target", params: { target: "fast1" } })).toBe("표적 접근 · fast1");
  });
  it("prints a GeoPoint destination", () => {
    expect(describeAction({ kind: "move_to", params: { target: { lat: 37.975, lon: 124.7, alt_m: 0 } } }))
      .toBe("이동 · 37.975, 124.700");
  });
  it("is just the label without params", () => {
    expect(describeAction({ kind: "hold" })).toBe("대기");
  });
});

describe("describeCondition", () => {
  it("labels target_found", () => {
    expect(describeCondition({ kind: "target_found", params: {} })).toBe("표적 발견");
  });
  it("reads battery_below pct", () => {
    expect(describeCondition({ kind: "battery_below", params: { pct: 30 } })).toBe("배터리 30% 미만");
  });
  it("appends unknown params as key value", () => {
    expect(describeCondition({ kind: "time_elapsed", params: { sec: 60 } })).toBe("시간 경과 sec 60");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- src/features/editor/describe.test.ts`
Expected: FAIL, `Failed to resolve import "./describe"`

- [ ] **Step 3: Write minimal implementation**

```ts
import type { Action, ActionKind, Condition, ConditionKind, Domain } from "../../contracts.gen";

const ACTION_LABEL: Record<ActionKind, string> = {
  move_to: "이동",
  patrol_route: "순찰 경로",
  search_area: "구역 수색",
  return_home: "귀환",
  watch_target: "표적 감시",
  watch_point: "지점 감시",
  approach_target: "표적 접근",
  relay_comms: "통신 중계",
  hold: "대기",
};

const CONDITION_LABEL: Record<ConditionKind, string> = {
  target_found: "표적 발견",
  arrived: "도착",
  time_elapsed: "시간 경과",
  battery_below: "배터리",
  operator_choice: "운용자 선택",
  signal_received: "신호 수신",
};

export const DOMAIN_LABEL: Record<Domain, string> = { air: "드론", sea: "수상정", ground: "지상" };

function targetText(t: unknown): string {
  if (t === "nearest") return "가장 가까운 표적";
  if (t === "operator") return "운용자가 고름";
  if (typeof t === "string") return t;
  if (t && typeof t === "object" && "lat" in t && "lon" in t) {
    const p = t as { lat: number; lon: number };
    return `${p.lat.toFixed(3)}, ${p.lon.toFixed(3)}`;
  }
  return "";
}

export function describeAction(a: Action): string {
  const p = a.params ?? {};
  let head = ACTION_LABEL[a.kind];
  if (Array.isArray(p.route)) head += ` ${p.route.length}점`;
  const parts = [head];
  if (p.target !== undefined) parts.push(targetText(p.target));
  if (typeof p.distance_m === "number") parts.push(`${p.distance_m}m 거리`);
  return parts.filter(Boolean).join(" · ");
}

export function describeCondition(c: Condition): string {
  const p = c.params ?? {};
  if (c.kind === "battery_below" && p.pct !== undefined) return `배터리 ${p.pct}% 미만`;
  const rest = Object.entries(p).map(([k, v]) => `${k} ${v}`);
  return [CONDITION_LABEL[c.kind], ...rest].join(" ");
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test -- src/features/editor/describe.test.ts`
Expected: PASS (7 tests)

- [ ] **Step 5: Commit**

```bash
git add modules/cop-ui/src/features/editor/describe.ts modules/cop-ui/src/features/editor/describe.test.ts
git commit -m "Part3-10: describeAction/describeCondition one-line Korean text for step cards"
```

---

### Task 2: 플레이 영역별 묶음

**Files:**
- Create: `modules/cop-ui/src/features/editor/groupPlays.ts`
- Test: `modules/cop-ui/src/features/editor/groupPlays.test.ts`

**Interfaces:**
- Consumes: `DOMAIN_LABEL` (Task 1)
- Produces: `type PlayGroup = { key: Domain | "common"; label: string; plays: Play[] }`, `groupPlays(plays: Play[]): PlayGroup[]`

- [ ] **Step 1: Write the failing test**

```ts
import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { Play } from "../../contracts.gen";
import { groupPlays } from "./groupPlays";

const plays = scenario.plays as unknown as Play[];
const ids = (g: { plays: Play[] }) => g.plays.map((p) => p.id);

describe("groupPlays", () => {
  it("groups the scenario plays by single domain, multi-domain into common", () => {
    const groups = groupPlays(plays);
    expect(groups.map((g) => [g.label, ids(g)])).toEqual([
      ["드론", ["patrol_a", "watch", "patrol_b", "track_fast"]],
      ["수상정", ["approach"]],
      ["지상", ["landing"]],
      ["공통", ["standby", "go_home"]],
    ]);
  });
  it("puts a play without domains into common and drops empty groups", () => {
    const bare = { ...plays[0], id: "bare", domains: [] } as Play;
    expect(groupPlays([bare]).map((g) => [g.key, ids(g)])).toEqual([["common", ["bare"]]]);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- src/features/editor/groupPlays.test.ts`
Expected: FAIL, `Failed to resolve import "./groupPlays"`

- [ ] **Step 3: Write minimal implementation**

```ts
import type { Domain, Play } from "../../contracts.gen";
import { DOMAIN_LABEL } from "./describe";

export type PlayGroup = { key: Domain | "common"; label: string; plays: Play[] };

const ORDER: (Domain | "common")[] = ["air", "sea", "ground", "common"];
const LABEL: Record<Domain | "common", string> = { ...DOMAIN_LABEL, common: "공통" };

export function groupPlays(plays: Play[]): PlayGroup[] {
  const keyOf = (p: Play) => (p.domains.length === 1 ? p.domains[0] : "common");
  return ORDER.map((key) => ({ key, label: LABEL[key], plays: plays.filter((p) => keyOf(p) === key) })).filter(
    (g) => g.plays.length > 0,
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test -- src/features/editor/groupPlays.test.ts`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add modules/cop-ui/src/features/editor/groupPlays.ts modules/cop-ui/src/features/editor/groupPlays.test.ts
git commit -m "Part3-10: groupPlays puts plays under drone/sea/ground/common for the editor sidebar"
```

---

### Task 3: 기체별 열(시작 + 이어지는 플레이)

**Files:**
- Create: `modules/cop-ui/src/features/editor/vehicleColumns.ts`
- Test: `modules/cop-ui/src/features/editor/vehicleColumns.test.ts`

**Interfaces:**
- Produces: `type ColumnPlay = { play_id: string; play: Play | null; via: string | null }` (via = 선택지 label, 시작 플레이는 null), `type Column = { vehicle_id: string; reserve_for: string[]; plays: ColumnPlay[] }`, `reachablePlays(op: Operation, plays: Play[]): Play[]`, `vehicleColumns(op: Operation, plays: Play[]): Column[]`

- [ ] **Step 1: Write the failing test**

```ts
import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { Operation, Play } from "../../contracts.gen";
import { reachablePlays, vehicleColumns } from "./vehicleColumns";

const op = scenario.operation as unknown as Operation;
const plays = scenario.plays as unknown as Play[];
const summary = (o: Operation, p: Play[]) =>
  vehicleColumns(o, p).map((c) => [c.vehicle_id, c.reserve_for, c.plays.map((x) => [x.play_id, x.via])]);

describe("vehicleColumns", () => {
  it("lists each vehicle's start play then the plays its report choices lead to", () => {
    expect(summary(op, plays)).toEqual([
      ["d1", [], [["patrol_a", null], ["watch", "근접 확인"]]],
      ["d2", [], [["standby", null], ["patrol_b", "근접 확인"]]],
      ["d3", ["d1"], [["standby", null]]],
      ["usv", [], [["standby", null], ["approach", "근접 확인"]]],
      ["ugv", [], [["standby", null], ["landing", "근접 확인"]]],
    ]);
  });
  it("keeps switches out of the columns", () => {
    const all = vehicleColumns(op, plays).flatMap((c) => c.plays.map((x) => x.play_id));
    expect(all).not.toContain("go_home");
  });
  it("marks a missing play with play null", () => {
    const o = { ...op, vehicle_ids: ["d1"], assign: { d1: "ghost" } };
    expect(vehicleColumns(o, plays)[0].plays).toEqual([{ play_id: "ghost", play: null, via: null }]);
  });
  it("gives an empty column to a vehicle without assign", () => {
    const o = { ...op, vehicle_ids: ["x9"], assign: {}, reserve: {} };
    expect(vehicleColumns(o, plays)).toEqual([{ vehicle_id: "x9", reserve_for: [], plays: [] }]);
  });
});

describe("reachablePlays", () => {
  it("stops on a choice cycle", () => {
    const step = (to: string) => ({
      id: "s", name: "s", do: { kind: "hold" as const },
      report: { text: "t", choices: [{ id: "c", label: "c", play_by_vehicle: { v: to } }] },
    });
    const a = { id: "a", name: "A", domains: ["air" as const], entry: "s", steps: [step("b")] };
    const b = { id: "b", name: "B", domains: ["air" as const], entry: "s", steps: [step("a")] };
    const o = { ...op, vehicle_ids: ["v"], assign: { v: "a" } };
    expect(reachablePlays(o, [a, b]).map((p) => p.id)).toEqual(["a", "b"]);
    expect(vehicleColumns(o, [a, b])[0].plays.map((x) => x.play_id)).toEqual(["a", "b"]);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- src/features/editor/vehicleColumns.test.ts`
Expected: FAIL, `Failed to resolve import "./vehicleColumns"`

- [ ] **Step 3: Write minimal implementation**

```ts
import type { Choice, Operation, Play } from "../../contracts.gen";

export type ColumnPlay = { play_id: string; play: Play | null; via: string | null };
export type Column = { vehicle_id: string; reserve_for: string[]; plays: ColumnPlay[] };

export function choicesOf(play: Play): Choice[] {
  return play.steps.flatMap((s) => s.report?.choices ?? []);
}

// Plays the operation can reach: assigned plays, then every play a report choice points to (BFS, each once).
export function reachablePlays(op: Operation, plays: Play[]): Play[] {
  const byId = new Map(plays.map((p) => [p.id, p]));
  const queue = Object.values(op.assign ?? {});
  const seen = new Set<string>();
  const out: Play[] = [];
  while (queue.length > 0) {
    const id = queue.shift()!;
    if (seen.has(id)) continue;
    seen.add(id);
    const play = byId.get(id);
    if (!play) continue;
    out.push(play);
    for (const c of choicesOf(play)) queue.push(...Object.values(c.play_by_vehicle ?? {}));
  }
  return out;
}

// One column per vehicle: its start play, then plays reachable choices send it to. Switches stay out.
export function vehicleColumns(op: Operation, plays: Play[]): Column[] {
  const byId = new Map(plays.map((p) => [p.id, p]));
  const reach = reachablePlays(op, plays);
  return op.vehicle_ids.map((v) => {
    const out: ColumnPlay[] = [];
    const add = (id: string, via: string | null) => {
      if (!out.some((c) => c.play_id === id)) out.push({ play_id: id, play: byId.get(id) ?? null, via });
    };
    const start = op.assign?.[v];
    if (start) add(start, null);
    for (const p of reach) {
      for (const c of choicesOf(p)) {
        const next = c.play_by_vehicle?.[v];
        if (next) add(next, c.label);
      }
    }
    const reserve_for = Object.entries(op.reserve ?? {})
      .filter(([, ids]) => ids.includes(v))
      .map(([id]) => id);
    return { vehicle_id: v, reserve_for, plays: out };
  });
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test -- src/features/editor/vehicleColumns.test.ts`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add modules/cop-ui/src/features/editor/vehicleColumns.ts modules/cop-ui/src/features/editor/vehicleColumns.test.ts
git commit -m "Part3-10: vehicleColumns gives each vehicle its start play and the plays report choices lead to"
```

---

### Task 4: 플레이를 쓰는 기체

**Files:**
- Create: `modules/cop-ui/src/features/editor/playUsage.ts`
- Test: `modules/cop-ui/src/features/editor/playUsage.test.ts`

**Interfaces:**
- Consumes: `choicesOf(play: Play): Choice[]` (Task 3)
- Produces: `type Usage = { vehicle_id: string; how: string }`, `playUsage(op: Operation, plays: Play[]): Record<string, Usage[]>`

- [ ] **Step 1: Write the failing test**

```ts
import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { Operation, Play } from "../../contracts.gen";
import { playUsage } from "./playUsage";

const op = scenario.operation as unknown as Operation;
const plays = scenario.plays as unknown as Play[];

describe("playUsage", () => {
  const u = playUsage(op, plays);
  it("names the operation start", () => {
    expect(u["patrol_a"]).toEqual([{ vehicle_id: "d1", how: "작전 시작" }]);
    expect(u["standby"].map((x) => x.vehicle_id)).toEqual(["d2", "d3", "usv", "ugv"]);
  });
  it("names the play and choice that lead here", () => {
    expect(u["patrol_b"]).toEqual([{ vehicle_id: "d2", how: "해안 순찰 A의 '근접 확인' 뒤" }]);
  });
  it("names the operation switch", () => {
    expect(u["go_home"]).toHaveLength(5);
    expect(u["go_home"][0]).toEqual({ vehicle_id: "d1", how: "전체 전환 '전 기체 귀환'" });
  });
  it("has no entry for an unused play", () => {
    expect(u["track_fast"]).toBeUndefined();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- src/features/editor/playUsage.test.ts`
Expected: FAIL, `Failed to resolve import "./playUsage"`

- [ ] **Step 3: Write minimal implementation**

```ts
import type { Operation, Play } from "../../contracts.gen";
import { choicesOf } from "./vehicleColumns";

export type Usage = { vehicle_id: string; how: string };

// Which vehicles run each play and how they get there: operation start, a report choice, or a switch.
export function playUsage(op: Operation, plays: Play[]): Record<string, Usage[]> {
  const out: Record<string, Usage[]> = {};
  const push = (playId: string, u: Usage) => (out[playId] ??= []).push(u);
  for (const [v, pid] of Object.entries(op.assign ?? {})) push(pid, { vehicle_id: v, how: "작전 시작" });
  for (const p of plays) {
    for (const c of choicesOf(p)) {
      for (const [v, pid] of Object.entries(c.play_by_vehicle ?? {})) {
        push(pid, { vehicle_id: v, how: `${p.name}의 '${c.label}' 뒤` });
      }
    }
  }
  for (const sw of op.switches ?? []) {
    for (const [v, pid] of Object.entries(sw.play_by_vehicle)) push(pid, { vehicle_id: v, how: `전체 전환 '${sw.label}'` });
  }
  return out;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test -- src/features/editor/playUsage.test.ts`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add modules/cop-ui/src/features/editor/playUsage.ts modules/cop-ui/src/features/editor/playUsage.test.ts
git commit -m "Part3-10: playUsage lists which vehicles run each play and how they get there"
```

---

### Task 5: 데이터 불러오기 + vite 설정

**Files:**
- Create: `modules/cop-ui/src/features/editor/loadEditorData.ts`
- Test: `modules/cop-ui/src/features/editor/loadEditorData.test.ts`
- Modify: `modules/cop-ui/vite.config.ts` (전체 교체)

**Interfaces:**
- Produces: `type EditorData = { operation: Operation; plays: Play[]; source: "gateway" | "example" }`, `loadEditorData(f?: (url: string) => Promise<Response>): Promise<EditorData>` (절대 reject하지 않음)

- [ ] **Step 1: Write the failing test**

```ts
import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import { loadEditorData } from "./loadEditorData";

const json = (body: unknown, status = 200) => Promise.resolve(new Response(JSON.stringify(body), { status }));

describe("loadEditorData", () => {
  it("uses the gateway when both calls succeed", async () => {
    const op = { ...scenario.operation, id: "op-gw" };
    const d = await loadEditorData((url) => json(url === "/operation" ? op : [scenario.plays[0]]));
    expect(d.source).toBe("gateway");
    expect(d.operation.id).toBe("op-gw");
    expect(d.plays).toHaveLength(1);
  });
  it("falls back to the example scenario on a network error", async () => {
    const d = await loadEditorData(() => Promise.reject(new TypeError("fetch failed")));
    expect(d.source).toBe("example");
    expect(d.operation.id).toBe(scenario.operation.id);
    expect(d.plays).toHaveLength(8);
  });
  it("falls back on a non-2xx answer", async () => {
    const d = await loadEditorData(() => json({ detail: "x" }, 500));
    expect(d.source).toBe("example");
  });
  it("falls back when the dev server answers index.html", async () => {
    const d = await loadEditorData(() => Promise.resolve(new Response("<!doctype html>", { status: 200 })));
    expect(d.source).toBe("example");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- src/features/editor/loadEditorData.test.ts`
Expected: FAIL, `Failed to resolve import "./loadEditorData"`

- [ ] **Step 3: Write minimal implementation**

```ts
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { Operation, Play } from "../../contracts.gen";

export type EditorData = { operation: Operation; plays: Play[]; source: "gateway" | "example" };
type Fetch = (url: string) => Promise<Response>;

// Dev stub until Part1-7 serves GET /operation and GET /plays. Remove before integration 2 (09 §4.5).
const EXAMPLE = scenario as unknown as { operation: Operation; plays: Play[] };

async function getJson<T>(f: Fetch, url: string): Promise<T> {
  const r = await f(url);
  if (!r.ok) throw new Error(`${url} answered ${r.status}`);
  return (await r.json()) as T;
}

export async function loadEditorData(f: Fetch = (url) => fetch(url)): Promise<EditorData> {
  try {
    const [operation, plays] = await Promise.all([getJson<Operation>(f, "/operation"), getJson<Play[]>(f, "/plays")]);
    return { operation, plays, source: "gateway" };
  } catch (e) {
    console.warn("editor: gateway unavailable, showing example data", e);
    return { operation: EXAMPLE.operation, plays: EXAMPLE.plays, source: "example" };
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test -- src/features/editor/loadEditorData.test.ts`
Expected: PASS (4 tests)

- [ ] **Step 5: Replace `vite.config.ts`**

```ts
import { realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const REPO = fileURLToPath(new URL("../..", import.meta.url)); // editor reads demo/scenarios
const NODE_MODULES = realpathSync(fileURLToPath(new URL("./node_modules", import.meta.url))); // symlinked in worktrees
const API = { target: "http://localhost:8000" };

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/ws": { target: "ws://localhost:8000", ws: true }, "/operation": API, "/plays": API },
    fs: { allow: [REPO, NODE_MODULES] },
  },
});
```

- [ ] **Step 6: Build to check types and config**

Run: `npm run build`
Expected: `tsc -b` 오류 없음, `vite build` 완료

- [ ] **Step 7: Commit**

```bash
git add modules/cop-ui/src/features/editor/loadEditorData.ts modules/cop-ui/src/features/editor/loadEditorData.test.ts modules/cop-ui/vite.config.ts
git commit -m "Part3-10: loadEditorData asks the gateway and falls back to the bundled example scenario; vite proxies /operation and /plays"
```

---

### Task 6: 플레이 화면 + 왼쪽 바 + 탭

**Files:**
- Create: `modules/cop-ui/src/features/editor/StepCard.tsx`, `PlayWorkflow.tsx`, `PlaySidebar.tsx`, `EditorScreen.tsx`
- Create: `modules/cop-ui/src/features/nav/tab.ts`, Test: `modules/cop-ui/src/features/nav/tab.test.ts`
- Modify: `modules/cop-ui/src/App.tsx` (전체 교체), `modules/cop-ui/src/index.css` (끝에 추가)

**Interfaces:**
- Consumes: Task 1~5 전부
- Produces: `OVERVIEW = "__overview__"` (PlaySidebar.tsx), `EditorScreen()`, `tabFromHash(hash: string): "editor" | "live"`

- [ ] **Step 1: Write the failing test for the tab**

```ts
import { describe, expect, it } from "vitest";
import { tabFromHash } from "./tab";

describe("tabFromHash", () => {
  it("opens the editor only on #editor", () => {
    expect(tabFromHash("#editor")).toBe("editor");
    expect(tabFromHash("#live")).toBe("live");
    expect(tabFromHash("")).toBe("live");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- src/features/nav/tab.test.ts`
Expected: FAIL, `Failed to resolve import "./tab"`

- [ ] **Step 3: Implement `tab.ts`**

```ts
export type Tab = "editor" | "live";

export function tabFromHash(hash: string): Tab {
  return hash === "#editor" ? "editor" : "live";
}
```

Run: `npm test -- src/features/nav/tab.test.ts` → PASS

- [ ] **Step 4: `StepCard.tsx`**

```tsx
import type { Play, Step } from "../../contracts.gen";
import { describeAction, describeCondition } from "./describe";

type Props = { step: Step; play: Play; playName: (id: string) => string | null; onOpen: (playId: string) => void };

export function StepCard({ step, play, playName, onOpen }: Props) {
  const stepName = (id: string) => play.steps.find((s) => s.id === id)?.name;
  return (
    <div className="step-card">
      <div className="step-name">
        {step.id === play.entry ? "▶ " : ""}
        {step.name}
      </div>
      <div className="step-do">{describeAction(step.do)}</div>
      {(step.on ?? []).map((e, i) => (
        <div key={i} className="step-exit">
          {describeCondition(e.cond)} → {stepName(e.go_step) ?? <span className="missing">{e.go_step}</span>}
        </div>
      ))}
      {step.report && (
        <div className="step-report">
          <div>■ {step.report.text}</div>
          {(step.report.choices ?? []).map((c) => (
            <div key={c.id} className="choice">
              <b>[{c.label}]</b>
              {Object.entries(c.play_by_vehicle ?? {}).map(([v, pid]) => {
                const name = playName(pid);
                return (
                  <div key={v} className="choice-target">
                    {v} →{" "}
                    {name ? (
                      <button className="link" onClick={() => onOpen(pid)}>
                        {name}
                      </button>
                    ) : (
                      <span className="missing">{pid}</span>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 5: `PlayWorkflow.tsx`**

```tsx
import type { Play } from "../../contracts.gen";
import { DOMAIN_LABEL } from "./describe";
import type { Usage } from "./playUsage";
import { StepCard } from "./StepCard";

type Props = { play: Play; usage: Usage[]; playName: (id: string) => string | null; onOpen: (playId: string) => void };

export function PlayWorkflow({ play, usage, playName, onOpen }: Props) {
  return (
    <section className="workflow">
      <h2>
        {play.name} <small>{play.domains.map((d) => DOMAIN_LABEL[d]).join("·") || "영역 없음"}</small>
      </h2>
      <div className="usage">
        {usage.length === 0
          ? "이 작전에서 쓰는 기체 없음"
          : usage.map((u, i) => (
              <div key={i}>
                {u.vehicle_id} — {u.how}
              </div>
            ))}
      </div>
      {play.steps.map((s) => (
        <StepCard key={s.id} step={s} play={play} playName={playName} onOpen={onOpen} />
      ))}
    </section>
  );
}
```

- [ ] **Step 6: `PlaySidebar.tsx`**

```tsx
import type { EditorData } from "./loadEditorData";
import type { PlayGroup } from "./groupPlays";

export const OVERVIEW = "__overview__";

type Props = {
  groups: PlayGroup[];
  selected: string;
  source: EditorData["source"];
  showOverview: boolean;
  onSelect: (id: string) => void;
};

export function PlaySidebar({ groups, selected, source, showOverview, onSelect }: Props) {
  const item = (id: string, label: string) => (
    <button key={id} className={selected === id ? "item on" : "item"} onClick={() => onSelect(id)}>
      {label}
    </button>
  );
  return (
    <nav className="play-sidebar">
      {source === "example" && <div className="example-badge">예시 데이터(서버 없음)</div>}
      {showOverview && item(OVERVIEW, "작전 개요")}
      {groups.map((g) => (
        <div key={g.key}>
          <div className="group">{g.label}</div>
          {g.plays.map((p) => item(p.id, p.name))}
        </div>
      ))}
    </nav>
  );
}
```

- [ ] **Step 7: `EditorScreen.tsx`** (작전 개요 없이. Task 7이 `OperationOverview`를 끼운다)

```tsx
import { useEffect, useMemo, useState } from "react";
import { groupPlays } from "./groupPlays";
import { type EditorData, loadEditorData } from "./loadEditorData";
import { PlaySidebar } from "./PlaySidebar";
import { playUsage } from "./playUsage";
import { PlayWorkflow } from "./PlayWorkflow";

export function EditorScreen() {
  const [data, setData] = useState<EditorData | null>(null);
  const [selected, setSelected] = useState<string>("");
  useEffect(() => {
    loadEditorData().then(setData);
  }, []);
  const view = useMemo(
    () =>
      data && {
        groups: groupPlays(data.plays),
        usage: playUsage(data.operation, data.plays),
        byId: new Map(data.plays.map((p) => [p.id, p])),
      },
    [data],
  );
  if (!data || !view) return <div className="editor">불러오는 중…</div>;
  const playName = (id: string) => view.byId.get(id)?.name ?? null;
  const play = view.byId.get(selected) ?? view.groups[0]?.plays[0]; // first play in the sidebar, not data.plays[0] (standby)
  return (
    <div className="editor">
      <PlaySidebar groups={view.groups} selected={play?.id ?? ""} source={data.source} showOverview={false} onSelect={setSelected} />
      <main className="editor-main">
        {play ? (
          <PlayWorkflow play={play} usage={view.usage[play.id] ?? []} playName={playName} onOpen={setSelected} />
        ) : (
          "플레이 없음"
        )}
      </main>
    </div>
  );
}
```

- [ ] **Step 8: Replace `App.tsx`** (WS는 탭과 무관하게 계속 연결)

```tsx
import { useEffect, useState } from "react";
import { AlertList } from "./features/alerts/AlertList";
import { EditorScreen } from "./features/editor/EditorScreen";
import { useFrames } from "./features/live/useFrames";
import { tilesExist } from "./features/map/basemap";
import { MapView } from "./features/map/MapView";
import { tabFromHash } from "./features/nav/tab";

const WS_URL = `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`;
const CENTER: [number, number] = [126.978, 37.5665];

export default function App() {
  const { frame, connected } = useFrames(WS_URL);
  const [tiles, setTiles] = useState<boolean | null>(null);
  const [hash, setHash] = useState(location.hash);
  useEffect(() => {
    tilesExist().then(setTiles);
    const onHash = () => setHash(location.hash);
    addEventListener("hashchange", onHash);
    return () => removeEventListener("hashchange", onHash);
  }, []);
  const tab = tabFromHash(hash);
  return (
    <div className="app">
      <header className="tabs">
        <a href="#editor" className={tab === "editor" ? "on" : ""}>편집기</a>
        <a href="#live" className={tab === "live" ? "on" : ""}>상황판</a>
      </header>
      {tab === "editor" ? (
        <EditorScreen />
      ) : (
        <div className="layout">
          {tiles !== null && <MapView frame={frame} center={CENTER} tilesAvailable={tiles} />}
          <aside>
            <div className={connected ? "status ok" : "status down"}>{connected ? "LIVE" : "연결 끊김"}</div>
            <AlertList frame={frame} />
          </aside>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 9: Append to `index.css`**

```css
.app { display: flex; flex-direction: column; height: 100%; }
.app > .layout, .app > .editor { flex: 1; min-height: 0; }
.tabs { display: flex; gap: 4px; padding: 6px 12px; border-bottom: 1px solid #22304a; }
.tabs a { color: #9fb0cc; text-decoration: none; padding: 4px 12px; border-radius: 6px; }
.tabs a.on { background: #14213a; color: #fff; font-weight: 700; }
.editor { display: grid; grid-template-columns: 220px 1fr; }
.play-sidebar { overflow-y: auto; padding: 12px; border-right: 1px solid #22304a; }
.play-sidebar .group { margin: 12px 0 4px; font-size: 12px; opacity: 0.7; }
.play-sidebar .item { display: block; width: 100%; text-align: left; padding: 6px 8px; margin: 2px 0; border: 0; border-radius: 6px; background: none; color: inherit; cursor: pointer; }
.play-sidebar .item.on { background: #1d3157; font-weight: 700; }
.example-badge { padding: 6px 8px; border-radius: 6px; background: #5c3b00; color: #ffd591; font-size: 12px; }
.editor-main { overflow: auto; padding: 16px; }
.workflow { max-width: 420px; }
.workflow h2 small { font-size: 12px; opacity: 0.7; }
.usage { font-size: 13px; opacity: 0.85; margin-bottom: 12px; }
.step-card { padding: 10px; margin-bottom: 8px; border-radius: 8px; background: #14213a; border-left: 4px solid #3a6df0; }
.step-name { font-weight: 700; } .step-do { margin: 4px 0; } .step-exit { font-size: 13px; opacity: 0.85; }
.step-report { margin-top: 6px; padding: 6px; border-radius: 6px; background: #1f2b45; font-size: 13px; }
.choice { margin-top: 4px; } .choice-target { padding-left: 12px; }
.link { border: 0; padding: 0; background: none; color: #69b1ff; cursor: pointer; text-decoration: underline; font: inherit; }
.missing { color: #ff4d4f; }
```

- [ ] **Step 10: Run all tests and build**

Run: `npm test && npm run build`
Expected: 테스트 전부 PASS, build 오류 없음

- [ ] **Step 11: Look at it**

Run (background): `npm run dev -- --port 5180`
`http://localhost:5180/#editor`를 브라우저나 headless 캡처로 열어 확인: 왼쪽 위 "예시 데이터(서버 없음)", 드론·수상정·지상·공통 묶음에 플레이 8개, 첫 화면 "해안 순찰 A" 카드 2장(▶ 경로 A 순찰 / 보고: 미식별 선박 접근, [근접 확인] 아래 d1·usv·ugv·d2 → 플레이 이름), 플레이 이름을 누르면 그 플레이로 이동, `#live` 탭에서 기존 지도. 확인 뒤 dev 서버 종료.

- [ ] **Step 12: Commit**

```bash
git add modules/cop-ui/src/features/editor modules/cop-ui/src/features/nav modules/cop-ui/src/App.tsx modules/cop-ui/src/index.css
git commit -m "Part3-10: editor tab with play sidebar and one play's read-only step cards"
```

---

### Task 7: 작전 개요 (12:00가 지났으면 건너뛰고 Task 8)

**Files:**
- Create: `modules/cop-ui/src/features/editor/OperationOverview.tsx`
- Modify: `modules/cop-ui/src/features/editor/EditorScreen.tsx`, `modules/cop-ui/src/index.css`

**Interfaces:**
- Consumes: `vehicleColumns`, `Column` (Task 3), `StepCard` (Task 6), `OVERVIEW` (Task 6)

- [ ] **Step 1: `OperationOverview.tsx`**

```tsx
import type { Operation } from "../../contracts.gen";
import { StepCard } from "./StepCard";
import type { Column } from "./vehicleColumns";

type Props = { op: Operation; columns: Column[]; playName: (id: string) => string | null; onOpen: (playId: string) => void };

export function OperationOverview({ op, columns, playName, onOpen }: Props) {
  const switches = op.switches ?? [];
  return (
    <section className="overview">
      <h2>{op.name}</h2>
      {switches.length > 0 && (
        <div className="switches">
          전체 전환:{" "}
          {switches.map((s) => (
            <span key={s.id} className="switch">[{s.label}]</span>
          ))}
        </div>
      )}
      <div className="columns">
        {columns.map((col) => (
          <div key={col.vehicle_id} className="column">
            <div className="column-head">
              {col.vehicle_id}
              {col.reserve_for.length > 0 && <small> 예비: {col.reserve_for.join(", ")} 대신</small>}
            </div>
            {col.plays.map((cp) => (
              <div key={cp.play_id}>
                {cp.via && <div className="via">↓ '{cp.via}' 선택 시</div>}
                {cp.play ? (
                  <>
                    <button className="link play-title" onClick={() => onOpen(cp.play_id)}>{cp.play.name}</button>
                    {cp.play.steps.map((s) => (
                      <StepCard key={s.id} step={s} play={cp.play!} playName={playName} onOpen={onOpen} />
                    ))}
                  </>
                ) : (
                  <div className="step-card missing">없는 플레이: {cp.play_id}</div>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Wire it into `EditorScreen.tsx`**

`import { OperationOverview } from "./OperationOverview";`, `import { OVERVIEW, PlaySidebar } from "./PlaySidebar";`, `import { vehicleColumns } from "./vehicleColumns";` 추가. 그리고:

```tsx
  const [selected, setSelected] = useState<string>(OVERVIEW);
```

`view`에 `columns: vehicleColumns(data.operation, data.plays),` 추가. 렌더 부분:

```tsx
  const play = view.byId.get(selected);
  return (
    <div className="editor">
      <PlaySidebar groups={view.groups} selected={play ? play.id : OVERVIEW} source={data.source} showOverview onSelect={setSelected} />
      <main className="editor-main">
        {play ? (
          <PlayWorkflow play={play} usage={view.usage[play.id] ?? []} playName={playName} onOpen={setSelected} />
        ) : (
          <OperationOverview op={data.operation} columns={view.columns} playName={playName} onOpen={setSelected} />
        )}
      </main>
    </div>
  );
```

- [ ] **Step 3: Append to `index.css`**

```css
.switches { margin-bottom: 12px; } .switch { margin-right: 6px; padding: 2px 8px; border-radius: 6px; background: #3a2a14; }
.columns { display: flex; gap: 12px; align-items: flex-start; }
.column { width: 240px; flex: none; }
.column-head { font-weight: 700; margin-bottom: 6px; } .column-head small { font-weight: 400; opacity: 0.7; }
.via { margin: 6px 0; font-size: 12px; opacity: 0.75; }
.play-title { display: block; margin: 4px 0; font-weight: 700; }
```

- [ ] **Step 4: Test, build, look**

Run: `npm test && npm run build`, 그리고 dev 서버로 `#editor` 확인: 첫 화면이 "작전 개요", 열 5개(d1 순찰 A → '근접 확인' 선택 시 → 표적 감시 / d2 대기 → 순찰 B / d3 "예비: d1 대신" / usv 대기 → 근접 확인 / ugv 대기 → 상륙 지점 감시), 위 띠 "[전 기체 귀환]", 플레이 이름을 누르면 플레이 화면.

- [ ] **Step 5: Commit**

```bash
git add modules/cop-ui/src/features/editor modules/cop-ui/src/index.css
git commit -m "Part3-10: operation overview with one column per vehicle (start play, then plays its choices lead to)"
```

---

### Task 8: SPEC·BUILT_HERE 기록, ship, 완료 기록

**Files:**
- Modify: `modules/cop-ui/SPEC.md` (표 끝에 행 추가), `demo/BUILT_HERE.md` (표 끝에 행 추가)

- [ ] **Step 1: SPEC.md 행 추가**

```
| UI-06 | describeAction·describeCondition | Action / Condition | string | 행동·조건 한국어 한 줄, 라벨 표 Record로 빠짐 없음 | 리드 | 완료 |
| UI-07 | groupPlays | Play[] | PlayGroup[] | 드론·수상정·지상·공통 묶음, 영역 둘 이상·없음은 공통 | 리드 | 완료 |
| UI-08 | vehicleColumns | Operation, Play[] | Column[] | 기체별 시작 플레이 + 선택지로 이어지는 플레이, 순환 종료, 없는 플레이 null | 리드 | 완료 |
| UI-09 | playUsage | Operation, Play[] | Record<playId, Usage[]> | 작전 시작·선택지·전체 전환으로 쓰는 기체 | 리드 | 완료 |
| UI-10 | loadEditorData | fetch | EditorData | /operation·/plays 실패 시 예시 시나리오 + source=example(통합 2 전 제거) | 리드 | 완료 |
| UI-11 | EditorScreen | — | 편집기 화면 | 예시 작전이 왼쪽 바·작전 개요·플레이 카드로 그려짐(Part3-10) | 리드 | 완료 |
```

(Task 7을 건너뛰었으면 UI-11 완료 기준에서 "작전 개요·"를 빼고 `task.py note Part3-10 "작전 개요(Task 7) 남음"`.)

- [ ] **Step 2: BUILT_HERE.md 행 추가** (시각은 실제 KST)

```
| 10/10 HH:MM | cop-ui | 편집기 탭: 플레이 목록(영역별), 플레이 하나의 읽기 전용 step 카드, 작전 개요(기체별 열) (Part3-10) | kth9245 |
```

- [ ] **Step 3: Commit and ship**

```bash
git add modules/cop-ui/SPEC.md demo/BUILT_HERE.md
git commit -m "Part3-10: SPEC rows UI-06..UI-11 and BUILT_HERE entry"
scripts/ship.sh
```

Expected: rebase → cop-ui 테스트 → smoke → main push 성공

- [ ] **Step 4: Record done**

Run: `uv run python scripts/task.py done Part3-10`
