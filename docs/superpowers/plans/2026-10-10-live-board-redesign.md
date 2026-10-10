# 상황판 개편 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 상황판을 결정 대기열(한 장 펼침)·아군/적 목록·배마다 탐지 상태·표적 지목으로 다시 짜서, 1366×768에서 지금 할 일과 상황이 한눈에 보이게 한다.

**Architecture:** 화면 계산은 `modules/cop-ui/src/features/board/`의 순수 함수(액션 1개 = 파일 1개 = vitest 1개)로 Frame에서 뽑고, `boardView`가 한 번에 묶어 부품(`SituationBar`·`RosterPanel`·`DecisionQueue`·`MapView`)에 넘긴다. 카드 보내기·잠금·실행 막대 요청 로직은 지금 것(`frameCards`·`pruneSent`·`postDecision`·`RunBar`)을 그대로 쓴다. 계약 칸 5개(기본값 있음)와 gateway 두 곳을 먼저 넣고, sensing·runtime 세 곳은 담당자 몫으로 마지막에 둔다. 스펙 7절은 효과가 큰 순서(오른쪽 열 먼저)지만, 화면 함수가 새 TS 칸을 타입으로 쓰므로 기본값만 더하는 계약 커밋(10분 안쪽)을 맨 앞에 둔다. 화면에 보이는 순서는 그대로 오른쪽 열 → 지도 → 지목.

**Tech Stack:** React 19 + TypeScript + Vite + MapLibre GL 6 + vitest (cop-ui), Python 3 + pydantic + pytest (contracts·gateway·sensing·runtime), FastAPI(gateway).

**Spec:** `docs/superpowers/specs/2026-10-10-live-board-redesign-design.md` (결정 0047·0048·0049)

## Global Constraints

- 작업 폴더: worktree `.claude/worktrees/Part1-32`, 할 일 번호 Part1-32. 메인 폴더에서 파일을 고치지 않는다.
- TDD: 모든 코드 변경은 실패 테스트 먼저, 실패 확인, 구현, 통과(결정 0014). 화면 부품(.tsx)은 테스트 생략 가능.
- cop-ui 로직: `src/features/<기능>/` 아래 함수 1개 = 파일 1개 + `*.test.ts`. 데이터 타입은 `src/contracts.gen.ts`만(직접 수정 금지, `scripts/gen_contracts.py`로 생성).
- 색·글꼴은 `src/theme.css` 토큰만(`var(--text)` 등), 새 CSS에 hex 금지. 기능 CSS(`board.css`)는 배치만, 색·글꼴은 `theme.css`의 "Live board (Part1-32)" 구역.
- 지도에 글자 레이어(symbol) 금지(오프라인, glyphs 없음). 이름표는 HTML Marker.
- 색의 뜻: 흰색 = 당신 차례(결정), 노랑·주황·빨강 = 위험도 0.40 미만·이상·0.70 이상(빨강은 타격·차단에도), 하늘 = 아군, 초록 = 시스템 상태·선택.
- 글자: 판단에 쓰는 글자 13px 이상, 보조 최소 11px(상표 부제·출처 표기 제외).
- 1366×768에서 스크롤 없이: 머리, 왼쪽 236px, 오른쪽 384px.
- cop-ui SPEC 행은 손으로 추가(`modules/cop-ui/SPEC.md`, cop-ui는 guard 대상 아님). Python 모듈 SPEC 행은 기존 행 수정.
- 액션 하나(또는 묶음) 끝날 때마다 `scripts/ship.sh`(rebase → 바뀐 모듈 테스트 → smoke → main push). 실패 테스트가 있으면 ship하지 않는다.
- cop-ui 테스트: `cd modules/cop-ui && npx vitest run src/features/board/<파일>.test.ts`, 전체 `npm test`, 타입 `npx tsc -b`. Python: `uv run pytest modules/<m> -n 0 -k <이름>`.
- 화면 점검: `scripts/dev.sh`가 돌고 있을 때 `scripts/qa.sh scripts/qa/live.json`(서버 실행 상태를 처음으로 돌림).

## Review Focus

- 게이트웨이가 아직 `last_seen_pos`를 안 보내는 동안(sensing 변경 전) 놓친 배: 실제 위치에 놓침으로 그려지고 화면이 깨지지 않아야 한다 → Task 3 `trackState` "lost without last_seen_pos" 테스트.
- `/plays`·`/vehicles`·`/watch_points` 읽기가 실패해도(게이트웨이 늦게 뜸) 상황판이 그려져야 한다(종류 칸 빈칸, 지목 메뉴 "플레이 없음") → Task 5 `fetchBoardData` 실패 테스트, Task 6 `boardView` 빈 데이터 테스트.
- 열린 카드가 하나도 없을 때 카메라 점이 0개 → fitBounds를 부르지 않는다 → Task 5 `cameraPoints` 빈 테스트와 Task 8 MapView의 `pts.length` 검사.
- 처리된 카드가 대기열에서 빠지면 펼친 항목 키가 사라짐 → 첫 항목을 펼친다(`DecisionQueue`의 `?? queue.action[0]`), 시간이 뒤로 가면(처음으로) 보낸 기록을 잊는다(`pruneSent` 그대로).
- 기체를 고른 채 표적 마커가 아닌 기체 마커를 누르면 다른 기체로 선택이 바뀐다(지목 메뉴 닫힘) → Task 8 `useDirectControl` 동작, 화면 점검 L15.

---

## 파일 구조

| 파일 | 할 일 |
|---|---|
| `contracts/models/events.py`, `contracts/models/api.py` | Target 칸 3개, SwitchIn 칸 2개, Injection 칸 1개 |
| `modules/gateway/live.py`, `modules/gateway/app.py` | 전환 요청이 표적·바로 승인을 싣기, `GET /watch_points` |
| `modules/cop-ui/src/features/board/boardFixtures.ts` | 테스트용 Frame·카드 만들기(테스트만 씀) |
| `.../board/trackState.ts` (UI-54) | 배 하나의 탐지 상태 |
| `.../board/targetStage.ts` (UI-55) | 배 하나의 단계 |
| `.../board/situationCounts.ts` (UI-56) | 머리 개수 |
| `.../board/decisionQueue.ts` (UI-57) | 대기열·알림·지난 기록 |
| `.../board/choiceGroups.ts` (UI-58) | 정해진 선택지·드론 요청 묶음 |
| `.../board/vehicleRows.ts` (UI-59) | 아군 목록 줄 |
| `.../board/targetPlays.ts` (UI-60) | 지목 메뉴 플레이 |
| `.../board/cameraPoints.ts` (UI-61) | 지도가 볼 점 |
| `.../board/postPoint.ts` (UI-62) | 지목 요청 보내기 |
| `.../board/fetchBoardData.ts` (UI-63) | /plays·/vehicles·/watch_points 읽기 |
| `.../board/boardView.ts` (UI-64) | 위 계산을 한 번에 |
| `.../board/linkLines.ts` (UI-65) | 지도 선 GeoJSON |
| `.../board/watchCircles.ts` (UI-66) | 기준점 원 GeoJSON |
| `.../board/useBoardData.ts` | 게이트웨이가 답하면 한 번 읽는 hook |
| `.../board/SituationBar.tsx`, `LoadBar.tsx`, `RosterPanel.tsx`, `DecisionQueue.tsx`, `QueueCard.tsx`, `PointMenu.tsx`, `board.css` | 화면 부품(UI-67~70) |
| `modules/cop-ui/src/features/cards/frameCards.ts` | 위험 이유를 항목 배열로도(`threat.parts`) |
| `modules/cop-ui/src/features/map/frameMarkers.ts`, `markers.ts`, `MapView.tsx`, `useDirectControl.ts` | 탐지 상태 마커, 선·원 레이어, 카메라, 지목 |
| `modules/cop-ui/src/Screen.tsx`, `App.tsx`, `index.css`, `theme.css` | 3열 배치, 머리 자리, 색·글꼴 |
| `scripts/qa/live.json` | 새 화면에 맞춘 점검 |
| `modules/sensing/actions/observe_targets.py`, `modules/runtime/actions/fleet_choices.py`, `modules/runtime/actions/apply_injection.py` | 담당자 몫(Task 9) |

---

### Task 1: 계약 칸과 gateway(표적·바로 승인·기준점)

**Files:**
- Modify: `contracts/models/events.py` (Target, Injection)
- Modify: `contracts/models/api.py` (SwitchIn)
- Modify: `modules/gateway/live.py:150-160` (`request_switch`)
- Modify: `modules/gateway/app.py:134-137` (`/enemies` 옆에 `/watch_points`)
- Modify: `contracts/API.md` (표적 칸, POST /injections, GET /watch_points)
- Generate: `modules/cop-ui/src/contracts.gen.ts`, `contracts/schema/*`, `contracts/examples/*` (스크립트)
- Test: `modules/gateway/tests/test_live.py`, `modules/gateway/tests/test_app.py`

**Interfaces:**
- Produces: `Target.last_seen_pos: GeoPoint | None = None`, `Target.last_seen_vel_east_mps: float = 0`, `Target.last_seen_vel_north_mps: float = 0`; `SwitchIn.target_by_vehicle: dict[str, str] = {}`, `SwitchIn.approve: bool = False`; `Injection.target_by_vehicle: dict[str, str] = {}`; `GET /watch_points -> WatchPoint[]`. TS: `Target.last_seen_pos?: GeoPoint | null` 등.

- [ ] **Step 1: 실패 테스트 — 바로 승인 지목 요청**

`modules/gateway/tests/test_live.py`의 `test_switch_button_uses_the_operation_switch` 아래에 추가:

```python
def test_pointing_request_is_approved_at_once_and_carries_the_target():
    # decisions 0048, 0049: point d2 at boat1 with a play; the press is the approval, so no pending card
    live, eng = make()
    inj = live.request_switch(
        SwitchIn(play_by_vehicle={"d2": "watch"}, target_by_vehicle={"d2": "boat1"}, approve=True)
    )
    assert (inj.status, inj.target_by_vehicle, inj.label) == ("approved", {"d2": "boat1"}, "표적 감시: d2 → boat1")
    live.jump(400)
    assert [(i.id, i.status) for i in eng.seen[1].injections] == [(inj.id, "approved")]
```

`modules/gateway/tests/test_app.py`의 `test_enemies_come_from_the_scenario` 아래에 추가:

```python
def test_watch_points_come_from_the_scenario():
    # decision 0047: the live board tells approaching from fleeing by the expected landing point
    client, _ = fake_app()
    got = client.get("/watch_points").json()
    assert [(w["id"], w["radius_m"]) for w in got] == [("landing", 2000.0)]
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest modules/gateway -n 0 -k "pointing_request or watch_points"`
Expected: FAIL (`SwitchIn` has no field `target_by_vehicle` / 404)

- [ ] **Step 3: 계약 칸 추가**

`contracts/models/events.py` `Target`의 `threat_accum` 다음 줄에:

```python
    last_seen_pos: GeoPoint | None = None  # sensing: where a live vehicle last saw it (decision 0047)
    last_seen_vel_east_mps: float = 0  # its velocity at that moment, for approaching / fleeing
    last_seen_vel_north_mps: float = 0
```

`Injection`의 `switch_id` 다음 줄에:

```python
    target_by_vehicle: dict[str, str] = {}  # vehicle id -> target it works (pointing, decision 0048)
```

`contracts/models/api.py` `SwitchIn`을:

```python
class SwitchIn(BaseModel):  # POST /injections: a switch button id, or vehicles -> plays
    switch_id: str | None = None
    play_by_vehicle: dict[str, str] = {}
    target_by_vehicle: dict[str, str] = {}  # pointing at a target on the map (decision 0048)
    approve: bool = False  # the press is the approval: recorded approved, no pending card (decision 0049)
```

(`GeoPoint`가 events.py에 import되어 있지 않으면 `from .world import GeoPoint`처럼 같은 파일의 기존 import 줄에 더한다.)

- [ ] **Step 4: gateway 구현**

`modules/gateway/live.py` `request_switch` 끝 두 줄을:

```python
            label = ", ".join(
                f"{names[p]}: {v}" + (f" → {body.target_by_vehicle[v]}" if v in body.target_by_vehicle else "")
                for v, p in pbv.items()
            )
        inj = Injection(id=id_, t_ms=t, label=label, play_by_vehicle=pbv, switch_id=body.switch_id,
                        target_by_vehicle=body.target_by_vehicle,
                        status="approved" if body.approve else "pending")  # fmt: skip
        return self._queue(inj, self.inputs.injections)
```

(위 `label = ", ".join(...)` 한 줄을 이 블록으로 바꾼다. `switch_id` 분기는 그대로.)

`modules/gateway/app.py` `/enemies` 다음에:

```python
    @app.get("/watch_points")
    async def watch_points():
        return live.scenario.watch_points
```

- [ ] **Step 5: 생성 파일 다시 만들기, 통과 확인**

Run: `uv run python scripts/gen_contracts.py && uv run python scripts/gen_examples.py && uv run pytest modules/gateway contracts -n auto -q`
Expected: PASS. `git status`에 `contracts.gen.ts`·schema·examples 변경이 보인다.

- [ ] **Step 6: API.md**

`contracts/API.md`에서 Target 칸 설명 표(또는 목록)에 세 칸, POST /injections 설명에 `target_by_vehicle`(지목 표적)과 `approve`(참이면 approved로 기록, 대기 카드 없음, 운용자 조작 1), 5절 GET 목록에 `GET /watch_points -> WatchPoint[]`(시나리오 기준점)을 한 줄씩 적는다.

- [ ] **Step 7: Commit, ship**

```bash
git add contracts modules/gateway modules/cop-ui/src/contracts.gen.ts
git commit -m "Part1-32: Target last seen position and velocity, switch requests carry targets and approve-on-press, GET /watch_points (decisions 0047-0049)"
scripts/ship.sh
```

---

### Task 2: 결정 대기열과 선택지 묶음 (UI-57, UI-58)

**Files:**
- Create: `modules/cop-ui/src/features/board/boardFixtures.ts`
- Create: `modules/cop-ui/src/features/board/decisionQueue.ts`, `decisionQueue.test.ts`
- Create: `modules/cop-ui/src/features/board/choiceGroups.ts`, `choiceGroups.test.ts`
- Modify: `modules/cop-ui/src/features/cards/frameCards.ts` (`CardThreat.parts`), `frameCards.test.ts`
- Modify: `modules/cop-ui/SPEC.md`

**Interfaces:**
- Consumes: `Card`, `CardChoice`, `CardThreat` from `features/cards/frameCards.ts`.
- Produces: `decisionQueue(cards: Card[], tMs: number): Queue` with `QueueItem { key: string; cards: Card[] }`, `Queue { action: QueueItem[]; alerts: Card[]; history: Card[] }`; `choiceGroups(choices: CardChoice[]): { planned: CardChoice[]; requests: ChoiceRequest[] }` with `ChoiceRequest { what: string; options: { vehicle: string; choiceId: string }[] }`; `CardThreat.parts: string[]`; fixtures `T0`, `at`, `mkTarget`, `mkVehicle`, `mkReport`, `mkFrame`, `mkCard`.

- [ ] **Step 1: 테스트 도우미**

`modules/cop-ui/src/features/board/boardFixtures.ts`:

```ts
import type { Frame, Report, Target, VehicleState } from "../../contracts.gen";
import type { Card } from "../cards/frameCards";

// Small Frames and cards for the board tests (Part1-32). Only tests import this file.
export const T0 = 1_791_634_000_000;
export const at = (lat: number, lon: number) => ({ lat, lon, alt_m: 0 });

export function mkTarget(p: Partial<Target> & { id: string }): Target {
  return { kind: "boat", pos: at(37.99, 124.72), vel_east_mps: 0, vel_north_mps: 0, first_seen_ms: 0,
    last_seen_ms: 0, seen_by: [], threat: 0, threat_reasons: [], ...p };
}
export function mkVehicle(p: Partial<VehicleState> & { id: string }): VehicleState {
  return { t_ms: T0, pos: at(37.95, 124.7), heading_deg: 0, battery_pct: 100, status: "ready", ...p };
}
export function mkReport(p: Partial<Report> & { id: string }): Report {
  return { t_ms: T0, kind: "target_detected", text: "보고", choices: [], ...p };
}
export function mkFrame(p: Partial<Frame> = {}): Frame {
  return { t_ms: T0, run: { status: "paused", speed: 1 }, vehicles: [], targets: [], reports: [], assignments: [],
    blocks: [], injections: [], metrics: {}, ...p };
}
export function mkCard(p: Partial<Card> & { id: string }): Card {
  return { source: "report", kind: "target_detected", vehicle: null, t_ms: T0, time: "21:00:00", text: "",
    choices: [], done: null, ...p };
}
```

- [ ] **Step 2: 실패 테스트 — decisionQueue**

`modules/cop-ui/src/features/board/decisionQueue.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { mkCard, T0 } from "./boardFixtures";
import { decisionQueue } from "./decisionQueue";

const ask = { id: "c", label: "근접 확인", preview: "" };
const ids = (q: ReturnType<typeof decisionQueue>) => q.action.map((i) => i.cards.map((c) => c.id).join("+"));

describe("decisionQueue", () => {
  it("puts open reports with choices and pending switches in the queue, answered ones in history", () => {
    const q = decisionQueue([
      mkCard({ id: "open", choices: [ask] }),
      mkCard({ id: "answered", done: "처리됨 21:00:05" }),
      mkCard({ id: "inj-1", source: "injection", kind: "injection" }),
      mkCard({ id: "inj-2", source: "injection", kind: "injection", done: "승인됨" }),
    ], T0);
    expect(ids(q)).toEqual(["inj-1", "open"]);
    expect(q.history.map((c) => c.id)).toEqual(["answered", "inj-2"]);
  });

  it("asks about a block with an alternative for 30 s, then shows it as an alert for 2 min, then history", () => {
    const block = mkCard({ id: "cmd-1", source: "block", kind: "outside_zone", alternative: { lat: 38, lon: 124.6 } });
    expect(ids(decisionQueue([block], T0 + 29_000))).toEqual(["cmd-1"]);
    expect(decisionQueue([block], T0 + 31_000).alerts.map((c) => c.id)).toEqual(["cmd-1"]);
    expect(decisionQueue([block], T0 + 121_000).history.map((c) => c.id)).toEqual(["cmd-1"]);
  });

  it("orders strike approval, block, switch, then risk, newest first on a tie", () => {
    const risk = (s: number) => ({ score: s, rf: false, line: "", parts: [] });
    const q = decisionQueue([
      mkCard({ id: "low", choices: [ask], threat: risk(0.42) }),
      mkCard({ id: "high", choices: [ask], threat: risk(0.75) }),
      mkCard({ id: "inj", source: "injection", kind: "injection" }),
      mkCard({ id: "blk", source: "block", kind: "battery_insufficient", alternative: { lat: 37.9, lon: 124.7 } }),
      mkCard({ id: "strike", choices: [ask], text: "타격 승인 요청 · usv 센서 탐지", threat: risk(0.1) }),
      mkCard({ id: "high-new", choices: [ask], threat: risk(0.75), t_ms: T0 + 1 }),
    ], T0 + 1);
    expect(ids(q)).toEqual(["strike", "blk", "inj", "high-new", "high", "low"]);
  });

  it("merges the target picks one switch opened into one item, one decision per vehicle", () => {
    const pick = (id: string, vehicle: string) => mkCard({ id, kind: "target_select", vehicle, choices: [ask] });
    const q = decisionQueue([pick("p-d2", "d2"), pick("p-usv", "usv")], T0);
    expect(ids(q)).toEqual(["p-d2+p-usv"]);
    expect(decisionQueue([pick("p-d2", "d2")], T0).action[0].key).toBe("p-d2");
  });

  it("keeps a fresh strike result as an alert and older events in history, newest first", () => {
    const q = decisionQueue([
      mkCard({ id: "old", kind: "target_neutralized", t_ms: T0 - 200_000 }),
      mkCard({ id: "win", kind: "target_neutralized", t_ms: T0 - 5_000 }),
      mkCard({ id: "older", done: "처리됨", t_ms: T0 - 300_000 }),
    ], T0);
    expect(q.alerts.map((c) => c.id)).toEqual(["win"]);
    expect(q.history.map((c) => c.id)).toEqual(["old", "older"]);
  });
});
```

- [ ] **Step 3: 실패 확인**

Run: `cd modules/cop-ui && npx vitest run src/features/board/decisionQueue.test.ts`
Expected: FAIL ("Failed to resolve import ./decisionQueue")

- [ ] **Step 4: 구현 — decisionQueue**

`modules/cop-ui/src/features/board/decisionQueue.ts`:

```ts
import type { Card } from "../cards/frameCards";

export interface QueueItem { key: string; cards: Card[] }
export interface Queue { action: QueueItem[]; alerts: Card[]; history: Card[] }

const BLOCK_ASKS_MS = 30_000;
const ALERT_MS = 120_000;
const ALERT_KINDS: Card["kind"][] = ["target_neutralized", "vehicle_gap", "vehicle_lost", "battery_low"];

const waits = (c: Card, tMs: number) =>
  c.source === "block" ? !!c.alternative && tMs - c.t_ms < BLOCK_ASKS_MS
    : !c.done && (c.choices.length > 0 || c.source === "injection");

function rank(item: QueueItem): number {
  const c = item.cards[0];
  if (c.source === "report" && c.text.startsWith("타격 승인 요청")) return 3;
  if (c.source === "block") return 2;
  if (c.source === "injection") return 1.5;
  if (item.cards.length > 1) return 0.55; // target picks a switch opened, between watched and threatening boats
  return c.threat?.score ?? 0;
}

// Side column (Part1-32): what waits for the operator now, most pressing first (strike approval, block with an
// alternative, switch, then risk), with the target picks one switch opened merged into one item; fresh events
// (strike result, gap, battery, block) for 2 minutes; everything else newest first.
export function decisionQueue(cards: Card[], tMs: number): Queue {
  const open = cards.filter((c) => waits(c, tMs));
  const picks = open.filter((c) => c.kind === "target_select");
  const merge = picks.length > 1;
  const action: QueueItem[] = open.filter((c) => !(merge && picks.includes(c))).map((c) => ({ key: c.id, cards: [c] }));
  if (merge) action.push({ key: picks.map((c) => c.id).join("+"), cards: picks });
  const newest = (a: Card, b: Card) => b.t_ms - a.t_ms;
  action.sort((a, b) => rank(b) - rank(a) || newest(a.cards[0], b.cards[0]));
  const rest = cards.filter((c) => !open.includes(c)).sort(newest);
  const fresh = (c: Card) => (ALERT_KINDS.includes(c.kind) || c.source === "block") && tMs - c.t_ms < ALERT_MS;
  return { action, alerts: rest.filter(fresh), history: rest.filter((c) => !fresh(c)) };
}
```

- [ ] **Step 5: 통과 확인**

Run: `cd modules/cop-ui && npx vitest run src/features/board/decisionQueue.test.ts`
Expected: PASS (5)

- [ ] **Step 6: 실패 테스트 — choiceGroups (실제 엔진 boat1 카드의 선택지)**

`modules/cop-ui/src/features/board/choiceGroups.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { choiceGroups } from "./choiceGroups";

// boat1's card in the demo (decision 0046), after decision 0048 keeps watch-together to d1 only
const BOAT1 = [
  { id: "approach", label: "근접 확인", preview: "d1→watch · usv→approach · ugv→landing" },
  { id: "take_d3", label: "d3 → 발생 지역 순찰(해안 순찰 A)", preview: "d3→patrol_a" },
  { id: "take_d4", label: "d4 → 발생 지역 순찰(해안 순찰 A)", preview: "d4→patrol_a" },
  { id: "join_d3_d1", label: "d3 → d1와 함께 감시(boat1)", preview: "d3→watch" },
  { id: "join_d4_d1", label: "d4 → d1와 함께 감시(boat1)", preview: "d4→watch" },
];

describe("choiceGroups", () => {
  it("keeps the card's planned choices first and groups drone requests by what they ask", () => {
    const g = choiceGroups(BOAT1);
    expect(g.planned.map((c) => c.id)).toEqual(["approach"]);
    expect(g.requests).toEqual([
      { what: "해안 순찰 A 이어받기", options: [{ vehicle: "d3", choiceId: "take_d3" }, { vehicle: "d4", choiceId: "take_d4" }] },
      { what: "d1와 함께 boat1 감시", options: [{ vehicle: "d3", choiceId: "join_d3_d1" }, { vehicle: "d4", choiceId: "join_d4_d1" }] },
    ]);
  });

  it("treats choices that move several vehicles or none as planned", () => {
    const g = choiceGroups([
      { id: "keep", label: "감시 유지", preview: "" },
      { id: "both", label: "함께 타격", preview: "d2→strike · usv→strike" },
      { id: "one", label: "이 기체로 타격", preview: "usv→strike" },
    ]);
    expect(g.planned.map((c) => c.id)).toEqual(["keep", "both", "one"]);
    expect(g.requests).toEqual([]);
  });
});
```

- [ ] **Step 7: 실패 확인**

Run: `cd modules/cop-ui && npx vitest run src/features/board/choiceGroups.test.ts`
Expected: FAIL (import)

- [ ] **Step 8: 구현 — choiceGroups**

`modules/cop-ui/src/features/board/choiceGroups.ts`:

```ts
import type { CardChoice } from "../cards/frameCards";

export interface ChoiceRequest { what: string; options: { vehicle: string; choiceId: string }[] }

function what(rest: string): string {
  const take = rest.match(/^발생 지역 순찰\((.+)\)$/);
  if (take) return `${take[1]} 이어받기`;
  const join = rest.match(/^(\S+)와 함께 감시\((.+)\)$/);
  return join ? `${join[1]}와 함께 ${join[2]} 감시` : rest;
}

// A report card's choices (decision 0046): the card's planned choices first in the engine's order, then the
// requests to standby drones ("d3 → ...", moving exactly that drone) grouped by what they ask, one button each.
export function choiceGroups(choices: CardChoice[]): { planned: CardChoice[]; requests: ChoiceRequest[] } {
  const planned: CardChoice[] = [];
  const requests: ChoiceRequest[] = [];
  for (const ch of choices) {
    const m = ch.label.match(/^(\S+) → (.+)$/);
    if (!m || !new RegExp(`^${m[1]}→\\S+$`).test(ch.preview)) {
      planned.push(ch);
      continue;
    }
    const w = what(m[2]);
    let g = requests.find((r) => r.what === w);
    if (!g) requests.push((g = { what: w, options: [] }));
    g.options.push({ vehicle: m[1], choiceId: ch.id });
  }
  return { planned, requests };
}
```

- [ ] **Step 9: 통과 확인**

Run: `cd modules/cop-ui && npx vitest run src/features/board/choiceGroups.test.ts`
Expected: PASS (2)

- [ ] **Step 10: 실패 테스트 — 위험 이유 항목 배열**

`modules/cop-ui/src/features/cards/frameCards.test.ts`의 위험도 테스트(“threat” 들어간 it) 아래에 추가:

```ts
  it("keeps each risk reason as its own item for the board (Part1-32)", () => {
    const f = s1 as Frame;
    const t = { ...f.targets[0], threat: 75, threat_reasons: ["kind_boat", "rf_emission"] };
    const [c] = frameCards({ ...f, targets: [t] });
    expect(c.threat?.parts).toEqual(["관측 위험 0.75", "스캔 판별: 보트", "RF 방출 감지 +0.30"]);
    expect(c.threat?.line).toBe(c.threat?.parts.join(" · "));
  });
```

Run: `cd modules/cop-ui && npx vitest run src/features/cards/frameCards.test.ts` → FAIL (`parts` undefined)

- [ ] **Step 11: 구현**

`modules/cop-ui/src/features/cards/frameCards.ts`: `export interface CardThreat { score: number; rf: boolean; line: string; parts: string[] }` 로 바꾸고, `threatOf`의 마지막 줄을 `return { score, rf: reasons.includes("rf_emission"), line: parts.join(" · "), parts };` 로.

Run: `cd modules/cop-ui && npx vitest run src/features/cards src/features/board` → PASS

- [ ] **Step 12: SPEC 행, commit, ship**

`modules/cop-ui/SPEC.md` 끝에:

```
| UI-57 | decisionQueue | Card[], t_ms | {action, alerts, history} | 선택지 있는 미처리 보고·대기 전환·30초 안의 대안 있는 차단이 대기열, 같은 전환의 표적 선택 여러 장은 한 항목, 순서 타격 허락 > 차단 > 전환 > 위험도(같으면 최신), 2분 안의 무력화·공백·배터리·차단은 알림, 나머지 최신 위(Part1-32) | 리드 | 완료 |
| UI-58 | choiceGroups | CardChoice[] | {planned, requests} | 정해진 선택지 먼저 엔진 순서(결정 0046), "X → 무엇" 한 기체 선택지는 무엇별 묶음(발생 지역 순찰 → "… 이어받기", 함께 감시 → "Y와 함께 T 감시") | 리드 | 완료 |
```

```bash
git add modules/cop-ui
git commit -m "Part1-32: decision queue (one switch's target picks merged, strike approval first) and choice groups (planned first, drone requests grouped); risk reasons as items"
scripts/ship.sh
```

---

### Task 3: 탐지 상태와 단계 (UI-54, UI-55, UI-56)

**Files:**
- Create: `modules/cop-ui/src/features/board/trackState.ts`, `trackState.test.ts`
- Create: `modules/cop-ui/src/features/board/targetStage.ts`, `targetStage.test.ts`
- Create: `modules/cop-ui/src/features/board/situationCounts.ts`, `situationCounts.test.ts`
- Modify: `modules/cop-ui/SPEC.md`

**Interfaces:**
- Consumes: Task 1 TS 칸(`Target.last_seen_pos`, `last_seen_vel_*_mps`), Task 2 `Queue`, fixtures.
- Produces: `trackState(t: Target, tMs: number, watch: GeoPoint | null): Track` with `Track { k: TrackKind; pos: GeoPoint; est?: GeoPoint; agoMs?: number; dir?: LostDir; speed?: number }`, `TrackKind = "seen"|"rf"|"lost"|"never"|"gone"`, `LostDir = "still"|"approach"|"away"`; `targetStage(f: Frame, t: Target, track: Track): Stage` with `Stage { key: StageKey; label: string; detail: string; away: boolean }`, `StageKey = "gone"|"strike"|"ask"|"lost"|"rf"|"never"|"track"|"found"`; `situationCounts(stages: Stage[], queue: Queue): Situation` with `Situation { targets: number; stages: { key: StageKey; label: string; n: number }[]; decisions: number }`.

- [ ] **Step 1: 실패 테스트 — trackState**

`modules/cop-ui/src/features/board/trackState.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { at, mkTarget, T0 } from "./boardFixtures";
import { trackState } from "./trackState";

const LANDING = at(37.978, 124.7);
const lostAt = (p: object) => mkTarget({ id: "fast1", first_seen_ms: T0 - 60_000, last_seen_ms: T0 - 20_000,
  pos: at(37.99, 124.76), last_seen_pos: at(37.987, 124.745), ...p });

describe("trackState", () => {
  it("says seen, RF only, never detected or struck from what our side knows", () => {
    expect(trackState(mkTarget({ id: "a", seen_by: ["d1"], first_seen_ms: T0 }), T0, LANDING).k).toBe("seen");
    expect(trackState(mkTarget({ id: "b", rf_detected: true }), T0, LANDING).k).toBe("rf");
    expect(trackState(mkTarget({ id: "c" }), T0, LANDING)).toEqual({ k: "never", pos: at(37.99, 124.72) });
    expect(trackState(mkTarget({ id: "d", neutralized_ms: T0, seen_by: ["usv"] }), T0, LANDING).k).toBe("gone");
  });

  it("draws a lost target where it was last seen, still when it was not moving", () => {
    expect(trackState(lostAt({}), T0, LANDING)).toEqual({ k: "lost", pos: at(37.987, 124.745), agoMs: 20_000, dir: "still", speed: 0 });
  });

  it("estimates where a moving lost target is now and whether it heads to the landing point", () => {
    const away = trackState(lostAt({ last_seen_vel_east_mps: 6.3 }), T0, LANDING); // landing is west
    expect([away.k, away.dir, away.agoMs]).toEqual(["lost", "away", 20_000]);
    expect(away.est!.lat).toBeCloseTo(37.987, 6);
    expect(away.est!.lon).toBeCloseTo(124.745 + (6.3 * 20) / (111_320 * Math.cos((37.987 * Math.PI) / 180)), 6);
    expect(trackState(lostAt({ last_seen_vel_east_mps: -6.3 }), T0, LANDING).dir).toBe("approach");
  });

  it("assumes a moving lost target approaches when there is no landing point", () => {
    expect(trackState(lostAt({ last_seen_vel_east_mps: 6.3 }), T0, null).dir).toBe("approach");
  });

  it("falls back to the true position while the gateway does not send the last seen spot yet", () => {
    expect(trackState(lostAt({ last_seen_pos: null }), T0, LANDING).pos).toEqual(at(37.99, 124.76));
  });
});
```

- [ ] **Step 2: 실패 확인**

Run: `cd modules/cop-ui && npx vitest run src/features/board/trackState.test.ts` → FAIL (import)

- [ ] **Step 3: 구현 — trackState**

`modules/cop-ui/src/features/board/trackState.ts`:

```ts
import type { GeoPoint, Target } from "../../contracts.gen";

export type TrackKind = "seen" | "rf" | "lost" | "never" | "gone";
export type LostDir = "still" | "approach" | "away";
export interface Track { k: TrackKind; pos: GeoPoint; est?: GeoPoint; agoMs?: number; dir?: LostDir; speed?: number }

const M_PER_DEG = 111_320;
const STILL_MPS = 0.3;

// What our side knows about a target (decision 0047): seen now, RF only, lost (drawn where it was last seen,
// moving on at the velocity it had then), never detected, or struck. A moving lost target heading toward the
// expected landing point is "approach", away from it "away"; with no landing point it is assumed to approach.
export function trackState(t: Target, tMs: number, watch: GeoPoint | null): Track {
  if (t.neutralized_ms != null) return { k: "gone", pos: t.pos };
  if ((t.seen_by ?? []).length > 0) return { k: "seen", pos: t.pos };
  if (t.rf_detected) return { k: "rf", pos: t.pos };
  if (!t.first_seen_ms) return { k: "never", pos: t.pos };
  const pos = t.last_seen_pos ?? t.pos;
  const ve = t.last_seen_vel_east_mps ?? 0;
  const vn = t.last_seen_vel_north_mps ?? 0;
  const speed = Math.hypot(ve, vn);
  const agoMs = tMs - t.last_seen_ms;
  if (speed < STILL_MPS) return { k: "lost", pos, agoMs, dir: "still", speed };
  const mLon = M_PER_DEG * Math.cos((pos.lat * Math.PI) / 180);
  const sec = agoMs / 1000;
  const est = { lat: pos.lat + (vn * sec) / M_PER_DEG, lon: pos.lon + (ve * sec) / mLon };
  const away = !!watch && ve * (watch.lon - pos.lon) * mLon + vn * (watch.lat - pos.lat) * M_PER_DEG <= 0;
  return { k: "lost", pos, est, agoMs, dir: away ? "away" : "approach", speed };
}
```

- [ ] **Step 4: 통과 확인**

Run: `cd modules/cop-ui && npx vitest run src/features/board/trackState.test.ts` → PASS (5)

- [ ] **Step 5: 실패 테스트 — targetStage**

`modules/cop-ui/src/features/board/targetStage.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import type { Frame, Target } from "../../contracts.gen";
import { at, mkFrame, mkReport, mkTarget, mkVehicle, T0 } from "./boardFixtures";
import { targetStage } from "./targetStage";
import { trackState } from "./trackState";

const LANDING = at(37.978, 124.7);
const stage = (f: Frame, t: Target) => targetStage(f, t, trackState(t, f.t_ms, LANDING));
const seen = mkTarget({ id: "boat1", seen_by: ["d1"], first_seen_ms: T0 - 1 });
const strikeCmd = { command: { id: "c", vehicle_id: "d2", kind: "strike" as const, params: {} }, checks: [], passed_ms: 0 };

describe("targetStage", () => {
  it("says struck, striking, then waiting for strike approval before anything else", () => {
    expect(stage(mkFrame(), { ...seen, neutralized_ms: T0 })).toMatchObject({ key: "gone", label: "무력화" });
    const striking = mkFrame({ vehicles: [mkVehicle({ id: "d2", status: "active", target_id: "boat1", active: strikeCmd })] });
    expect(stage(striking, seen)).toEqual({ key: "strike", label: "타격 중", detail: "d2", away: false });
    const asking = mkFrame({ reports: [mkReport({ id: "r", vehicle_id: "usv", target_id: "boat1", text: "타격 승인 요청 · usv",
      choices: [{ id: "x", label: "함께 타격" }] })] });
    expect(stage(asking, seen)).toEqual({ key: "ask", label: "허락 대기", detail: "usv 요청", away: false });
  });

  it("says lost with time and direction, red when it moves away", () => {
    const fast1 = mkTarget({ id: "fast1", first_seen_ms: T0 - 60_000, last_seen_ms: T0 - 20_000,
      last_seen_pos: at(37.987, 124.745), last_seen_vel_east_mps: 6.3 });
    expect(stage(mkFrame(), fast1)).toEqual({ key: "lost", label: "놓침", detail: "0:20 전 · 이탈(도주) 추정 6.3 m/s", away: true });
  });

  it("says RF only and never detected", () => {
    expect(stage(mkFrame(), mkTarget({ id: "b", rf_detected: true })).key).toBe("rf");
    expect(stage(mkFrame(), mkTarget({ id: "c" }))).toEqual({ key: "never", label: "미탐", detail: "센서에 안 잡힘", away: false });
  });

  it("says tracked only by vehicles on a mission, else found by who sees it", () => {
    const on = mkFrame({ vehicles: [mkVehicle({ id: "d1", status: "active", target_id: "boat1" })] });
    expect(stage(on, seen)).toEqual({ key: "track", label: "추적", detail: "d1", away: false });
    const home = mkFrame({ vehicles: [mkVehicle({ id: "d1", status: "maintenance", target_id: "boat1" })] });
    expect(stage(home, seen)).toEqual({ key: "found", label: "발견", detail: "d1 관측", away: false });
  });
});
```

- [ ] **Step 6: 실패 확인**

Run: `cd modules/cop-ui && npx vitest run src/features/board/targetStage.test.ts` → FAIL (import)

- [ ] **Step 7: 구현 — targetStage**

`modules/cop-ui/src/features/board/targetStage.ts`:

```ts
import type { Frame, Target } from "../../contracts.gen";
import { kstTime } from "../cards/kstTime";
import { mmss } from "../run/mmss";
import type { Track } from "./trackState";

export type StageKey = "gone" | "strike" | "ask" | "lost" | "rf" | "never" | "track" | "found";
export interface Stage { key: StageKey; label: string; detail: string; away: boolean }

const DIR_KO = { still: "정지", approach: "접근 추정", away: "이탈(도주) 추정" } as const;

// One target's stage (Part1-32). Targets move through these on their own (one can wait for strike approval while
// another is just found), so the screen counts them and never shows one order for the whole operation.
export function targetStage(f: Frame, t: Target, track: Track): Stage {
  const st = (key: StageKey, label: string, detail: string, away = false): Stage => ({ key, label, detail, away });
  if (track.k === "gone") return st("gone", "무력화", kstTime(t.neutralized_ms ?? f.t_ms));
  const on = f.vehicles.filter((v) => v.status === "active" && v.target_id === t.id);
  const strikers = on.filter((v) => v.active?.command.kind === "strike");
  if (strikers.length) return st("strike", "타격 중", strikers.map((v) => v.id).join("·"));
  const ask = f.reports.find((r) => r.target_id === t.id && !r.resolved_ms && (r.choices ?? []).length > 0
    && r.text.startsWith("타격 승인 요청"));
  if (ask) return st("ask", "허락 대기", `${ask.vehicle_id} 요청`);
  if (track.k === "lost") {
    const speed = (track.speed ?? 0) >= 0.3 ? ` ${(track.speed ?? 0).toFixed(1)} m/s` : "";
    return st("lost", "놓침", `${mmss(track.agoMs ?? 0)} 전 · ${DIR_KO[track.dir ?? "still"]}${speed}`, track.dir === "away");
  }
  if (track.k === "rf") return st("rf", "RF 탐지", "무선만 잡힘");
  if (track.k === "never") return st("never", "미탐", "센서에 안 잡힘");
  if (on.length) return st("track", "추적", on.map((v) => v.id).join("·"));
  return st("found", "발견", `${(t.seen_by ?? []).join("·")} 관측`);
}
```

Run: `cd modules/cop-ui && npx vitest run src/features/board/targetStage.test.ts` → PASS (4)

- [ ] **Step 8: 실패 테스트 — situationCounts**

`modules/cop-ui/src/features/board/situationCounts.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { mkCard } from "./boardFixtures";
import { situationCounts } from "./situationCounts";
import type { Stage } from "./targetStage";

const s = (key: Stage["key"]): Stage => ({ key, label: key, detail: "", away: false });

describe("situationCounts", () => {
  it("counts targets per stage, most urgent first, leaving out empty stages", () => {
    const got = situationCounts([s("found"), s("never"), s("ask"), s("found"), s("lost")], { action: [], alerts: [], history: [] });
    expect(got.targets).toBe(5);
    expect(got.stages).toEqual([
      { key: "ask", label: "허락 대기", n: 1 }, { key: "lost", label: "놓침", n: 1 },
      { key: "found", label: "발견", n: 2 }, { key: "never", label: "미탐", n: 1 },
    ]);
  });

  it("counts decisions, one per vehicle in a merged target pick", () => {
    const q = { action: [{ key: "a", cards: [mkCard({ id: "a" })] }, { key: "p", cards: [mkCard({ id: "p1" }), mkCard({ id: "p2" })] }],
      alerts: [], history: [] };
    expect(situationCounts([], q).decisions).toBe(3);
  });
});
```

Run: `cd modules/cop-ui && npx vitest run src/features/board/situationCounts.test.ts` → FAIL (import)

- [ ] **Step 9: 구현 — situationCounts**

`modules/cop-ui/src/features/board/situationCounts.ts`:

```ts
import type { Queue } from "./decisionQueue";
import type { Stage, StageKey } from "./targetStage";

export interface Situation { targets: number; stages: { key: StageKey; label: string; n: number }[]; decisions: number }

const URGENT: [StageKey, string][] = [["ask", "허락 대기"], ["strike", "타격 중"], ["lost", "놓침"], ["rf", "RF 탐지"],
  ["track", "추적"], ["found", "발견"], ["gone", "무력화"], ["never", "미탐"]];

// Header line (Part1-32): targets per stage, most urgent first (counts, not an order of events), and the
// decisions waiting. A merged target pick holds one decision per vehicle.
export function situationCounts(stages: Stage[], queue: Queue): Situation {
  return {
    targets: stages.length,
    stages: URGENT.map(([key, label]) => ({ key, label, n: stages.filter((x) => x.key === key).length })).filter((x) => x.n > 0),
    decisions: queue.action.reduce((n, item) => n + item.cards.length, 0),
  };
}
```

Run: `cd modules/cop-ui && npx vitest run src/features/board` → PASS

- [ ] **Step 10: SPEC 행, commit (ship은 Task 4와 함께)**

`modules/cop-ui/SPEC.md` 끝에:

```
| UI-54 | trackState | Target, t_ms, 기준점 | {k, pos, est?, agoMs?, dir?, speed?} | seen·rf·lost·never·gone, lost는 마지막으로 본 위치(없으면 실제 위치), 0.3 m/s 미만 정지, 기준점 쪽 접근·반대 이탈(기준점 없으면 접근), 추정 위치 = 마지막 위치 + 속도 × 지난 시간(결정 0047) | 리드 | 완료 |
| UI-55 | targetStage | Frame, Target, Track | {key, label, detail, away} | 무력화 > 타격 중 > 허락 대기 > 놓침(경과·방향·속도, 이탈이면 away) > RF 탐지 > 미탐 > 추적(임무 중 기체만) > 발견 | 리드 | 완료 |
| UI-56 | situationCounts | Stage[], Queue | {targets, stages, decisions} | 단계별 개수 급한 순, 0개 뺌, 결정 수는 합친 표적 선택의 기체 수만큼 | 리드 | 완료 |
```

```bash
git add modules/cop-ui
git commit -m "Part1-32: per-target detection state (lost at the last seen spot, approach/away), stage and header counts (decision 0047)"
```

---

### Task 4: 아군 목록 줄, 지목 플레이, 지목 요청 (UI-59, UI-60, UI-62)

**Files:**
- Create: `modules/cop-ui/src/features/board/vehicleRows.ts`, `vehicleRows.test.ts`
- Create: `modules/cop-ui/src/features/board/targetPlays.ts`, `targetPlays.test.ts`
- Create: `modules/cop-ui/src/features/board/postPoint.ts`, `postPoint.test.ts`
- Modify: `modules/cop-ui/SPEC.md`

**Interfaces:**
- Consumes: fixtures, `postJson` (`features/cards/postJson.ts`), Task 1 `SwitchIn` TS 칸.
- Produces: `vehicleRows(f: Frame, playNames: Record<string, string>, specs: VehicleSpec[]): VehicleRow[]` with `VehicleRow { id; status: VehicleStatus; doing: string; kind: string; target: string | null; striking: boolean; battery: number; low: boolean; waiting: boolean }`; `targetPlays(plays: Play[], domain: Domain): Play[]`; `postPoint(vehicle: string, play: string, target: string): Promise<Sent>`.

- [ ] **Step 1: 실패 테스트 — vehicleRows**

`modules/cop-ui/src/features/board/vehicleRows.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import type { VehicleSpec } from "../../contracts.gen";
import { at, mkFrame, mkReport, mkVehicle } from "./boardFixtures";
import { vehicleRows } from "./vehicleRows";

const spec = (id: string, kind: string): VehicleSpec =>
  ({ id, name: id, domain: "air", speed_mps: 15, endurance_min: 100, sensor_range_m: 800, home: at(37.95, 124.7), kind });
const NAMES = { patrol_a: "해안 순찰 A", strike: "표적 타격" };
const strikeCmd = { command: { id: "c", vehicle_id: "d2", kind: "strike" as const, params: {} }, checks: [], passed_ms: 0 };

describe("vehicleRows", () => {
  it("says what each vehicle does, its kind, battery and whether a card waits for it", () => {
    const f = mkFrame({
      vehicles: [mkVehicle({ id: "d1", status: "active", play_id: "patrol_a", target_id: "boat1", battery_pct: 82.6 }),
        mkVehicle({ id: "d3" })],
      reports: [mkReport({ id: "r", vehicle_id: "d1", choices: [{ id: "c", label: "근접 확인" }] })],
    });
    expect(vehicleRows(f, NAMES, [spec("d1", "recon_drone")])).toEqual([
      { id: "d1", status: "active", doing: "해안 순찰 A", kind: "정찰 드론", target: "boat1", striking: false, battery: 83, low: false, waiting: true },
      { id: "d3", status: "ready", doing: "대기", kind: "", target: null, striking: false, battery: 100, low: false, waiting: false },
    ]);
  });

  it("shows no target for a vehicle back at base, and marks a striking one and low battery", () => {
    const f = mkFrame({ vehicles: [
      mkVehicle({ id: "d1", status: "maintenance", play_id: "go_home", target_id: "boat1", battery_pct: 20 }),
      mkVehicle({ id: "d2", status: "active", play_id: "strike", target_id: "fast1", active: strikeCmd, battery_pct: 29 }),
      mkVehicle({ id: "d4", status: "returning", play_id: "go_home" }),
    ] });
    const rows = vehicleRows(f, NAMES, []);
    expect(rows.map((r) => [r.doing, r.target, r.striking, r.low])).toEqual([
      ["기지 정비", null, false, true], ["표적 타격", "fast1", true, true], ["귀환 중", null, false, false],
    ]);
  });
});
```

Run: `cd modules/cop-ui && npx vitest run src/features/board/vehicleRows.test.ts` → FAIL (import)

- [ ] **Step 2: 구현 — vehicleRows**

`modules/cop-ui/src/features/board/vehicleRows.ts`:

```ts
import type { Frame, VehicleSpec, VehicleStatus } from "../../contracts.gen";

export interface VehicleRow {
  id: string; status: VehicleStatus; doing: string; kind: string; target: string | null;
  striking: boolean; battery: number; low: boolean; waiting: boolean;
}

const KIND_KO: Record<string, string> = {
  recon_drone: "정찰 드론", armed_drone: "무장 드론", armed_usv: "무장 수상정", ground_robot: "지상 로봇",
};
const LOW_PCT = 35;

// Left column (Part1-32): what each of our vehicles does now. A returning or parked vehicle keeps target_id in
// the engine, so only a vehicle on a mission shows a target.
export function vehicleRows(f: Frame, playNames: Record<string, string>, specs: VehicleSpec[]): VehicleRow[] {
  return f.vehicles.map((v) => {
    const spec = specs.find((s) => s.id === v.id);
    const doing = v.status === "returning" ? "귀환 중" : v.status === "maintenance" ? "기지 정비"
      : v.play_id ? playNames[v.play_id] ?? v.play_id : "대기";
    const onMission = v.status === "active";
    return {
      id: v.id, status: v.status, doing,
      kind: (spec?.kind && KIND_KO[spec.kind]) || "",
      target: onMission ? v.target_id ?? null : null,
      striking: onMission && v.active?.command.kind === "strike",
      battery: Math.round(v.battery_pct), low: v.battery_pct < LOW_PCT,
      waiting: f.reports.some((r) => r.vehicle_id === v.id && !r.resolved_ms && (r.choices ?? []).length > 0),
    };
  });
}
```

Run: `cd modules/cop-ui && npx vitest run src/features/board/vehicleRows.test.ts` → PASS (2)

- [ ] **Step 3: 실패 테스트 — targetPlays**

`modules/cop-ui/src/features/board/targetPlays.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import type { ActionKind, Domain, Play } from "../../contracts.gen";
import { targetPlays } from "./targetPlays";

const play = (id: string, kind: ActionKind, domains: Domain[]): Play =>
  ({ id, name: id, domains, entry: "s", steps: [{ id: "s", name: "s", do: { kind } }] });
const PLAYS = [play("watch", "watch_target", ["air"]), play("track_fast", "watch_target", ["air"]),
  play("approach", "approach_target", ["sea"]), play("strike", "strike_target", ["air", "sea"]),
  play("patrol_a", "patrol_route", ["air"])];

describe("targetPlays", () => {
  it("offers the plays whose first step works a target and that the vehicle's domain runs, never strike", () => {
    expect(targetPlays(PLAYS, "air").map((p) => p.id)).toEqual(["watch", "track_fast"]);
    expect(targetPlays(PLAYS, "sea").map((p) => p.id)).toEqual(["approach"]);
    expect(targetPlays(PLAYS, "ground")).toEqual([]);
  });
});
```

Run: → FAIL (import)

- [ ] **Step 4: 구현 — targetPlays**

`modules/cop-ui/src/features/board/targetPlays.ts`:

```ts
import type { ActionKind, Domain, Play } from "../../contracts.gen";

// strike_target is never offered: a switch carries no operator decision id, so safety rule 1 would block it
// (decision 0048). Strikes go through the approval card.
const TARGET_KINDS: ActionKind[] = ["watch_target", "approach_target"];

// Plays offered when the operator points a vehicle at a target (decision 0048): their first step works a target
// and the vehicle's domain can run them.
export function targetPlays(plays: Play[], domain: Domain): Play[] {
  return plays.filter((p) => {
    const first = p.steps.find((s) => s.id === p.entry);
    return p.domains.includes(domain) && !!first && TARGET_KINDS.includes(first.do.kind);
  });
}
```

Run: → PASS (1)

- [ ] **Step 5: 실패 테스트 — postPoint**

`modules/cop-ui/src/features/board/postPoint.test.ts`:

```ts
import { afterEach, describe, expect, it, vi } from "vitest";
import { postPoint } from "./postPoint";

describe("postPoint", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("asks for the play with the target, approved by the press (decisions 0048, 0049)", async () => {
    const f = vi.fn((_u: string, _i?: RequestInit) => Promise.resolve({ ok: true, json: () => Promise.resolve({ id: "inj-3" }) } as Response));
    vi.stubGlobal("fetch", f);
    expect(await postPoint("d3", "watch", "boat2")).toEqual({ ok: true, id: "inj-3" });
    const [url, init] = f.mock.calls[0];
    expect(url).toBe("/injections");
    expect(JSON.parse(init?.body as string)).toEqual({ play_by_vehicle: { d3: "watch" }, target_by_vehicle: { d3: "boat2" }, approve: true });
  });

  it("returns the error instead of throwing when the gateway is down", async () => {
    vi.stubGlobal("fetch", vi.fn(() => Promise.reject(new Error("net"))));
    expect(await postPoint("d3", "watch", "boat2")).toEqual({ ok: false, error: "서버 연결 실패" });
  });
});
```

Run: → FAIL (import)

- [ ] **Step 6: 구현 — postPoint**

`modules/cop-ui/src/features/board/postPoint.ts`:

```ts
import type { SwitchIn } from "../../contracts.gen";
import { postJson, type Sent } from "../cards/postJson";

// Point a vehicle at a target with a play (decisions 0048, 0049). The menu was the preview and the press is the
// approval, so one request the gateway records as approved (one operator action, no pending card).
export function postPoint(vehicle: string, play: string, target: string): Promise<Sent> {
  const body: SwitchIn = { play_by_vehicle: { [vehicle]: play }, target_by_vehicle: { [vehicle]: target }, approve: true };
  return postJson("/injections", body);
}
```

Run: `cd modules/cop-ui && npx vitest run src/features/board` → PASS

- [ ] **Step 7: SPEC 행, commit, ship (Task 3·4 함께)**

```
| UI-59 | vehicleRows | Frame, 플레이 이름, VehicleSpec[] | VehicleRow[] | 하는 일(귀환 중·기지 정비·플레이 이름·대기), 종류 한글, 표적·타격은 임무 중일 때만, 배터리(35% 미만 low), 결정 대기 | 리드 | 완료 |
| UI-60 | targetPlays | Play[], 도메인 | Play[] | 첫 step이 watch_target·approach_target이고 그 도메인을 쓰는 플레이, strike_target 없음(결정 0048) | 리드 | 완료 |
| UI-62 | postPoint | 기체, 플레이, 표적 | Sent | POST /injections {play_by_vehicle, target_by_vehicle, approve: true}(결정 0049), throw 없음 | 리드 | 완료 |
```

```bash
git add modules/cop-ui
git commit -m "Part1-32: vehicle rows (target only on a mission), plays offered when pointing (no strike), pointing request approved by the press"
scripts/ship.sh
```

---

### Task 5: 게이트웨이 데이터 읽기, 카메라 점, 지도 선·원 (UI-63, UI-61, UI-65, UI-66)

**Files:**
- Create: `modules/cop-ui/src/features/board/fetchBoardData.ts`, `fetchBoardData.test.ts`
- Create: `modules/cop-ui/src/features/board/cameraPoints.ts`, `cameraPoints.test.ts`
- Create: `modules/cop-ui/src/features/board/linkLines.ts`, `linkLines.test.ts`
- Create: `modules/cop-ui/src/features/board/watchCircles.ts`, `watchCircles.test.ts`
- Modify: `modules/cop-ui/SPEC.md`

**Interfaces:**
- Consumes: `Track` (Task 3), `Queue` (Task 2), fixtures.
- Produces: `fetchBoardData(): Promise<BoardData>` with `BoardData { plays: Play[]; vehicles: VehicleSpec[]; watch: WatchPoint[] }` and `NO_BOARD_DATA`; `cameraPoints(f: Frame, tracks: Record<string, Track>, queue: Queue): GeoPoint[]`; `linkLines(f, tracks, queue): FeatureCollection<LineString, { k: LinkKind; v: string }>` with `LinkKind = "watch" | "strike" | "est" | "alt"`; `watchCircles(watch: WatchPoint[]): FeatureCollection<LineString>`.

- [ ] **Step 1: 실패 테스트 — fetchBoardData**

`modules/cop-ui/src/features/board/fetchBoardData.test.ts`:

```ts
import { afterEach, describe, expect, it, vi } from "vitest";
import { fetchBoardData } from "./fetchBoardData";

const reply = (body: unknown, ok = true) => Promise.resolve({ ok, json: () => Promise.resolve(body) } as Response);

describe("fetchBoardData", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("reads plays, vehicle specs and watch points", async () => {
    const data: Record<string, unknown> = { "/plays": [{ id: "watch" }], "/vehicles": [{ id: "d1" }], "/watch_points": [{ id: "landing" }] };
    vi.stubGlobal("fetch", vi.fn((u: string) => reply(data[u])));
    expect(await fetchBoardData()).toEqual({ plays: [{ id: "watch" }], vehicles: [{ id: "d1" }], watch: [{ id: "landing" }] });
  });

  it("gives empty lists for a failed, non-list or unreachable read", async () => {
    vi.stubGlobal("fetch", vi.fn((u: string) => (u === "/plays" ? reply(null, false) : u === "/vehicles" ? reply({}) : Promise.reject(new Error("net")))));
    expect(await fetchBoardData()).toEqual({ plays: [], vehicles: [], watch: [] });
  });
});
```

Run: → FAIL (import)

- [ ] **Step 2: 구현 — fetchBoardData**

`modules/cop-ui/src/features/board/fetchBoardData.ts`:

```ts
import type { Play, VehicleSpec, WatchPoint } from "../../contracts.gen";

export interface BoardData { plays: Play[]; vehicles: VehicleSpec[]; watch: WatchPoint[] }
export const NO_BOARD_DATA: BoardData = { plays: [], vehicles: [], watch: [] };

async function list<T>(url: string): Promise<T[]> {
  try {
    const r = await fetch(url);
    if (!r.ok) return [];
    const d = await r.json();
    return Array.isArray(d) ? (d as T[]) : [];
  } catch {
    return [];
  }
}

// What the live board needs besides the Frame (Part1-32): play names and first steps, vehicle specs, watch points
// (decision 0047). A failed read is an empty list, never a broken screen.
export async function fetchBoardData(): Promise<BoardData> {
  const [plays, vehicles, watch] = await Promise.all([
    list<Play>("/plays"), list<VehicleSpec>("/vehicles"), list<WatchPoint>("/watch_points"),
  ]);
  return { plays, vehicles, watch };
}
```

Run: → PASS (2)

- [ ] **Step 3: 실패 테스트 — cameraPoints**

`modules/cop-ui/src/features/board/cameraPoints.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { cameraPoints } from "./cameraPoints";
import { at, mkCard, mkFrame, mkVehicle, mkTarget, T0 } from "./boardFixtures";

const EMPTY = { action: [], alerts: [], history: [] };

describe("cameraPoints", () => {
  it("is empty when nothing is on the map", () => {
    expect(cameraPoints(mkFrame(), {}, EMPTY)).toEqual([]);
  });

  it("looks at targets where we show them, a lost one's estimate, and vehicles on a mission with a target", () => {
    const f = mkFrame({
      targets: [mkTarget({ id: "boat1" }), mkTarget({ id: "old", neutralized_ms: T0 - 130_000 })],
      vehicles: [mkVehicle({ id: "d1", status: "active", target_id: "boat1", pos: at(37.98, 124.7) }),
        mkVehicle({ id: "d4", status: "maintenance", target_id: "boat1", pos: at(37.95, 124.7) })],
    });
    const tracks = { boat1: { k: "lost" as const, pos: at(37.99, 124.74), est: at(37.99, 124.75) }, old: { k: "gone" as const, pos: at(1, 1) } };
    expect(cameraPoints(f, tracks, EMPTY)).toEqual([at(37.99, 124.74), at(37.99, 124.75), at(37.98, 124.7)]);
  });

  it("adds every vehicle an open card names and a block's alternative point", () => {
    const f = mkFrame({ vehicles: [mkVehicle({ id: "d3", pos: at(37.94, 124.7) }), mkVehicle({ id: "usv", pos: at(37.98, 124.69) })] });
    const q = { action: [
      { key: "r", cards: [mkCard({ id: "r", choices: [{ id: "t", label: "d3 → 순찰", preview: "d3→patrol_a" }] })] },
      { key: "b", cards: [mkCard({ id: "b", source: "block", vehicle: "usv", alternative: { lat: 38, lon: 124.6 } })] },
    ], alerts: [], history: [] };
    expect(cameraPoints(f, {}, q)).toEqual([at(37.94, 124.7), at(37.98, 124.69), { lat: 38, lon: 124.6 }]);
  });
});
```

Run: → FAIL (import)

- [ ] **Step 4: 구현 — cameraPoints**

`modules/cop-ui/src/features/board/cameraPoints.ts`:

```ts
import type { Frame, GeoPoint } from "../../contracts.gen";
import type { Queue } from "./decisionQueue";
import type { Track } from "./trackState";

const KEEP_GONE_MS = 120_000;
const movedBy = (preview: string) => preview.split(" · ").map((x) => x.split("→")[0]).filter(Boolean);

// Where the map looks (Part1-32): targets where we show them (and where a lost one may be now), vehicles on a
// mission with a target, every vehicle an open card names (reporter and the vehicles its choices move), and a
// block's alternative point.
export function cameraPoints(f: Frame, tracks: Record<string, Track>, queue: Queue): GeoPoint[] {
  const pts: GeoPoint[] = [];
  for (const t of f.targets) {
    const tr = tracks[t.id];
    if (!tr || (t.neutralized_ms != null && f.t_ms - t.neutralized_ms >= KEEP_GONE_MS)) continue;
    pts.push(tr.pos, ...(tr.est ? [tr.est] : []));
  }
  const cards = queue.action.flatMap((i) => i.cards);
  const named = new Set(cards.flatMap((c) => [...(c.vehicle ?? "").split("·"), ...c.choices.flatMap((ch) => movedBy(ch.preview))]));
  for (const v of f.vehicles) if ((v.status === "active" && v.target_id) || named.has(v.id)) pts.push(v.pos);
  for (const c of cards) if (c.source === "block" && c.alternative) pts.push(c.alternative);
  return pts;
}
```

Run: → PASS (3)

- [ ] **Step 5: 실패 테스트 — linkLines, watchCircles**

`modules/cop-ui/src/features/board/linkLines.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { at, mkCard, mkFrame, mkVehicle } from "./boardFixtures";
import { linkLines } from "./linkLines";

const strikeCmd = { command: { id: "c", vehicle_id: "d2", kind: "strike" as const, params: {} }, checks: [], passed_ms: 0 };

describe("linkLines", () => {
  it("joins vehicles on a mission to the target they work, solid for a strike, none for a struck target", () => {
    const f = mkFrame({ vehicles: [
      mkVehicle({ id: "d1", status: "active", target_id: "boat1", pos: at(1, 1) }),
      mkVehicle({ id: "d2", status: "active", target_id: "fast1", pos: at(2, 2), active: strikeCmd }),
      mkVehicle({ id: "d3", status: "active", target_id: "gone1", pos: at(3, 3) }),
      mkVehicle({ id: "d4", status: "maintenance", target_id: "boat1", pos: at(4, 4) }),
    ] });
    const tracks = { boat1: { k: "seen" as const, pos: at(5, 5) }, fast1: { k: "seen" as const, pos: at(6, 6) },
      gone1: { k: "gone" as const, pos: at(7, 7) } };
    const fc = linkLines(f, tracks, { action: [], alerts: [], history: [] });
    expect(fc.features.map((x) => [x.properties.k, x.properties.v, x.geometry.coordinates])).toEqual([
      ["watch", "d1", [[1, 1], [5, 5]]], ["strike", "d2", [[2, 2], [6, 6]]],
    ]);
  });

  it("draws a lost target's estimate and a blocked vehicle's way to the alternative", () => {
    const f = mkFrame({ vehicles: [mkVehicle({ id: "d2", pos: at(1, 1) })] });
    const tracks = { fast1: { k: "lost" as const, pos: at(2, 2), est: at(3, 3) } };
    const q = { action: [{ key: "b", cards: [mkCard({ id: "b", source: "block", vehicle: "d2", alternative: { lat: 4, lon: 4 } })] }],
      alerts: [], history: [] };
    expect(linkLines(f, tracks, q).features.map((x) => [x.properties.k, x.properties.v, x.geometry.coordinates])).toEqual([
      ["est", "fast1", [[2, 2], [3, 3]]], ["alt", "d2", [[1, 1], [4, 4]]],
    ]);
  });
});
```

`modules/cop-ui/src/features/board/watchCircles.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { at } from "./boardFixtures";
import { watchCircles } from "./watchCircles";

describe("watchCircles", () => {
  it("draws each watch point's radius as a closed ring of 64 segments", () => {
    const fc = watchCircles([{ id: "landing", name: "상륙 예상 지점", pos: at(37.978, 124.7), radius_m: 2000 }]);
    const ring = fc.features[0].geometry.coordinates;
    expect(ring).toHaveLength(65);
    expect(ring[64]).toEqual(ring[0]);
    expect(ring[0][1]).toBeCloseTo(37.978, 6);
    expect(ring[16][1]).toBeCloseTo(37.978 + 2000 / 111_320, 6);
  });

  it("is empty without watch points", () => {
    expect(watchCircles([]).features).toEqual([]);
  });
});
```

Run: `cd modules/cop-ui && npx vitest run src/features/board/linkLines.test.ts src/features/board/watchCircles.test.ts` → FAIL (import)

- [ ] **Step 6: 구현 — linkLines, watchCircles**

`modules/cop-ui/src/features/board/linkLines.ts`:

```ts
import type { Feature, FeatureCollection, LineString } from "geojson";
import type { Frame, GeoPoint } from "../../contracts.gen";
import type { Queue } from "./decisionQueue";
import type { Track } from "./trackState";

export type LinkKind = "watch" | "strike" | "est" | "alt";
type Link = Feature<LineString, { k: LinkKind; v: string }>;

const line = (k: LinkKind, v: string, a: GeoPoint, b: GeoPoint): Link =>
  ({ type: "Feature", properties: { k, v }, geometry: { type: "LineString", coordinates: [[a.lon, a.lat], [b.lon, b.lat]] } });

// Map lines (Part1-32): each vehicle on a mission to the target it works (dashed watch, solid strike; none to a
// struck target unless striking), a lost target's estimate from where it was last seen, and a blocked vehicle
// to the alternative point its block offers.
export function linkLines(f: Frame, tracks: Record<string, Track>, queue: Queue): FeatureCollection<LineString, { k: LinkKind; v: string }> {
  const out: Link[] = [];
  for (const v of f.vehicles) {
    const tr = v.status === "active" && v.target_id ? tracks[v.target_id] : undefined;
    const strike = v.active?.command.kind === "strike";
    if (tr && (tr.k !== "gone" || strike)) out.push(line(strike ? "strike" : "watch", v.id, v.pos, tr.pos));
  }
  for (const [id, tr] of Object.entries(tracks)) if (tr.est) out.push(line("est", id, tr.pos, tr.est));
  for (const c of queue.action.flatMap((i) => i.cards)) {
    const v = c.source === "block" && c.alternative ? f.vehicles.find((x) => x.id === c.vehicle) : undefined;
    if (v && c.alternative) out.push(line("alt", v.id, v.pos, c.alternative));
  }
  return { type: "FeatureCollection", features: out };
}
```

`modules/cop-ui/src/features/board/watchCircles.ts`:

```ts
import type { FeatureCollection, LineString, Position } from "geojson";
import type { WatchPoint } from "../../contracts.gen";

const M_PER_DEG = 111_320;
const SEGMENTS = 64;

// Watch point radius as a ring (Part1-32): "inside the expected landing radius +0.30" on a risk line is visible
// on the map. Outline only, so it never outshines the targets.
export function watchCircles(watch: WatchPoint[]): FeatureCollection<LineString> {
  return {
    type: "FeatureCollection",
    features: watch.map((w) => {
      const mLon = M_PER_DEG * Math.cos((w.pos.lat * Math.PI) / 180);
      const ring: Position[] = [];
      for (let i = 0; i <= SEGMENTS; i++) {
        const a = (i / SEGMENTS) * 2 * Math.PI;
        ring.push(i === SEGMENTS ? ring[0] : [w.pos.lon + (w.radius_m * Math.cos(a)) / mLon, w.pos.lat + (w.radius_m * Math.sin(a)) / M_PER_DEG]);
      }
      return { type: "Feature", properties: {}, geometry: { type: "LineString", coordinates: ring } };
    }),
  };
}
```

Run: `cd modules/cop-ui && npx vitest run src/features/board` → PASS

- [ ] **Step 7: SPEC 행, commit**

```
| UI-61 | cameraPoints | Frame, Track 묶음, Queue | GeoPoint[] | 표적 표시 위치·추정 위치(2분 넘은 무력화 제외), 임무 중 표적 맡은 기체, 열린 카드가 부르는 기체(보고·선택지 미리 보기), 차단 대안 지점, 없으면 빈 목록 | 리드 | 완료 |
| UI-63 | fetchBoardData | — | {plays, vehicles, watch} | GET /plays·/vehicles·/watch_points, 실패·목록 아님·연결 실패는 빈 목록 | 리드 | 완료 |
| UI-65 | linkLines | Frame, Track 묶음, Queue | FeatureCollection | 임무 중 기체→표적(감시·타격, 무력화 표적엔 타격만), 놓친 표적 추정선, 차단 기체→대안 지점 | 리드 | 완료 |
| UI-66 | watchCircles | WatchPoint[] | FeatureCollection | 기준점 반경 고리(64칸, 닫힘) | 리드 | 완료 |
```

```bash
git add modules/cop-ui
git commit -m "Part1-32: board data reads, camera points, map link lines and watch point rings"
```

---

### Task 6: boardView 묶음과 오른쪽·머리·왼쪽 화면 (UI-64, UI-67~69)

**Files:**
- Create: `modules/cop-ui/src/features/board/boardView.ts`, `boardView.test.ts`
- Create: `modules/cop-ui/src/features/board/useBoardData.ts`
- Create: `modules/cop-ui/src/features/board/SituationBar.tsx`, `LoadBar.tsx`, `RosterPanel.tsx`, `DecisionQueue.tsx`, `QueueCard.tsx`, `board.css`
- Modify: `modules/cop-ui/src/Screen.tsx` (전체), `modules/cop-ui/src/App.tsx` (머리 자리), `modules/cop-ui/src/index.css` (`.layout`), `modules/cop-ui/src/theme.css` (끝에 구역 추가)
- Modify: `scripts/qa/live.json`, `modules/cop-ui/SPEC.md`

**Interfaces:**
- Consumes: Task 2~5 함수, `frameCards`, `pruneSent`, `postDecision`, `postSettle`, `postDirect`, `metricView`, `SwitchPanel`, `RunBar`, `MapView`(Task 7 전까지 지금 서명), `ObjectGraphView`.
- Produces: `boardView(f: Frame, data: BoardData): BoardView` with `BoardView { tracks: Record<string, Track>; stages: Record<string, Stage>; queue: Queue; situation: Situation; rows: VehicleRow[] }`; `useBoardData(ready: boolean): BoardData`; 부품 `SituationBar({ situation })`, `LoadBar({ metrics })`, `RosterPanel({ rows, targets, stages, selected, onVehicle, onTarget })`, `DecisionQueue({ frame, queue, onGraph })`, `QueueCard({ frame, item, sent, send, onGraph })`.

- [ ] **Step 1: 실패 테스트 — boardView**

`modules/cop-ui/src/features/board/boardView.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import s1 from "../../../../../contracts/examples/frames/s1_report_wait.json";
import type { Frame } from "../../contracts.gen";
import { boardView } from "./boardView";
import { NO_BOARD_DATA } from "./fetchBoardData";

describe("boardView", () => {
  it("draws the board from a Frame even before plays, specs and watch points arrive", () => {
    const v = boardView(s1 as Frame, NO_BOARD_DATA);
    expect(Object.keys(v.tracks)).toEqual(["boat1"]);
    expect(v.stages.boat1.key).toBe("found"); // d1 sees boat1 but has no target_id in this example
    expect(v.queue.action.map((i) => i.key)).toEqual(["rep-d1-1791634270000"]);
    expect(v.situation.decisions).toBe(1);
    expect(v.rows.map((r) => r.id)).toEqual(["d1", "d2", "d3", "usv", "ugv", "d4"]);
  });
});
```

Run: `cd modules/cop-ui && npx vitest run src/features/board/boardView.test.ts` → FAIL (import)

- [ ] **Step 2: 구현 — boardView, useBoardData**

`modules/cop-ui/src/features/board/boardView.ts`:

```ts
import type { Frame } from "../../contracts.gen";
import { frameCards } from "../cards/frameCards";
import { type Queue, decisionQueue } from "./decisionQueue";
import type { BoardData } from "./fetchBoardData";
import { type Situation, situationCounts } from "./situationCounts";
import { type Stage, targetStage } from "./targetStage";
import { type Track, trackState } from "./trackState";
import { type VehicleRow, vehicleRows } from "./vehicleRows";

export interface BoardView {
  tracks: Record<string, Track>; stages: Record<string, Stage>; queue: Queue; situation: Situation; rows: VehicleRow[];
}

// Everything the live board draws from one Frame (Part1-32), computed once per Frame.
export function boardView(f: Frame, data: BoardData): BoardView {
  const watch = data.watch[0]?.pos ?? null;
  const tracks = Object.fromEntries(f.targets.map((t) => [t.id, trackState(t, f.t_ms, watch)]));
  const stages = Object.fromEntries(f.targets.map((t) => [t.id, targetStage(f, t, tracks[t.id])]));
  const queue = decisionQueue(frameCards(f), f.t_ms);
  const names = Object.fromEntries(data.plays.map((p) => [p.id, p.name]));
  return { tracks, stages, queue, situation: situationCounts(Object.values(stages), queue), rows: vehicleRows(f, names, data.vehicles) };
}
```

`modules/cop-ui/src/features/board/useBoardData.ts`:

```ts
import { useEffect, useState } from "react";
import { type BoardData, fetchBoardData, NO_BOARD_DATA } from "./fetchBoardData";

// Reads plays, specs and watch points once the gateway answers (ready = a Frame arrived), again if all came
// back empty (the gateway was still starting).
export function useBoardData(ready: boolean): BoardData {
  const [data, setData] = useState<BoardData>(NO_BOARD_DATA);
  const empty = data.plays.length === 0 && data.vehicles.length === 0;
  useEffect(() => {
    if (ready && empty) fetchBoardData().then(setData);
  }, [ready, empty]);
  return data;
}
```

Run: `cd modules/cop-ui && npx vitest run src/features/board/boardView.test.ts` → PASS.

- [ ] **Step 3: 머리·왼쪽 부품**

`modules/cop-ui/src/features/board/SituationBar.tsx`:

```tsx
import type { Situation } from "./situationCounts";

// Header, middle (Part1-32): targets per stage, most urgent first, and the decisions waiting (white = your turn).
export function SituationBar({ situation }: { situation: Situation }) {
  return (
    <div className="situation">
      <span className="lbl">적 {situation.targets}척</span>
      {situation.stages.map((s) => (
        <span key={s.key} className={`c ${s.key}`}><b>{s.n}</b>{s.label}</span>
      ))}
      <span className="sep" />
      <span className={`c dec${situation.decisions ? "" : " none"}`}><b>{situation.decisions}</b>결정 대기</span>
    </div>
  );
}
```

`modules/cop-ui/src/features/board/LoadBar.tsx`:

```tsx
import type { Metrics } from "../../contracts.gen";
import { metricView } from "../run/metricView";

// Header, right (Part1-32): operator actions next to the manual baseline of the same run (docs/research/09 2.3).
// The other numbers and what the baseline means sit in the tooltip.
export function LoadBar({ metrics }: { metrics: Metrics | null }) {
  if (!metrics) return null;
  const v = metricView(metrics);
  const title = [...v.rows.map(([k, x]) => `${k} ${x}`),
    "수동 기준 = 같은 실행에서 엔진이 만든 명령 수 + 보고 카드 수(사람이 누른 수가 아님)"].join("\n");
  return (
    <div className="loadbar" title={title}>
      <span className="op"><b>{v.operator}</b><small>운용자<br />조작</small></span>
      <span className="vs">vs</span>
      <span className="man"><b>{v.manual}</b><small>기체별 직접<br />명령이었다면</small></span>
    </div>
  );
}
```

`modules/cop-ui/src/features/board/RosterPanel.tsx`:

```tsx
import type { Target } from "../../contracts.gen";
import type { Stage } from "./targetStage";
import type { VehicleRow } from "./vehicleRows";

const KIND_KO: Record<string, string> = { boat: "보트", fast_boat: "고속정", person: "사람", unknown: "미상" };
const tone = (r: number) => (r >= 0.7 ? "hi" : r >= 0.4 ? "mid" : "lo");
const QUIET: Record<string, number> = { gone: 1, never: 2 };

// Left column (Part1-32): our vehicles (what each does, its target, battery) and the targets by risk with their
// own stage. A vehicle row selects it like its map marker; with a vehicle selected a target row points at it.
export function RosterPanel({ rows, targets, stages, selected, onVehicle, onTarget }: {
  rows: VehicleRow[]; targets: Target[]; stages: Record<string, Stage>; selected: string | null;
  onVehicle: (id: string) => void; onTarget: (id: string) => void;
}) {
  const busy = rows.filter((r) => r.status === "active").length;
  const back = rows.filter((r) => r.status === "returning").length;
  const idle = rows.length - busy - back;
  const counts = [busy && `임무 ${busy}`, back && `귀환 ${back}`, idle && `대기 ${idle}`].filter(Boolean).join(" · ");
  const ts = [...targets].sort((a, b) => (QUIET[stages[a.id]?.key] ?? 0) - (QUIET[stages[b.id]?.key] ?? 0)
    || (b.threat ?? 0) - (a.threat ?? 0));
  const gone = targets.filter((t) => t.neutralized_ms != null).length;
  return (
    <aside className="roster">
      <h3>아군 <b>{rows.length}</b><small>{counts}</small></h3>
      {rows.map((r) => (
        <button key={r.id} type="button" className={`ro st-${r.status}${r.id === selected ? " sel" : ""}`} onClick={() => onVehicle(r.id)}>
          <span className="l1"><b>{r.id}</b><span className="doing">{r.doing}</span>{r.waiting && <span className="chip">결정 대기</span>}</span>
          <span className="l2">
            <span className="kind">{r.kind}</span>
            {r.target && <span className={`tgt${r.striking ? " strike" : ""}`}>{r.striking ? "타격 →" : "→"} {r.target}</span>}
            <span className={`bat${r.low ? " low" : ""}`}><i style={{ width: `${r.battery}%` }} /></span>
            <em className={r.low ? "low" : ""}>{r.battery}%</em>
          </span>
        </button>
      ))}
      <h3 className="en">적 <b>{targets.length - gone}</b><small>{gone ? `무력화 ${gone} · ` : ""}위험도 순</small></h3>
      {ts.map((t) => {
        const s = stages[t.id];
        const r = (t.threat ?? 0) / 100;
        const quiet = s?.key === "gone" || s?.key === "never";
        return (
          <button key={t.id} type="button" className={`ro en ${quiet ? s.key : tone(r)}`} onClick={() => onTarget(t.id)}>
            <span className="l1">
              <b>{t.id}</b><span className="doing">{KIND_KO[t.kind] ?? t.kind}</span>
              {t.rf_detected && !quiet && <span className="rf">RF</span>}
              <span className="risk">{quiet ? "—" : r.toFixed(2)}</span>
            </span>
            <span className="l2"><span className={`stg ${s?.key}${s?.away ? " away" : ""}`}>{s?.label}</span><span className="det">{s?.detail}</span></span>
            {!quiet && <span className="rbar"><i style={{ width: `${Math.min(100, r * 100)}%` }} /></span>}
          </button>
        );
      })}
    </aside>
  );
}
```

- [ ] **Step 4: 오른쪽 부품**

`modules/cop-ui/src/features/board/QueueCard.tsx`:

```tsx
import type { Frame } from "../../contracts.gen";
import type { Card } from "../cards/frameCards";
import { postSettle } from "../cards/injectionRequests";
import { postDecision } from "../cards/postDecision";
import { postDirect } from "../cards/postDirect";
import type { Sent } from "../cards/postJson";
import { choiceGroups } from "./choiceGroups";
import type { QueueItem } from "./decisionQueue";

export type SendState = { state: "sending" } | { state: "sent"; id: string } | { state: "error"; error: string };
export type Send = (cardId: string, request: () => Promise<Sent>) => void;

const BLOCK_KO: Record<string, string> = { outside_zone: "작전 구역 밖", battery_insufficient: "귀환 배터리 부족", no_provenance: "근거 없음" };
const tone = (r: number) => (r >= 0.7 ? "hi" : r >= 0.4 ? "mid" : "lo");
const isApproval = (c: Card) => c.source === "report" && c.text.startsWith("타격 승인 요청");

function Note({ card, s, paused }: { card: Card; s?: SendState; paused: boolean }) {
  if (s?.state === "error") return <div className="note error">보내기 실패: {s.error}</div>;
  if (s?.state !== "sent") return null;
  return <div className="note">{card.source === "block" ? `대안 지점 보냄 ${s.id}` : `보냄 ${s.id} · ${paused ? "재생하면 반영" : "다음 틱에 반영"}`}</div>;
}

// One open queue item (Part1-32): title, sensor line, why it asks, risk with its reasons, the question, then the
// buttons — planned choices first and drone requests grouped (decision 0046), target picks as risk-ordered chips
// per vehicle, strike approval in red, approve / reject for a switch, the alternative point for a block.
export function QueueCard({ frame, item, sent, send, onGraph }: {
  frame: Frame; item: QueueItem; sent: Record<string, SendState>; send: Send; onGraph?: (target: string) => void;
}) {
  const c = item.cards[0];
  const paused = frame.run.status === "paused";
  const locked = (id: string) => sent[id]?.state === "sending" || sent[id]?.state === "sent";
  const battery = (v: string) => frame.vehicles.find((x) => x.id === v)?.battery_pct;
  const head = (title: string, tid: string | null) => (
    <div className="head"><b>{title}</b>{tid && <span className="tid">{tid}</span>}<time>{c.time}</time></div>
  );

  if (c.source === "block") return (
    <div className="card first t-block">
      {head(`명령 차단 · ${BLOCK_KO[c.kind] ?? c.kind}`, c.vehicle)}
      <div className="text">{c.text}</div>
      <div className="hint">{c.vehicle}는 하던 일을 계속합니다. 안전 검사가 고른 대안 지점으로 보낼 수 있습니다.</div>
      <div className="q">대안 지점으로 보낼까요?</div>
      {c.alternative && c.vehicle && (
        <button className="wide go" disabled={locked(c.id)} onClick={() => send(c.id, () => postDirect(c.vehicle!, c.alternative!))}>
          대안 지점으로<small>{c.vehicle} → {c.alternative.lat.toFixed(4)}, {c.alternative.lon.toFixed(4)}</small>
        </button>
      )}
      <Note card={c} s={sent[c.id]} paused={paused} />
    </div>
  );

  if (c.source === "injection") return (
    <div className="card first">
      {head(`전환 승인 · ${c.text}`, c.vehicle)}
      <div className="text">{c.preview}</div>
      <div className="settle">
        <button className="wide pri" disabled={locked(c.id)} onClick={() => send(c.id, () => postSettle(c.id, true))}>승인</button>
        <button className="wide" disabled={locked(c.id)} onClick={() => send(c.id, () => postSettle(c.id, false))}>거부</button>
      </div>
      <Note card={c} s={sent[c.id]} paused={paused} />
    </div>
  );

  if (c.kind === "target_select") {
    const vs = item.cards.map((x) => x.vehicle).join("·");
    return (
      <div className="card first">
        {head("추적할 표적 선택", vs)}
        <div className="hint">위험도가 가장 높은 표적이 맨 앞입니다. 기체마다 하나씩 고릅니다.</div>
        {item.cards.map((x) => {
          const opts = x.choices.map((ch) => ({ ch, t: frame.targets.find((t) => t.id === ch.label.split(" ")[0]) }))
            .sort((a, b) => (b.t?.threat ?? 0) - (a.t?.threat ?? 0));
          return (
            <div key={x.id} className="selrow">
              <span className="who">{x.vehicle}<small>{Math.round(battery(x.vehicle ?? "") ?? 0)}%</small></span>
              <div className="tchips">
                {opts.map(({ ch, t }, i) => {
                  const r = (t?.threat ?? 0) / 100;
                  return (
                    <button key={ch.id} className={`tchip ${tone(r)}${i === 0 ? " top" : ""}`} disabled={locked(x.id)}
                      onClick={() => send(x.id, () => postDecision(x.id, ch.id))}>
                      {t?.id ?? ch.label}<em>{r.toFixed(2)}{t?.rf_detected ? " RF" : ""}</em>
                    </button>
                  );
                })}
              </div>
              <Note card={x} s={sent[x.id]} paused={paused} />
            </div>
          );
        })}
      </div>
    );
  }

  const ap = isApproval(c);
  const { planned, requests } = choiceGroups(c.choices);
  const sensor = c.text.split(" · ").slice(1).join(" · ") || c.text;
  const hint = ap ? "사람이 고르기 전에는 어떤 기체도 타격하지 않습니다."
    : `${c.vehicle}는 그 배 위에 머뭅니다. 정해진 대응을 고르거나, 기지 대기 드론에게 비는 해안이나 함께 감시를 맡기세요.`;
  return (
    <div className={`card first${ap ? " t-danger" : ""}`}>
      {head(ap ? "타격 허락 요청" : "표적 발견", c.target ?? null)}
      <div className="text">{sensor}</div>
      <div className="hint">{hint}</div>
      {c.threat && (
        <div className={`threat${c.threat.rf ? " rf" : ""}`}>
          <span className={`sc ${tone(c.threat.score)}`}>위험 {c.threat.score.toFixed(2)}</span>
          {c.threat.parts.slice(1).map((p) => <span key={p} className="why">{p}</span>)}
        </div>
      )}
      <div className="q">{ap ? "타격을 허락할까요?" : "누구를 보낼까요?"}</div>
      {planned.map((ch, i) => (
        <button key={ch.id} className={`wide ${ap ? (i === 0 ? "strike" : "strike2") : ch.preview ? "pri" : ""}`}
          disabled={locked(c.id)} onClick={() => send(c.id, () => postDecision(c.id, ch.id))}>
          {ch.label}<small>{ch.preview || "아무 기체도 옮기지 않음"}</small>
        </button>
      ))}
      {requests.length > 0 && <div className="reqs">기지 대기 드론에게 맡기기</div>}
      {requests.map((g) => (
        <div key={g.what} className="grp">
          <span className="gl">{g.what}</span>
          <span className="vs">
            {g.options.map((o) => {
              const b = battery(o.vehicle);
              return (
                <button key={o.choiceId} className={`vbtn${b !== undefined && b < 50 ? " low" : ""}`} disabled={locked(c.id)}
                  onClick={() => send(c.id, () => postDecision(c.id, o.choiceId))}>
                  {o.vehicle}<small>{b !== undefined ? `${Math.round(b)}%` : ""}</small>
                </button>
              );
            })}
          </span>
        </div>
      ))}
      <Note card={c} s={sent[c.id]} paused={paused} />
      {onGraph && c.target && <button className="graph-open" onClick={() => onGraph(c.target!)}>연결 보기</button>}
    </div>
  );
}
```

`modules/cop-ui/src/features/board/DecisionQueue.tsx`:

```tsx
import { useEffect, useRef, useState } from "react";
import type { Frame } from "../../contracts.gen";
import type { Card } from "../cards/frameCards";
import { pruneSent } from "../cards/pruneSent";
import type { Queue, QueueItem } from "./decisionQueue";
import { QueueCard, type Send, type SendState } from "./QueueCard";

const tone = (r: number) => (r >= 0.7 ? "hi" : r >= 0.4 ? "mid" : "lo");

function Row({ item, onOpen }: { item: QueueItem; onOpen: () => void }) {
  const c = item.cards[0];
  const ap = c.source === "report" && c.text.startsWith("타격 승인 요청");
  const [b, who] = c.source === "block" ? [c.vehicle, "명령 차단 · 대안 지점"]
    : c.source === "injection" ? [c.text, "전환 승인"]
    : item.cards.length > 1 || c.kind === "target_select" ? [item.cards.map((x) => x.vehicle).join("·"), "쫓을 표적 고르기"]
    : [c.target, ap ? `${c.vehicle} 타격 허락 요청` : `${c.vehicle} 발견 · 누구를 보낼지`];
  return (
    <button type="button" className={`qrow${ap || c.source === "block" ? " t-danger" : ""}`} onClick={onOpen}>
      <b>{b}</b>{c.threat && <span className={`sc ${tone(c.threat.score)}`}>{c.threat.score.toFixed(2)}</span>}
      <span className="who">{who}</span><time>{c.time}</time><span className="go">▸</span>
    </button>
  );
}

function Idle({ frame, alerts }: { frame: Frame; alerts: Card[] }) {
  const win = alerts.find((c) => c.kind === "target_neutralized");
  const m = frame.metrics;
  return win ? (
    <div className="next-act done"><div className="k">작전 결과</div><div className="t">{win.target} 무력화 — 사람 허락 뒤 타격</div>
      <div className="s">운용자 조작 {m.operator_actions ?? 0}번 (기체별 직접 명령이었다면 {m.manual_baseline_actions ?? 0}번)</div></div>
  ) : (
    <div className="next-act"><div className="k">할 일 없음</div><div className="t">지금 결정할 것이 없습니다</div>
      <div className="s">▶ 재생하거나 다음 사건으로 넘어가세요.</div></div>
  );
}

// Right column (Part1-32): the decision queue — one item open (the first, or the one the operator opened), the
// rest one line each; with nothing waiting, what to do next. One answer per card, locked while sending and after
// the server accepted it until the Frame shows it done; a reset forgets what was sent (UI-20).
export function DecisionQueue({ frame, queue, onGraph }: { frame: Frame; queue: Queue; onGraph?: (target: string) => void }) {
  const [sent, setSent] = useState<Record<string, SendState>>({});
  const [openKey, setOpenKey] = useState<string | null>(null);
  const lastT = useRef(0);
  useEffect(() => {
    const back = frame.t_ms < lastT.current;
    lastT.current = frame.t_ms;
    const ids = [...frame.reports.map((r) => r.id), ...frame.injections.map((i) => i.id), ...frame.blocks.map((b) => b.command_id)];
    setSent((m) => pruneSent(m, ids, back));
  }, [frame]);
  const send: Send = async (cardId, request) => {
    const s = sent[cardId]?.state;
    if (s === "sending" || s === "sent") return;
    setSent((m) => ({ ...m, [cardId]: { state: "sending" } }));
    const r = await request();
    setSent((m) => ({ ...m, [cardId]: r.ok ? { state: "sent", id: r.id } : { state: "error", error: r.error } }));
  };
  const open = queue.action.find((i) => i.key === openKey) ?? queue.action[0];
  const decisions = queue.action.reduce((n, i) => n + i.cards.length, 0);
  return (
    <div className="queue">
      {open ? (
        <>
          <div className="sec">결정 대기 <b>{decisions}</b><span className="ord">타격 허락 · 차단 · 위험도 순</span></div>
          {queue.action.map((item) => (item === open
            ? <QueueCard key={item.key} frame={frame} item={item} sent={sent} send={send} onGraph={onGraph} />
            : <Row key={item.key} item={item} onOpen={() => setOpenKey(item.key)} />))}
        </>
      ) : <Idle frame={frame} alerts={queue.alerts} />}
      {queue.alerts.length > 0 && <div className="sec">알림</div>}
      {queue.alerts.map((c) => (
        <div key={`${c.source}-${c.id}`} className={`alert${c.kind === "target_neutralized" ? " win" : c.source === "block" ? " blk" : ""}`}>
          <b>{c.kind === "target_neutralized" ? `${c.target} 무력화` : c.text}</b><time>{c.time}</time>
          {c.preview && <span className="why">{c.preview}</span>}
          {onGraph && c.target && c.kind === "target_neutralized" && <button className="graph-open" onClick={() => onGraph(c.target!)}>연결 보기</button>}
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 5: Screen, App, 배치 CSS**

`modules/cop-ui/src/App.tsx`의 `<header className="tabs">` 안 마지막 `<a href="#live" ...>` 다음 줄에:

```tsx
        <div id="header-slot" className="header-slot" />
```

`modules/cop-ui/src/Screen.tsx` 전체:

```tsx
import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import type { Frame, Polygon } from "./contracts.gen";
import { boardView } from "./features/board/boardView";
import { DecisionQueue } from "./features/board/DecisionQueue";
import { LoadBar } from "./features/board/LoadBar";
import { RosterPanel } from "./features/board/RosterPanel";
import { SituationBar } from "./features/board/SituationBar";
import { useBoardData } from "./features/board/useBoardData";
import "./features/board/board.css";
import { SwitchPanel } from "./features/cards/SwitchPanel";
import { ObjectGraphView } from "./features/graph/ObjectGraphView";
import { tilesExist } from "./features/map/basemap";
import { MapView } from "./features/map/MapView";
import { useDirectControl } from "./features/map/useDirectControl";
import { RunBar } from "./features/run/RunBar";

// Live board (Part1-32): header line (stage counts, operator load, link status) in the app header, our vehicles
// and the targets on the left, the map with the run bar in the middle, the decision queue on the right with the
// switch panel and the history folded under it. A card's "연결 보기" opens its target's graph over the map.
export function Screen({ frame, zone, status, ok }:
  { frame: Frame | null; zone: Polygon | null; status: string; ok: boolean }) {
  const [tiles, setTiles] = useState<boolean | null>(null);
  const [graph, setGraph] = useState<string | null>(null);
  const [slot, setSlot] = useState<HTMLElement | null>(null);
  const data = useBoardData(frame !== null);
  const direct = useDirectControl(frame?.t_ms ?? 0);
  const board = useMemo(() => (frame ? boardView(frame, data) : null), [frame, data]);
  useEffect(() => {
    tilesExist().then(setTiles);
    setSlot(document.getElementById("header-slot"));
  }, []);
  return (
    <div className="layout board">
      {slot && createPortal(
        <>
          {board && <SituationBar situation={board.situation} />}
          <LoadBar metrics={frame?.metrics ?? null} />
          <div className={ok ? "status ok" : "status down"}>{status}</div>
        </>, slot)}
      {frame && board ? (
        <RosterPanel rows={board.rows} targets={frame.targets} stages={board.stages} selected={direct.selected}
          onVehicle={direct.onVehicleClick} onTarget={() => {}} />
      ) : <aside className="roster" />}
      <div className="map-col">
        {tiles === null ? <div className="map" /> : <MapView frame={frame} zone={zone} tilesAvailable={tiles} direct={direct} />}
        {direct.hint && <div className={direct.selected ? "direct-hint on" : "direct-hint"}>{direct.hint}</div>}
        <RunBar frame={frame} />
        {graph && <ObjectGraphView focus={graph} onClose={() => setGraph(null)} />}
      </div>
      <aside className="ops">
        <div className="ops-scroll">
          {frame && board ? <DecisionQueue frame={frame} queue={board.queue} onGraph={setGraph} /> : <div className="next-act"><div className="t">게이트웨이 연결 대기</div></div>}
        </div>
        <div className="folds">
          <details className="fold switch"><summary>작전 전환 <small>전 기체 · 기체 하나만</small></summary><SwitchPanel frame={frame} /></details>
          <details className="fold hist"><summary>지난 기록 <b>{board?.queue.history.length ?? 0}</b></summary>
            {board?.queue.history.map((c) => (
              <div key={`${c.source}-${c.id}`} className="hist-row"><time>{c.time}</time><span>{c.text}{c.done ? ` · ${c.done}` : ""}</span></div>
            ))}
          </details>
        </div>
      </aside>
    </div>
  );
}
```

`modules/cop-ui/src/features/board/board.css` (배치만):

```css
/* Live board layout (Part1-32). Colors and type live in theme.css ("Live board" section). */
.header-slot { display: flex; flex: 1; align-items: center; gap: 16px; min-width: 0; padding-left: 24px; }
.header-slot .situation { display: flex; align-items: center; gap: 12px; margin: 0 auto; white-space: nowrap; }
.header-slot .situation .c { display: flex; align-items: baseline; gap: 5px; }
.header-slot .situation .sep { width: 1px; height: 18px; }
.header-slot .situation .c.dec { padding: 3px 10px; }
.header-slot .loadbar { display: flex; align-items: center; gap: 8px; }
.header-slot .loadbar span { display: flex; align-items: center; gap: 6px; }
.header-slot .status { margin: 0; }
.layout.board { grid-template-columns: 236px 1fr 384px; }
.board .roster { display: flex; flex-direction: column; overflow: hidden; padding: 12px 10px 12px 12px; }
.board .roster h3 { display: flex; align-items: baseline; gap: 8px; margin: 0 0 6px; }
.board .roster h3 small { margin-left: auto; }
.board .roster h3.en { margin-top: 16px; }
.board .ro { display: block; width: 100%; padding: 7px 4px 7px 10px; text-align: left; cursor: pointer; }
.board .ro .l1, .board .ro .l2 { display: flex; align-items: center; gap: 7px; min-width: 0; }
.board .ro .l2 { margin-top: 3px; white-space: nowrap; }
.board .ro .doing, .board .ro .kind, .board .ro .det { min-width: 0; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.board .ro .chip, .board .ro .stg, .board .ro .tgt { flex: none; padding: 0 5px; }
.board .ro .tgt { padding: 0; }
.board .ro .bat { position: relative; flex: none; width: 32px; height: 5px; margin-left: auto; }
.board .ro .bat i, .board .ro .rbar i { position: absolute; inset: 0 auto 0 0; }
.board .ro em { flex: none; width: 34px; font-style: normal; text-align: right; }
.board .ro .risk { margin-left: auto; }
.board .ro .rf { padding: 0 4px; }
.board .ro .rbar { position: relative; display: block; height: 3px; margin-top: 5px; }
.board .ro .rbar::after { content: ""; position: absolute; left: 40%; top: -2px; bottom: -2px; width: 1px; }
.board .ops { display: flex; flex-direction: column; min-height: 0; padding: 0; overflow: hidden; }
.board .ops-scroll { flex: 1; min-height: 0; overflow-y: auto; padding: 12px 14px 8px; }
.board .sec { display: flex; align-items: baseline; gap: 8px; margin: 2px 0 8px; }
.board .sec b { padding: 0 6px; }
.board .sec .ord { margin-left: auto; }
.board .card { position: relative; margin-bottom: 10px; padding: 12px 13px 13px; }
.board .card.first::after { content: "지금"; position: absolute; right: -1px; top: -1px; padding: 1px 7px; }
.board .card .head { display: flex; align-items: baseline; gap: 7px; }
.board .card .head time { margin-left: auto; }
.board .card .text { margin-top: 4px; }
.board .card .hint { margin-top: 7px; padding-left: 8px; }
.board .card .threat { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 12px; margin-top: 7px; }
.board .card .threat span { white-space: nowrap; }
.board .card .q { margin: 10px 0 4px; }
.board .wide { display: flex; flex-direction: column; align-items: flex-start; gap: 3px; width: 100%; margin-top: 6px; padding: 8px 11px; text-align: left; cursor: pointer; }
.board .settle { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.board .reqs { margin: 12px 0 2px; }
.board .grp { display: grid; grid-template-columns: 1fr auto; align-items: center; gap: 6px; padding: 6px 0; }
.board .grp .vs { display: flex; gap: 4px; }
.board .vbtn { display: flex; flex-direction: column; align-items: center; min-width: 52px; padding: 4px 6px; cursor: pointer; }
.board .selrow { display: grid; grid-template-columns: 50px 1fr; align-items: center; gap: 6px; padding: 6px 0; }
.board .selrow .who small { display: block; }
.board .tchips { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; }
.board .tchip { position: relative; display: flex; flex-direction: column; align-items: flex-start; gap: 1px; padding: 5px 6px; text-align: left; cursor: pointer; }
.board .tchip em { font-style: normal; }
.board .tchip.top::after { content: "최고"; position: absolute; right: 3px; top: -8px; padding: 0 4px; }
.board .qrow { display: flex; align-items: baseline; gap: 8px; width: 100%; padding: 10px 8px 10px 10px; text-align: left; cursor: pointer; }
.board .qrow .who { flex: 1; min-width: 0; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.board .next-act { margin-bottom: 14px; padding: 11px 13px; }
.board .alert { display: grid; grid-template-columns: 1fr auto; gap: 2px 8px; margin-bottom: 6px; padding: 8px 10px; }
.board .alert .why { grid-column: 1 / -1; }
.board .graph-open { margin-top: 8px; padding: 6px 10px; cursor: pointer; }
.board .folds { flex: none; }
.board .fold summary { display: flex; align-items: center; gap: 8px; padding: 10px 14px; list-style: none; cursor: pointer; }
.board .fold summary small { overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.board .fold summary b { margin-left: auto; }
.board .fold > :not(summary) { margin: 0 14px 12px; }
.board .fold.hist { max-height: 220px; overflow-y: auto; }
.board .hist-row { display: flex; gap: 8px; padding: 3px 14px; }
```

`modules/cop-ui/src/theme.css` 끝에 (색·글꼴):

```css
/* Live board (Part1-32): white = your turn, yellow/amber/red = risk only, cyan = ours, green = system. Type floor 11px. */
.header-slot .situation .lbl { color: var(--text2); font-size: 13px; font-weight: 600; }
.header-slot .situation .c { color: var(--text2); font-size: 13px; }
.header-slot .situation .c b { font-family: var(--font-mono); font-size: 15px; }
.header-slot .situation .c.ask, .header-slot .situation .c.strike { color: var(--hostile); }
.header-slot .situation .c.track { color: var(--friend); }
.header-slot .situation .c.found { color: var(--warn); }
.header-slot .situation .c.rf { color: var(--hostile); }
.header-slot .situation .c.lost { color: var(--text2); }
.header-slot .situation .c.never, .header-slot .situation .c.gone { color: var(--muted); }
.header-slot .situation .sep { background: var(--line2); }
.header-slot .situation .c.dec { border: 1px solid var(--text); background: var(--text); color: var(--bg); }
.header-slot .situation .c.dec.none { border-color: var(--line2); background: none; color: var(--muted); }
.header-slot .loadbar b { font-family: var(--font-mono); font-size: 22px; color: var(--text); }
.header-slot .loadbar .op b { color: var(--live); }
.header-slot .loadbar small { color: var(--muted); font-size: 11px; line-height: 1.25; }
.header-slot .loadbar .vs { color: var(--dim); font-family: var(--font-mono); font-size: 11px; }
.board aside { background-image: none; }
.board .roster { background-color: var(--s1); border-right: 1px solid var(--line); }
.board .roster h3 { color: var(--muted); font-size: 12px; font-weight: 600; }
.board .roster h3 b { color: var(--text); font-size: 14px; }
.board .roster h3 small { font-size: 12px; }
.board .ro { border: 0; border-bottom: 1px solid var(--line); border-left: 3px solid var(--friend); background: transparent; color: var(--text); font-family: var(--font); }
.board .ro:hover, .board .ro.sel { background: var(--s2); }
.board .ro.sel { border-left-color: var(--live); }
.board .ro.st-returning { border-left-color: var(--warn); }
.board .ro.st-ready, .board .ro.st-maintenance { border-left-color: var(--line2); }
.board .ro .l1 b { font-family: var(--font-mono); font-size: 14px; }
.board .ro .doing { color: var(--text2); font-size: 13px; }
.board .ro.st-ready .doing, .board .ro.st-maintenance .doing { color: var(--muted); }
.board .ro .l2 { color: var(--muted); font-size: 12px; }
.board .ro .tgt { color: var(--friend); font-family: var(--font-mono); }
.board .ro .tgt.strike { color: var(--hostile); }
.board .ro .chip { border: 1px solid var(--text); color: var(--text); font-size: 11px; }
.board .ro .bat { background: var(--s3); }
.board .ro .bat i { background: var(--friend); }
.board .ro .bat.low i { background: var(--warn); }
.board .ro em { font-family: var(--font-mono); font-size: 11px; }
.board .ro em.low { color: var(--warn); }
.board .ro.en { border-left-color: var(--unknown); }
.board .ro.en.mid { border-left-color: var(--warn); }
.board .ro.en.hi { border-left-color: var(--hostile); }
.board .ro.en.gone, .board .ro.en.never { border-left: 3px dotted var(--line2); opacity: 0.6; }
.board .ro .risk { font-family: var(--font-mono); font-size: 14px; font-weight: 700; }
.board .ro.en.lo .risk { color: var(--unknown); } .board .ro.en.mid .risk { color: var(--warn); } .board .ro.en.hi .risk { color: var(--hostile); }
.board .ro .rf { background: var(--hostile); color: var(--bg); font-family: var(--font-mono); font-size: 10px; font-weight: 700; }
.board .ro .stg { border: 1px solid var(--line2); color: var(--text2); font-size: 11px; }
.board .ro .stg.ask, .board .ro .stg.strike, .board .ro .stg.rf, .board .ro .stg.lost.away { border-color: var(--hostile); color: var(--hostile); }
.board .ro .stg.track { border-color: var(--friend); color: var(--friend); }
.board .ro .stg.found { border-color: var(--warn); color: var(--warn); }
.board .ro .stg.lost { border-style: dashed; }
.board .ro .stg.never { border-style: dotted; color: var(--muted); }
.board .ro .rbar { background: var(--s3); }
.board .ro .rbar::after { background: var(--muted); }
.board .ro.en.lo .rbar i { background: var(--unknown); } .board .ro.en.mid .rbar i { background: var(--warn); } .board .ro.en.hi .rbar i { background: var(--hostile); }
.board .ops { background-color: var(--s1); border-left: 1px solid var(--line); }
.board .sec { color: var(--text2); font-size: 13px; font-weight: 600; }
.board .sec b { background: var(--text); color: var(--bg); font-size: 12px; }
.board .sec .ord { color: var(--muted); font-size: 12px; font-weight: 400; }
.board .card { border: 1px solid var(--line); border-left: 3px solid var(--text); background: var(--s2); }
.board .card.first::after { background: var(--text); color: var(--bg); font-size: 11px; font-weight: 700; }
.board .card.t-danger, .board .card.t-block { border-left-color: var(--hostile); }
.board .card.t-danger.first::after, .board .card.t-block.first::after { background: var(--hostile); }
.board .card.t-block { background: linear-gradient(90deg, var(--hostile-soft), transparent 60%), var(--s2); }
.board .card .head b { color: var(--text); font-size: 15px; }
.board .card .head .tid { font-family: var(--font-mono); font-size: 15px; font-weight: 700; }
.board .card .head time { color: var(--muted); font-family: var(--font-mono); font-size: 11px; }
.board .card .text { color: var(--muted); font-size: 13px; line-height: 1.45; }
.board .card .hint { border-left: 2px solid var(--line2); color: var(--text2); font-size: 13px; line-height: 1.45; }
.board .card .threat { font-family: var(--font-mono); font-size: 12px; }
.board .card .threat .sc { font-size: 14px; font-weight: 700; }
.board .card .threat .sc.lo { color: var(--unknown); } .board .card .threat .sc.mid { color: var(--warn); } .board .card .threat .sc.hi { color: var(--hostile); }
.board .card .threat .why { color: var(--muted); }
.board .card .q { color: var(--text); font-size: 14px; font-weight: 700; }
.board .wide { border: 1px solid var(--line2); background: transparent; color: var(--text2); font-family: var(--font); font-size: 14px; font-weight: 600; }
.board .wide small { color: var(--muted); font-family: var(--font-mono); font-size: 11px; font-weight: 500; }
.board .wide.pri, .board .wide.go { border-color: var(--text); background: var(--text); color: var(--bg); font-weight: 700; }
.board .wide.pri small, .board .wide.go small { color: var(--s3); }
.board .wide.strike { border-color: var(--hostile); background: var(--hostile); color: var(--bg); font-weight: 700; }
.board .wide.strike small { color: var(--s1); }
.board .wide.strike2 { border-color: var(--hostile); color: var(--hostile); }
.board .wide:hover:not(:disabled) { border-color: var(--live); }
.board .wide:disabled, .board .vbtn:disabled, .board .tchip:disabled { opacity: 0.45; cursor: default; }
.board .reqs { color: var(--muted); font-size: 12px; font-weight: 600; }
.board .grp { border-top: 1px solid var(--line); }
.board .grp .gl { color: var(--text2); font-size: 13px; }
.board .vbtn { border: 1px solid var(--text); background: var(--text); color: var(--bg); font-family: var(--font-mono); font-size: 13px; font-weight: 700; }
.board .vbtn small { font-size: 11px; font-weight: 500; opacity: 0.7; }
.board .vbtn.low { border-color: var(--warn); background: transparent; color: var(--warn); }
.board .vbtn:hover:not(:disabled), .board .tchip:hover:not(:disabled) { border-color: var(--live); background: var(--live); color: var(--bg); }
.board .selrow { border-top: 1px solid var(--line); }
.board .selrow .who { font-family: var(--font-mono); font-size: 13px; font-weight: 700; }
.board .selrow .who small { color: var(--muted); font-size: 11px; font-weight: 500; }
.board .tchip { border: 1px solid var(--line2); background: transparent; color: var(--text); font-family: var(--font-mono); font-size: 12px; font-weight: 700; }
.board .tchip.lo em { color: var(--unknown); } .board .tchip.mid em { color: var(--warn); } .board .tchip.hi em { color: var(--hostile); }
.board .tchip.top { border-color: var(--hostile); background: var(--hostile-soft); }
.board .tchip.top::after { background: var(--hostile); color: var(--bg); font-family: var(--font); font-size: 10px; }
.board .qrow { border: 0; border-bottom: 1px solid var(--line); border-left: 3px solid var(--text); background: transparent; color: var(--text2); font-family: var(--font); font-size: 13px; }
.board .qrow.t-danger { border-left-color: var(--hostile); }
.board .qrow:hover { background: var(--s2); }
.board .qrow b { color: var(--text); font-family: var(--font-mono); font-size: 14px; }
.board .qrow .sc { font-family: var(--font-mono); font-size: 13px; font-weight: 700; }
.board .qrow .sc.lo { color: var(--unknown); } .board .qrow .sc.mid { color: var(--warn); } .board .qrow .sc.hi { color: var(--hostile); }
.board .qrow time { color: var(--muted); font-family: var(--font-mono); font-size: 11px; }
.board .qrow .go { color: var(--muted); }
.board .next-act { border: 1px solid var(--line2); background: var(--s2); }
.board .next-act .k { color: var(--muted); font-size: 12px; font-weight: 600; }
.board .next-act .t { margin-top: 4px; color: var(--text); font-size: 16px; font-weight: 700; }
.board .next-act .s { margin-top: 3px; color: var(--text2); font-size: 13px; }
.board .next-act.done { border-color: var(--live); background: linear-gradient(90deg, var(--live-soft), transparent 70%), var(--s2); }
.board .next-act.done .k { color: var(--live); }
.board .alert { border: 1px solid var(--line); background: var(--s2); color: var(--text2); font-size: 13px; }
.board .alert time { color: var(--muted); font-family: var(--font-mono); font-size: 11px; }
.board .alert .why { color: var(--muted); font-family: var(--font-mono); font-size: 12px; }
.board .alert.win { border-color: var(--live); background: linear-gradient(90deg, var(--live-soft), transparent 70%), var(--s2); }
.board .alert.win b { color: var(--text); font-size: 14px; }
.board .alert.blk b { color: var(--hostile); }
.board .graph-open { border: 1px solid var(--line2); background: transparent; color: var(--text2); font-size: 12px; }
.board .folds { border-top: 1px solid var(--line); }
.board .fold { border-bottom: 1px solid var(--line); }
.board .fold summary { color: var(--text2); font-size: 14px; font-weight: 600; }
.board .fold summary::before { content: "▸"; color: var(--muted); }
.board .fold[open] summary::before { content: "▾"; }
.board .fold summary small { color: var(--muted); font-size: 12px; font-weight: 500; }
.board .fold summary b { color: var(--muted); font-family: var(--font-mono); font-size: 12px; }
.board .fold .switchpanel::before { content: none; }
.board .hist-row { color: var(--muted); font-size: 12px; }
.board .hist-row time { font-family: var(--font-mono); }
```

- [ ] **Step 6: 타입·테스트·화면 확인**

Run: `cd modules/cop-ui && npx tsc -b && npm test`
Expected: 오류 없음, 전부 PASS.

`scripts/dev.sh`가 도는 상태에서 브라우저 `http://localhost:5173/#live` 와 `?scene=s1`~`s8` 을 1366×768로 열어 본다: 오른쪽에 결정 대기 한 장만 펼침, 머리에 개수·운용자 조작·LIVE, 왼쪽에 아군 6·적 목록, 스크롤 없음.

- [ ] **Step 7: 화면 점검 갱신**

`scripts/qa/live.json`에서 다음을 바꾼다(나머지 단계는 그대로):
- L2 단계 전체를 (결정 0046 흐름: 17:05에 boat1·boat2 카드, 위험이 높은 boat1이 펼쳐짐):

```json
 {"label": "L2 next event stops at 17:05 with boat1's card open, its planned choice first (decision 0046)", "eval": "({ clock: document.querySelector('.runbar .clock')?.innerText, play: document.querySelector('.runbar .play')?.innerText, open: document.querySelector('.card .head')?.innerText.replace(/\\n/g, ' '), first: document.querySelector('.card .wide')?.innerText.split('\\n')[0], rows: document.querySelectorAll('.qrow').length })", "match": "T\\+17:05.*▶ 재생.*표적 발견 boat1.*근접 확인.*\"rows\":1"},
```

- L2b: `{"label": "L2b boat1's card shows its observed risk", "eval": "document.querySelector('.card .threat .sc')?.innerText", "expect": "위험 0.50"}`.
- L3 클릭: `{"click": "d3 → 발생 지역 순찰", "wait": 800}` 를 `{"clickSel": ".card .grp .vbtn", "wait": 800}` 로(첫 이어받기 줄의 첫 기체 d3).
- L4 단계 전체를:

```json
 {"label": "L4 card resolved, vehicles moved, operator count 1", "eval": "(() => { const now = Object.fromEntries([...document.querySelectorAll('.mk.vehicle')].map(i => [i.querySelector('span').innerText, i.parentElement.style.transform])); return { resolved: ![...document.querySelectorAll('.card .head, .qrow')].some(e => e.innerText.includes('boat1') && e.innerText.includes('d1')), moved: Object.keys(now).filter(k => now[k] !== window.__before[k]).sort(), operator: document.querySelector('.loadbar .op b')?.innerText }; })()", "expect": {"resolved": true, "moved": ["d1", "d2", "d3"], "operator": "1"}},
```

  (`moved`는 실제 실행 결과에 맞춘다: d1은 배 위 선회, d2는 순찰, d3는 출발. 다르면 그 실행의 값으로 고치고 이유를 커밋 메시지에 적는다.)
- L6 차단 카드: `"eval": "[...document.querySelectorAll('.card.t-block')].map(c => c.innerText.replace(/\\n/g, ' | '))"`, `"match": "명령 차단 · 작전 구역 밖 .*대안 지점으로"`. 대안 보내기·확인 단계의 `x.innerText.includes('BLOCKED')` 를 `x.classList.contains('t-block')` 로. "L6 the alternative is not blocked"는 `document.querySelectorAll('.card.t-block, .alert.blk').length` 와 `"expect": 1`.
- L7 전환 요청 앞에 `{"clickSel": ".fold.switch summary", "wait": 300}` 추가. "L7 pending card": `c.innerText.includes('전환 승인')` 로 찾고 `"match": "전환 승인 · .*d2→track_fast.*승인.*거부"`. "L7 switch approved": `"eval": "[...document.querySelectorAll('.fold.hist .hist-row')].some(r => r.innerText.includes('승인됨'))"`, `"expect": true` (앞에 `{"clickSel": ".fold.hist summary", "wait": 300}`).
- L11: `"eval": "document.querySelector('.loadbar')?.innerText.replace(/\\n/g, ' ')"`, `"match": "운용자"`.
- `.direct-hint`, `.mk.vehicle`, `.mk.aim`, `.runbar`, `.status` 단계는 그대로.

Run: `scripts/qa.sh scripts/qa/live.json` → `[qa] 전부 통과`. 스크린샷 `logs/qa/live-contact.png`·`live-end-1366.png`를 열어 넘침·겹침이 없는지 본다.

- [ ] **Step 8: SPEC 행, commit, ship**

`modules/cop-ui/SPEC.md`: UI-21 CardList와 UI-28 MetricsPanel 행의 상태를 `폐기(Part1-32, DecisionQueue·LoadBar로 대체)`로, 끝에:

```
| UI-64 | boardView | Frame, BoardData | {tracks, stages, queue, situation, rows} | 데이터가 오기 전(빈 목록)에도 그려짐 | 리드 | 완료 |
| UI-67 | SituationBar·LoadBar | Situation / Metrics | 머리 한 줄 | 앱 머리 자리(#header-slot)에 단계별 개수·결정 대기(흰색)·운용자 조작 대 수동 기준(나머지는 툴팁)·LIVE | 리드 | 완료 |
| UI-68 | RosterPanel | VehicleRow[], Target[], Stage | 왼쪽 열 | 아군 줄(하는 일·표적·배터리·결정 대기), 적 줄 위험도 순(무력화·미탐 아래), 단계 표시, 줄 누르면 기체 선택 | 리드 | 완료 |
| UI-69 | DecisionQueue·QueueCard | Frame, Queue | 오른쪽 열 | 한 장 펼침(나머지 한 줄), 정해진 선택지 먼저·드론 요청 묶음, 표적 선택 위험도 순 칩, 타격 빨강, 승인·거부, 대안 지점, 보내기 잠금(UI-20), 결정 없으면 할 일 없음·무력화 결과, 알림 2분 | 리드 | 완료 |
```

```bash
git add modules/cop-ui scripts/qa/live.json
git commit -m "Part1-32: live board layout: header counts and operator load, vehicles and targets on the left, decision queue with one open item on the right, switch panel and history folded"
scripts/ship.sh
```

---

### Task 7: 지도 — 탐지 상태 마커, 선·원, 카메라 (frameMarkers·markers·MapView)

**Files:**
- Modify: `modules/cop-ui/src/features/map/frameMarkers.ts`, `frameMarkers.test.ts`
- Modify: `modules/cop-ui/src/features/map/markers.ts`
- Modify: `modules/cop-ui/src/features/map/MapView.tsx`
- Modify: `modules/cop-ui/src/Screen.tsx` (MapView에 board·watch 넘김)
- Modify: `modules/cop-ui/src/theme.css` (지도 구역), `modules/cop-ui/SPEC.md` (UI-07 행 갱신)

**Interfaces:**
- Consumes: `Track`, `BoardView`, `linkLines`, `watchCircles`, `cameraPoints`.
- Produces: `frameMarkers(frame: Frame, tracks?: Record<string, Track>)` → `TargetMarker`에 `track: TrackKind`, `tone: "hi" | "mid" | "lo"` 추가, `VehicleMarker`에 `label: string` 추가; `MapView` props에 `board?: BoardView | null`, `watch?: WatchPoint[]`.

- [ ] **Step 1: 실패 테스트 — 이름표와 위치**

`modules/cop-ui/src/features/map/frameMarkers.test.ts` 첫 테스트의 `expect(vehicles[0]).toEqual(...)` 를 `toEqual({ id: "d1", lon: 124.695, lat: 37.98, status: "active", label: "d1" })` 로 바꾸고, 세 번째 테스트 기대값에 `track: "seen", tone: "lo"` 를 더한다. 파일 끝 `});` 앞에 추가:

```ts
  it("draws a target where our side knows it and says its risk, lost time and direction (decision 0047)", () => {
    const f = s1 as Frame;
    const t = { ...f.targets[0], threat: 72, seen_by: [], first_seen_ms: f.t_ms - 60_000, last_seen_ms: f.t_ms - 20_000 };
    const tracks = { boat1: { k: "lost" as const, pos: { lat: 37.98, lon: 124.71 }, agoMs: 20_000, dir: "away" as const, speed: 6.3 } };
    expect(frameMarkers({ ...f, targets: [t] }, tracks).targets[0]).toMatchObject({
      lon: 124.71, lat: 37.98, track: "lost", tone: "hi", label: "boat1 0.72 · 놓침 0:20 · 이탈(도주) 추정",
    });
    const never = { boat1: { k: "never" as const, pos: t.pos } };
    expect(frameMarkers({ ...f, targets: [t] }, never).targets[0]).toMatchObject({ track: "never", label: "boat1 · 미탐" });
  });

  it("names a vehicle with its battery when it runs low", () => {
    const f = s1 as Frame;
    const low = { ...f, vehicles: [{ ...f.vehicles[0], battery_pct: 29.4 }] };
    expect(frameMarkers(low).vehicles[0].label).toBe("d1 29%");
  });
```

Run: `cd modules/cop-ui && npx vitest run src/features/map/frameMarkers.test.ts` → FAIL

- [ ] **Step 2: 구현 — frameMarkers**

`modules/cop-ui/src/features/map/frameMarkers.ts` 전체:

```ts
import type { Frame, TargetKind, VehicleStatus } from "../../contracts.gen";
import type { Track, TrackKind } from "../board/trackState";
import { mmss } from "../run/mmss";

export interface VehicleMarker { id: string; lon: number; lat: number; status: VehicleStatus; label: string }
export interface TargetMarker {
  id: string; kind: TargetKind; lon: number; lat: number; seen: boolean; neutralized: boolean; rf: boolean;
  track: TrackKind; tone: "hi" | "mid" | "lo"; label: string;
}

const LOW_PCT = 35;
const DIR_KO = { still: "정지", approach: "접근 추정", away: "이탈(도주) 추정" } as const;
const tone = (r: number) => (r >= 0.7 ? "hi" : r >= 0.4 ? "mid" : "lo");

// Frame → what the map draws as HTML markers (offline there are no glyphs, so labels cannot be map layers).
// Targets sit where our side knows them (decision 0047: a lost one at its last seen spot, from tracks) and say
// their risk; a never-detected one says "미탐" without a risk; a struck one is "<id> · 무력화" (Part1-20); RF only
// from rf_detected (decision 0040). Vehicles name their battery when it runs low.
export function frameMarkers(frame: Frame, tracks: Record<string, Track> = {}):
  { vehicles: VehicleMarker[]; targets: TargetMarker[] } {
  return {
    vehicles: frame.vehicles.map((v) => ({ id: v.id, lon: v.pos.lon, lat: v.pos.lat, status: v.status,
      label: v.battery_pct < LOW_PCT ? `${v.id} ${Math.round(v.battery_pct)}%` : v.id })),
    targets: frame.targets.map((t) => {
      const tr = tracks[t.id];
      const neutralized = t.neutralized_ms != null;
      const k: TrackKind = tr?.k ?? (neutralized ? "gone" : (t.seen_by ?? []).length ? "seen" : "never");
      const rf = !neutralized && t.rf_detected === true;
      const r = (t.threat ?? 0) / 100;
      const score = r > 0 ? ` ${r.toFixed(2)}` : "";
      const label = neutralized ? `${t.id} · 무력화` : k === "never" && tr ? `${t.id} · 미탐`
        : k === "lost" && tr ? `${t.id}${score} · 놓침 ${mmss(tr.agoMs ?? 0)} · ${DIR_KO[tr.dir ?? "still"]}`
        : `${t.id}${score}${rf ? " · RF" : ""}`;
      const pos = tr?.pos ?? t.pos;
      return { id: t.id, kind: t.kind, lon: pos.lon, lat: pos.lat, seen: (t.seen_by ?? []).length > 0, neutralized, rf,
        track: k, tone: tone(r), label };
    }),
  };
}
```

(예시 Frame의 boat1 위험도가 0이면 이름표는 지금처럼 "boat1"이라 기존 테스트가 그대로 통과한다.)

Run: `cd modules/cop-ui && npx vitest run src/features/map/frameMarkers.test.ts` → PASS

- [ ] **Step 3: markers.ts 클래스, 표적 클릭**

`modules/cop-ui/src/features/map/markers.ts`의 `syncVehicles`는 그대로(라벨은 `item.label`을 이미 씀). `syncTargets`를:

```ts
export function syncTargets(map: MapLibreMap, store: MarkerStore, items: TargetMarker[], onClick?: (id: string) => void): void {
  sync(map, store, items,
    (t) => `mk target ${t.kind} ${t.track} ${t.tone}${t.seen ? "" : " unseen"}${t.neutralized ? " neutralized" : ""}${t.rf ? " rf" : ""}`,
    onClick);
}
```

- [ ] **Step 4: MapView — 선·원 레이어, 카메라, 표적 위치**

`modules/cop-ui/src/features/map/MapView.tsx`:
- import 추가: `import type { WatchPoint } from "../../contracts.gen";`, `import { LngLatBounds } from "maplibre-gl";`(기존 import 줄에 합침), `import type { BoardView } from "../board/boardView";`, `import { cameraPoints } from "../board/cameraPoints";`, `import { linkLines } from "../board/linkLines";`, `import { watchCircles } from "../board/watchCircles";`.
- 서명: `export function MapView({ frame, zone, tilesAvailable, direct = NO_DIRECT, board = null, watch = [] }: { frame: Frame | null; zone: Polygon | null; tilesAvailable: boolean; direct?: DirectProps; board?: BoardView | null; watch?: WatchPoint[] })`, `latest` ref에 `board, watch` 추가하고 첫 effect에서 `latest.current.board = board; latest.current.watch = watch;`.
- `draw`에서 `frameMarkers(f)` 를 `frameMarkers(f, latest.current.board?.tracks)` 로, 그리고 끝에:

```ts
    const b = latest.current.board;
    const empty = { type: "FeatureCollection" as const, features: [] };
    (m.getSource("links") as GeoJSONSource | undefined)?.setData(f && b ? linkLines(f, b.tracks, b.queue) : empty);
    (m.getSource("watch") as GeoJSONSource | undefined)?.setData(watchCircles(latest.current.watch));
```

- `load` 안 zone 레이어 다음에 (색은 theme 토큰과 같은 값, 지도 paint는 CSS 변수를 못 읽음 — 기존 zone 주석과 같은 방식):

```ts
      m.addSource("watch", { type: "geojson", data: watchCircles(latest.current.watch) });
      // Expected landing radius: --warn, outline only.
      m.addLayer({ id: "watch-line", type: "line", source: "watch", paint: { "line-color": "#f59e0b", "line-opacity": 0.4, "line-width": 1, "line-dasharray": [2, 2] } });
      m.addSource("links", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      // Vehicle → target (--friend dashed), strike (--hostile solid), lost estimate (--warn dotted), alternative (--live dashed).
      m.addLayer({ id: "link-watch", type: "line", source: "links", filter: ["==", ["get", "k"], "watch"], paint: { "line-color": "#80e0ff", "line-width": 1.6, "line-opacity": 0.85, "line-dasharray": [2, 2] } });
      m.addLayer({ id: "link-strike", type: "line", source: "links", filter: ["==", ["get", "k"], "strike"], paint: { "line-color": "#ef4444", "line-width": 2.5 } });
      m.addLayer({ id: "link-est", type: "line", source: "links", filter: ["==", ["get", "k"], "est"], paint: { "line-color": "#f59e0b", "line-width": 1.5, "line-dasharray": [1, 2] } });
      m.addLayer({ id: "link-alt", type: "line", source: "links", filter: ["==", ["get", "k"], "alt"], paint: { "line-color": "#4ade80", "line-width": 1.8, "line-dasharray": [3, 2] } });
      draw(m);
```

- 카메라: 컴포넌트 안에 `const lastKey = useRef("");` 와 effect 추가:

```ts
  useEffect(() => {
    // Camera follows the open decisions (Part1-32): refit only when the set of open items changes, never per frame.
    const m = map.current;
    if (!m || !frame || !board) return;
    const key = board.queue.action.map((i) => i.key).join("|");
    if (key === lastKey.current) return;
    lastKey.current = key;
    const pts = cameraPoints(frame, board.tracks, board.queue);
    if (pts.length === 0) return;
    const bounds = new LngLatBounds();
    pts.forEach((p) => bounds.extend([p.lon, p.lat]));
    m.fitBounds(bounds, { padding: { top: 60, bottom: 40, left: 60, right: 60 }, maxZoom: 13.4, duration: 700 });
  }, [frame, board]);
```

- 그리기 effect의 의존성에 `board` 추가: `}, [frame, board, direct.selected, direct.pending]);`

`modules/cop-ui/src/Screen.tsx`의 MapView 줄을 `<MapView frame={frame} zone={zone} tilesAvailable={tiles} direct={direct} board={board} watch={data.watch} />` 로.

- [ ] **Step 5: 지도 색 (theme.css 끝)**

```css
/* Map (Part1-32): target color = risk tone, lost = dashed outline at the last seen spot, never = faded dotted,
   vehicle names hang left and target names right so a vehicle on its target never covers the label. */
.mk.vehicle span { left: auto; right: 17px; }
.mk.target span { top: 50%; bottom: auto; left: 17px; transform: translateY(-50%); }
.target.lo i { background: var(--unknown); }
.target.mid i { background: var(--warn); box-shadow: 0 0 10px rgba(245, 158, 11, 0.55); }
.target.hi i { background: var(--hostile); box-shadow: 0 0 12px rgba(239, 68, 68, 0.65); }
.target.lost i { background: transparent; border: 2px dashed var(--text2); box-shadow: none; }
.target.lost.hi i { border-color: var(--hostile); } .target.lost.mid i { border-color: var(--warn); }
.target.lost span { border-style: dashed; }
.target.never { opacity: 0.45; }
.target.never i { background: none; border: 1.5px dotted var(--text2); box-shadow: none; }
.target.never span { border-style: dotted; color: var(--text2); }
```

- [ ] **Step 6: 확인, SPEC, commit, ship**

Run: `cd modules/cop-ui && npx tsc -b && npm test` → PASS. `scripts/qa.sh scripts/qa/live.json` → 통과(L5 "every vehicle dot is on top" 포함). 스크린샷에서 선·이름표 겹침 확인.

`modules/cop-ui/SPEC.md` UI-07 행 완료 기준 끝에 `, 표적 위치·이름표는 탐지 상태(놓침 마지막 위치·경과·방향, 미탐 흐리게, 위험도 숫자), 배터리 35% 미만 기체 이름표에 %(Part1-32)` 를 덧붙인다.

```bash
git add modules/cop-ui
git commit -m "Part1-32: map draws targets where we know them (lost, never), risk tones, vehicle-target lines, landing ring, camera on open decisions"
scripts/ship.sh
```

---

### Task 8: 표적 지목 — 기체 선택 → 표적 → 플레이 (useDirectControl·PointMenu, UI-70)

**Files:**
- Modify: `modules/cop-ui/src/features/map/useDirectControl.ts`
- Modify: `modules/cop-ui/src/features/map/MapView.tsx` (표적 클릭 → 위치)
- Create: `modules/cop-ui/src/features/board/PointMenu.tsx`
- Modify: `modules/cop-ui/src/Screen.tsx`, `modules/cop-ui/src/features/board/board.css`, `modules/cop-ui/src/theme.css`
- Modify: `scripts/qa/live.json`, `modules/cop-ui/SPEC.md`

**Interfaces:**
- Consumes: `targetPlays`, `postPoint`, `BoardData`.
- Produces: `DirectProps`에 `pick: { target: string; x: number; y: number } | null`, `onTargetClick(id: string, x: number, y: number): void`, `onPoint(play: string): void`, `cancelPick(): void`; `PointMenu({ vehicle, target, x, y, plays, current, onPick, onCancel })`.

- [ ] **Step 1: useDirectControl 확장**

`modules/cop-ui/src/features/map/useDirectControl.ts`:
- import 추가: `import { postPoint } from "../board/postPoint";`
- `DirectProps`(MapView.tsx)에 칸 추가:

```ts
export interface DirectProps {
  selected: string | null;
  pending: PendingAim | null;
  pick: { target: string; x: number; y: number } | null; // a target pointed at with a vehicle selected (decision 0048)
  onVehicleClick: (id: string) => void;
  onMapClick: (p: GeoPoint) => void;
  onTargetClick: (id: string, x: number, y: number) => void;
  onPoint: (play: string) => void;
  cancelPick: () => void;
}
const NO_DIRECT: DirectProps = { selected: null, pending: null, pick: null, onVehicleClick: () => {}, onMapClick: () => {},
  onTargetClick: () => {}, onPoint: () => {}, cancelPick: () => {} };
```

- hook 안:

```ts
  const [pick, setPick] = useState<{ target: string; x: number; y: number } | null>(null);
```

Escape 처리에서 `setSelected(null)` 옆에 `setPick(null)`. `onVehicleClick`에 `setPick(null);` 추가. `onMapClick` 맨 앞에 `if (pick) return setPick(null);`(메뉴가 열린 채 지도를 누르면 메뉴만 닫힘). 추가 함수:

```ts
  const onTargetClick = (id: string, x: number, y: number) => {
    if (selected) setPick({ target: id, x, y });
  };
  const cancelPick = () => setPick(null);
  const onPoint = async (play: string) => {
    if (!selected || !pick) return;
    const v = selected, t = pick.target;
    setSelected(null);
    setPick(null);
    setStatus({ text: `${v} → ${t} 지목 보내는 중`, sentAt: frameT });
    const r = await postPoint(v, play, t);
    setStatus(r.ok ? { text: `지목 ${r.id} · ${v} → ${t}`, sentAt: frameT } : { text: `보내기 실패: ${r.error}`, sentAt: null });
  };
```

hint를:

```ts
  const hint = selected
    ? pick ? `${selected} → ${pick.target} · 플레이를 고르세요` : `${selected} 선택 · 표적을 누르면 붙일 플레이 · 지도를 누르면 그 지점으로 이동 · Esc 취소`
    : shown;
  return { selected, pending, pick, onVehicleClick, onMapClick, onTargetClick, onPoint, cancelPick, hint };
```

- [ ] **Step 2: MapView 표적 클릭**

`MapView.tsx`의 `draw`에서 `syncTargets(m, targets.current, ts);` 를:

```ts
    syncTargets(m, targets.current, ts, onTargetClick);
```

컴포넌트 안 `onVehicleClick` 옆에:

```ts
  // A target click reports where the target sits in the map box, so the play menu opens beside it.
  const onTargetClick = (id: string) => {
    const mk = targets.current.get(id);
    const box = el.current?.getBoundingClientRect();
    const at = mk?.getElement().getBoundingClientRect();
    if (mk && box && at) latest.current.direct.onTargetClick(id, at.left - box.left + at.width / 2, at.top - box.top + at.height / 2);
  };
```

맵 div에 선택 중 표시: `return <div ref={el} className={direct.selected ? "map picking" : "map"} />;`

- [ ] **Step 3: PointMenu**

`modules/cop-ui/src/features/board/PointMenu.tsx`:

```tsx
import type { Play } from "../../contracts.gen";

// Play menu beside a pointed target (decisions 0048, 0049): each button shows what changes (current play →
// new play · target) and pressing it is the approval. No strike here: strikes go through the approval card.
export function PointMenu({ vehicle, target, x, y, plays, current, onPick, onCancel }: {
  vehicle: string; target: string; x: number; y: number; plays: Play[]; current: string;
  onPick: (play: string) => void; onCancel: () => void;
}) {
  return (
    <div className="pickpop" style={{ left: x + 16, top: Math.max(8, y - 20) }}>
      <div className="ph">{vehicle} → {target}</div>
      {plays.length ? plays.map((p) => (
        <button key={p.id} type="button" onClick={() => onPick(p.id)}>{p.name}<small>{current} → {p.name} · 표적 {target}</small></button>
      )) : <div className="pn">{vehicle}가 표적에 쓸 수 있는 플레이가 없습니다.</div>}
      <button type="button" className="x" onClick={onCancel}>취소</button>
      <div className="pn">누르면 바로 바뀝니다. 타격은 여기서 할 수 없고 타격 승인 카드로만.</div>
    </div>
  );
}
```

- [ ] **Step 4: Screen 연결**

`Screen.tsx`에 import `import { PointMenu } from "./features/board/PointMenu";`, `import { targetPlays } from "./features/board/targetPlays";`. `RosterPanel`의 `onTarget={() => {}}` 를 `onTarget={(id) => direct.selected && direct.onTargetClick(id, 220, 120)}` 로(목록에서 지목하면 메뉴는 지도 왼쪽 위). `RunBar` 줄 앞에:

```tsx
        {direct.selected && direct.pick && frame && (() => {
          const v = frame.vehicles.find((x) => x.id === direct.selected);
          const spec = data.vehicles.find((s) => s.id === direct.selected);
          const current = data.plays.find((p) => p.id === v?.play_id)?.name ?? "대기";
          return <PointMenu vehicle={direct.selected} target={direct.pick.target} x={direct.pick.x} y={direct.pick.y}
            plays={spec ? targetPlays(data.plays, spec.domain) : []} current={current}
            onPick={direct.onPoint} onCancel={direct.cancelPick} />;
        })()}
```

`board.css` 끝에:

```css
.board .pickpop { position: absolute; z-index: 5; width: 240px; padding: 10px; }
.board .pickpop button { display: flex; flex-direction: column; align-items: flex-start; gap: 2px; width: 100%; margin-top: 6px; padding: 7px 10px; text-align: left; cursor: pointer; }
.board .pickpop .pn { margin-top: 8px; }
.map.picking .maplibregl-marker:has(> .mk.target) { pointer-events: auto; cursor: crosshair; }
```

`theme.css` 끝에:

```css
.board .pickpop { border: 1px solid var(--text); background: var(--s1); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6); }
.board .pickpop .ph { font-family: var(--font-mono); font-size: 13px; font-weight: 700; }
.board .pickpop button { border: 1px solid var(--text); background: var(--text); color: var(--bg); font-size: 13px; font-weight: 700; }
.board .pickpop button small { color: var(--s3); font-family: var(--font-mono); font-size: 11px; font-weight: 500; }
.board .pickpop button.x { border-color: var(--line2); background: transparent; color: var(--text2); }
.board .pickpop .pn { color: var(--muted); font-size: 11px; line-height: 1.45; }
.map.picking .mk.target:hover i { outline: 2px solid var(--live); outline-offset: 4px; }
```

- [ ] **Step 5: 화면 점검 단계 추가, 확인**

`scripts/qa/live.json`의 L7 단계들 뒤(“L7 switch approved” 다음)에 추가:

```json
 {"label": "L15 mark d3 and boat1", "eval": "(() => { const v = [...document.querySelectorAll('.mk.vehicle')].find(x => x.querySelector('span').innerText.startsWith('d3')); const t = [...document.querySelectorAll('.mk.target')].find(x => x.querySelector('span').innerText.startsWith('boat1')); if (!v || !t) return 'missing'; v.querySelector('i').id = 'qa-d3'; t.querySelector('i').id = 'qa-boat1'; return 'marked'; })()", "expect": "marked"},
 {"clickSel": "#qa-d3", "wait": 400},
 {"clickSel": "#qa-boat1", "wait": 400},
 {"label": "L15 play menu beside boat1 offers target plays, no strike", "eval": "[...document.querySelectorAll('.pickpop button')].map(b => b.innerText.split('\\n')[0])", "match": "^\\[\"표적 감시\".*\"취소\"\\]$"},
 {"label": "L15 no strike in the menu", "eval": "[...document.querySelectorAll('.pickpop button')].some(b => b.innerText.includes('타격'))", "expect": false},
 {"clickSel": ".pickpop button", "wait": 800},
 {"label": "L15 pointing sent, approved by the press", "eval": "document.querySelector('.direct-hint')?.innerText ?? null", "match": "^지목 inj-\\d+ · d3 → boat1$"},
 {"click": "재생", "wait": 2500},
 {"click": "일시정지", "wait": 800},
 {"label": "L15 d3 works boat1", "eval": "[...document.querySelectorAll('.roster .ro')].find(r => r.innerText.startsWith('d3'))?.innerText.replace(/\\n/g, ' ')", "match": "표적 감시 .*→ boat1"}
```

(`.pickpop button`의 첫 버튼은 `targetPlays` 순서상 "표적 감시"다. 화면 점검의 편집기 단계가 저장한 플레이가 메뉴 뒤쪽에 더 붙을 수 있어 메뉴는 앞·뒤만 맞춘다. runtime `apply_injection`이 표적을 기록하기 전(Task 9)에는 마지막 단계 "L15 d3 works boat1"이 실패하므로, 그 한 단계는 Task 9의 apply_injection ship 뒤에 넣는다.)

Run: `cd modules/cop-ui && npx tsc -b && npm test` → PASS, `scripts/qa.sh scripts/qa/live.json` → 통과.

- [ ] **Step 6: SPEC, commit, ship**

```
| UI-70 | PointMenu·지목(useDirectControl) | 선택 기체, 표적 | 플레이 메뉴 | 기체를 고른 동안만 표적이 클릭을 받음, 표적 옆 메뉴에 targetPlays 버튼("지금 → 새 · 표적"), 누르면 postPoint, 빈 지도 클릭은 메뉴만 닫고 다음 클릭은 직접 이동, Esc 취소, 목록 줄로도 지목(결정 0048·0049) | 리드 | 완료 |
```

```bash
git add modules/cop-ui scripts/qa/live.json
git commit -m "Part1-32: point a selected vehicle at a target and press a play (decisions 0048, 0049)"
scripts/ship.sh
```

---

### Task 9: 엔진 세 곳 (담당자 몫 — 동의 뒤 시작)

담당자(최동호: sensing, 황승주: runtime)에게 Task 1 ship 뒤 채팅으로 알리고, 직접 할지 리드가 할지 정한다. 리드가 하면 커밋 뒤 채팅으로 알린다. 각자 자기 worktree에서, 각 항목 하나씩 ship.

**Files:**
- Modify: `modules/sensing/actions/observe_targets.py`, `modules/sensing/tests/test_observe_targets.py`
- Modify: `modules/runtime/actions/fleet_choices.py`, `modules/runtime/tests/test_fleet_choices.py`
- Modify: `modules/runtime/actions/apply_injection.py`, `modules/runtime/tests/test_apply_injection.py`

**Interfaces:**
- Consumes: Task 1 계약 칸.
- Produces: Frame의 `Target.last_seen_pos`·`last_seen_vel_*`가 채워짐; 카드의 함께 감시가 그 카드 드론과만; 지목 전환 뒤 `VehicleState.target_id`가 지목한 표적.

- [ ] **Step 1: sensing — 실패 테스트**

`modules/sensing/tests/test_observe_targets.py` 끝에(파일의 `_target`, `D1`, `SPEC`, `T` 그대로):

```python
def test_records_where_and_how_fast_a_target_was_last_seen():
    # decision 0047: the board draws a lost target at its last seen spot and estimates where it went
    moving = _target(900).model_copy(update={"vel_east_mps": 6.3, "vel_north_mps": 0.5})
    (t,) = observe_targets([D1], {"d1": SPEC}, [moving], T)
    assert (t.last_seen_pos, t.last_seen_vel_east_mps, t.last_seen_vel_north_mps) == (moving.pos, 6.3, 0.5)
    gone = _target(1100).model_copy(update={"last_seen_pos": moving.pos, "last_seen_vel_east_mps": 6.3})
    (t,) = observe_targets([D1], {"d1": SPEC}, [gone], T + 1000)
    assert (t.last_seen_pos, t.last_seen_vel_east_mps) == (moving.pos, 6.3)
```

Run: `uv run pytest modules/sensing -n 0 -k last_seen` → FAIL (`last_seen_pos` None)

- [ ] **Step 2: sensing — 구현**

`modules/sensing/actions/observe_targets.py`의 `if seen:` 블록을:

```python
        if seen:
            upd |= {"last_seen_ms": t_ms, "first_seen_ms": tg.first_seen_ms or t_ms,
                    "last_seen_pos": tg.pos, "last_seen_vel_east_mps": tg.vel_east_mps,
                    "last_seen_vel_north_mps": tg.vel_north_mps}  # fmt: skip
```

Run: `uv run pytest modules/sensing -n 0` → PASS. Commit `"Part1-32: sensing records where and how fast each target was last seen (decision 0047)"`, ship.

- [ ] **Step 3: runtime fleet_choices — 실패 테스트**

`modules/runtime/tests/test_fleet_choices.py`의 `test_join_lists_every_hovering_drone`이 결정 0048로 바뀌는 동작이다. 그 테스트를 다음으로 바꾼다(같은 states, 기대값만 새 규칙):

```python
def test_join_only_with_the_drone_that_raised_the_card():
    # decision 0048: boat1's card does not offer "with d2 on boat2" (it would close boat1's card for a boat2 action)
    states = [vs("d1", "coast_a", "report", target="boat1"), vs("d2", "coast_b", "report", target="boat2"),
              vs("d3", None, None, "ready"), vs("d4", None, None, "maintenance", battery=40)]  # fmt: skip
    rep = fleet_choices(CARD, states, OP, PLAYS)
    assert labels(rep) == ["take_d3", "join_d3_d1", "keep"]
    assert rep.choices[1].target_by_vehicle == {"d3": "boat1"}
```

Run: `uv run pytest modules/runtime -n 0 -k join_only_with` → FAIL (`join_d3_d2`가 들어 있음)

- [ ] **Step 4: runtime fleet_choices — 구현**

`modules/runtime/actions/fleet_choices.py`의 `join = [...]`를:

```python
    join = [
        Choice(id=f"join_{x.id}_{me.id}", label=f"{x.id} → {me.id}와 함께 감시({me.target_id})",
               play_by_vehicle={x.id: WATCH_PLAY}, target_by_vehicle={x.id: me.target_id})
        for x in others
    ] if me.target_id else []  # decision 0048: watch together only with the drone that raised this card
```

모듈 docstring의 `"감시 중인 드론 Y와 함께 감시"(Y마다…)` 를 `"이 카드를 올린 드론과 함께 감시"(결정 0048)` 로. `modules/runtime/SPEC.md` RT-11 완료 기준에 `, 함께 감시는 카드를 올린 드론과만(결정 0048)` 추가.

Run: `uv run pytest modules/runtime modules/gateway -n auto -q` → PASS(타임라인 테스트가 함께 감시를 고르지 않아 장면 시각은 그대로여야 한다; 깨지면 멈추고 담당자와 본다). Commit, ship.

- [ ] **Step 5: runtime apply_injection — 실패 테스트**

`modules/runtime/tests/test_apply_injection.py` 끝에(파일의 `vs` 그대로):

```python
WATCH = Play(id="watch", name="표적 감시", domains=["air"], entry="w1",
             steps=[Step(id="w1", name="w", do=Action(kind="watch_target"))])  # fmt: skip


def test_pointing_switch_records_the_target():
    # decision 0048: the operator pointed d2 at boat1 with a play; the vehicle works that target
    inj = Injection(id="inj2", t_ms=0, label="표적 감시: d2 → boat1", status="approved",
                    play_by_vehicle={"d2": "watch"}, target_by_vehicle={"d2": "boat1"})  # fmt: skip
    (d2,) = apply_injection([vs("d2")], {"watch": WATCH}, inj)
    assert (d2.play_id, d2.step_id, d2.target_id) == ("watch", "w1", "boat1")
```

Run: → FAIL (`target_id` None)

- [ ] **Step 6: runtime apply_injection — 구현**

`modules/runtime/actions/apply_injection.py`의 함수 본문을:

```python
    to, tgt = injection.play_by_vehicle, injection.target_by_vehicle
    out = []
    for s in states:
        if s.id in to:
            s = switch_play(s, plays[to[s.id]])
            if s.id in tgt:  # pointed at a target on the map (decision 0048)
                s = s.model_copy(update={"target_id": tgt[s.id]})
        out.append(s)
    return out
```

Run: `uv run pytest modules/runtime -n 0` → PASS. Commit, ship. 그 뒤 Task 8 Step 5의 "L15 d3 works boat1" 단계를 넣고 화면 점검.

---

### Task 10: 마무리 — 대본 리허설, 기록

**Files:**
- Modify: `modules/cop-ui/src/features/run/runStops.ts`(필요할 때만), `scripts/qa/live.json`, `demo/BUILT_HERE.md`

- [ ] **Step 1: 대본 리허설**

`scripts/dev.sh` 상태에서 `http://localhost:5173/#live` 를 1366×768로 열고 처음으로 → 다음 사건으로 3분 대본(보고 카드 → 드론1 귀환 → 드론2 직접 조종·차단·대안 → 고속정 → 전환 → 표적 선택 → 타격 허락 → 무력화)을 화면 조작만으로 끝까지 돈다. 각 정지에서 오른쪽 맨 위 펼친 카드가 그 장면의 할 일인지 본다. 정지 시각이 장면과 어긋나면 `runStops.ts`의 `RUN_STOPS` 시각을 실제 장면(엔진)에 맞추고 `runStops.test.ts`를 같은 커밋에서 고친다(TDD: 테스트 먼저).

- [ ] **Step 2: BUILT_HERE, 할 일 완료**

`demo/BUILT_HERE.md` 표에 한 줄:

```
| 10/10 | cop-ui·contracts·gateway | 상황판 개편(Part1-32, 결정 0047·0048·0049): 머리에 단계별 적 개수·결정 대기·운용자 조작, 왼쪽 아군·적 목록(하는 일·표적·배터리, 배마다 탐지 상태), 오른쪽 결정 대기열 한 장 펼침(정해진 선택지 먼저·드론 요청 묶음), 지도에 기체→표적 선·위험도 색·놓친 배 마지막 위치와 접근/이탈 추정·미탐 흐리게, 기체 클릭→표적→플레이 지목 | kth9245 |
```

```bash
git add demo/BUILT_HERE.md scripts/qa/live.json modules/cop-ui
git commit -m "Part1-32: board rehearsal fixes and BUILT_HERE line"
scripts/ship.sh
uv run python scripts/task.py done Part1-32
```
