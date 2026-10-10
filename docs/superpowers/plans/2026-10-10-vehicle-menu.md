# 상황판 기체 메뉴 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 상황판에서 기체를 누르면 왼쪽 아군 줄 아래로 메뉴가 펼쳐져 이동·Role 바로 전환·표적 Role(무장 기체는 '표적 타격')을 포착된 적에 바로 지목할 수 있게 하고, '작전 전환' 칸을 없애 '전 기체 귀환'만 아군 머리줄에 둔다.

**Architecture:** runtime `apply_injection`이 표적을 지목한 기체에 `decision_id = injection.id`를 적어 지목 타격이 안전 규칙 1을 통과한다(결정 0058). 화면은 순수 함수 액션 셋(`vehicleMenuRoles`·`seenTargets`·`postRole`)과 데이터 읽기(`fetchBoardData`) 위에, 새 컴포넌트 `VehicleMenu`를 `RosterPanel`의 고른 줄 아래에 그리고 `useDirectControl`이 요청을 보낸다. 요청은 모두 기존 `POST /injections`(approve: true)라 서버·계약 모델 변경은 없다.

**Tech Stack:** Python 3.12·pydantic·pytest(runtime), React 18·TypeScript·Vite·vitest(cop-ui), 화면 점검은 headless Chrome + `scripts/qa/run.mjs`.

**Spec:** `docs/superpowers/specs/2026-10-10-vehicle-menu-design.md` (결정 0058·0059·0060·0061, Part1-32.1 할 일 기록의 22:37·22:53 결정)

## Global Constraints

- 작업은 worktree `/home/kth9245/HACKERTON/KDTH2026/.claude/worktrees/Part1-32.1`에서만. git 명령은 `$(...)`·`cd … &&` 없이 따로 실행한다(worktree 세션이 거부함).
- TDD(결정 0014): 코드 변경마다 실패하는 테스트(화면 연결은 화면 점검 단계)를 먼저 쓰고 실패를 확인한 뒤 구현한다. 문서만 바꾸면 예외.
- 액션 파일: 공개 함수 1개, 이름 = 파일 이름, 80줄 이하. cop-ui는 new_action.py가 없으니 SPEC 행을 손으로 넣는다(다음 번호 UI-97부터).
- happy path만(결정 0024). 시연 대본이 끝까지 돌면 된다. 하한선 규칙 3개(출처·작전 구역·귀환 배터리)는 그대로.
- 화면 글은 한국어, 화면 표기는 Role(결정 0052). 시각은 KST(결정 0012).
- 데이터 삭제(`track_fast`·`patrol_all`)·시연 대본 테스트·`scripts/qa/script.json`·`scripts/qa/editor.json`은 'track' 세션 몫이다. 이 계획은 그 파일들을 고치지 않는다(마지막 Task 7의 script.json P6 클릭 전환만 예외, track 세션이 main에 올린 뒤).
- 각 Task 끝에 `scripts/ship.sh`(origin/main rebase → 바뀐 모듈 테스트 → smoke → push). 실패 테스트가 있으면 ship하지 않는다.
- 다른 개발 서버가 8000·5173을 쓰고 있다. 이 worktree 화면 점검은 gateway 8010·vite 5183·Chrome 9349로 띄운다(Task 5 Step 1).

## Review Focus

- 지금 하고 있는 Role이 '표적 없는 Role' 목록에 다시 나오면 누른 것이 아무것도 바꾸지 않는다 → 목록에서 빠져야 한다(Task 2 테스트 `leaves out the role it runs now`).
- 적이 쓰는 Role(`enemy_*`, 해상 move_to)이 usv 메뉴에 나오면 아군 수상정이 적 대본을 따른다 → 빠져야 한다(Task 2 테스트 `usv`).
- 정찰 드론(d1·d3·d4)에 '표적 타격'이 보이면 누른 뒤 타격 명령이 나가 무장 없는 기체가 표적을 무력화한다 → 능력 조건으로 빠져야 한다(Task 2 테스트 `d1`, Task 5 L7c 화면 점검).
- 놓친 적·RF만 잡힌 적·무력화된 적이 포착 목록에 있으면 위치를 모르는 적을 친다 → `seen`만(Task 2 `seenTargets` 테스트).
- 표적 없이 옮긴 기체가 예전 결정 id를 들고 있으면 전 기체 버튼 뒤 타격이 출처 검사를 통과한다 → `decision_id`가 지워져야 한다(Task 1 테스트 `a switch without a target leaves no decision`).

---

### Task 1: 지목 전환이 기체의 결정 id가 된다 (runtime + API.md)

**Files:**
- Modify: `modules/runtime/actions/apply_injection.py`
- Test: `modules/runtime/tests/test_apply_injection.py`
- Modify: `modules/runtime/SPEC.md:10` (RT-05 행)
- Modify: `contracts/API.md` 1절 타격 문단, 4절 표

**Interfaces:**
- Consumes: `switch_role(st, role) -> VehicleState`(이미 `decision_id`를 None으로 지움), `Injection.id`, `Injection.target_by_vehicle: dict[str, str]`
- Produces: `apply_injection(states, roles, injection) -> list[VehicleState]` — `target_by_vehicle`에 있는 기체는 `role_id`·`target_id`·`decision_id == injection.id`. 화면 Task들은 이 동작에 기대어 지목 타격을 확인한다.

- [ ] **Step 1: 실패하는 테스트 쓰기** — `modules/runtime/tests/test_apply_injection.py` 끝에 더한다.

```python
def test_pointing_makes_the_press_the_vehicles_decision():
    # decision 0058: the operator picked d2, a target role and boat1; that press is the decision on boat1,
    # so a strike step of that role carries inj2 as its source and passes safety rule 1
    inj = Injection(id="inj2", t_ms=0, label="표적 감시: d2 → boat1", status="approved",
                    role_by_vehicle={"d2": "watch"}, target_by_vehicle={"d2": "boat1"})  # fmt: skip
    (d2,) = apply_injection([vs("d2")], {"watch": WATCH}, inj)
    assert d2.decision_id == "inj2"


def test_a_switch_without_a_target_leaves_no_decision():
    # whole-operation buttons and target-less menu switches never make a strike source (decision 0033)
    inj = Injection(id="inj1", t_ms=0, label="전체 귀환", status="approved", role_by_vehicle={"d1": "go_home"})
    (d1,) = apply_injection([vs("d1").model_copy(update={"decision_id": "dec-1"})], {"go_home": HOME}, inj)
    assert d1.decision_id is None
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest modules/runtime/tests/test_apply_injection.py -n 0 -v`
Expected: `test_pointing_makes_the_press_the_vehicles_decision` FAIL (`assert None == 'inj2'`), `test_a_switch_without_a_target_leaves_no_decision` PASS(switch_role이 이미 지움 — 회귀 방지용).

- [ ] **Step 3: 구현** — `modules/runtime/actions/apply_injection.py` 전체를 이렇게 바꾼다.

```python
"""RT-05 apply_injection: 승인된 전환(전체 전환 버튼·일부 전환)을 role_by_vehicle대로 적용 (사건 4)
지도·기체 메뉴에서 표적을 지목한 전환은 target_by_vehicle의 표적을 그 기체의 표적으로 두고(결정 0048),
그 전환 id를 기체의 결정 id로 적는다: 기체·표적·Role을 골라 누른 것이 그 표적에 대한 운용자 결정이라
타격 Role도 안전 규칙 1(출처)을 통과한다(결정 0058). 표적 없이 옮긴 기체는 결정 id가 없다.
SPEC: modules/runtime/SPEC.md#RT-05
"""

from contracts.models import Injection, Role, VehicleState
from modules.runtime.actions.switch_role import switch_role


def apply_injection(
    states: list[VehicleState], roles: dict[str, Role], injection: Injection
) -> list[VehicleState]:
    to, tgt = injection.role_by_vehicle, injection.target_by_vehicle
    out = []
    for s in states:
        if s.id in to:
            s = switch_role(s, roles[to[s.id]])
            if s.id in tgt:  # pointed at a target (decisions 0048, 0058)
                s = s.model_copy(update={"target_id": tgt[s.id], "decision_id": injection.id})
        out.append(s)
    return out
```

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest modules/runtime -q`
Expected: 모두 PASS(slow 제외는 기본 설정이 아니면 `-m "not slow"`).

- [ ] **Step 5: SPEC·API.md**
  - `modules/runtime/SPEC.md` RT-05 완료 기준 칸 끝 `(지도 지목, 결정 0048)` 뒤에 `, 그 기체 decision_id = injection id(지목 타격 출처, 결정 0058)`를 더한다. 담당 칸(황승주)은 그대로.
  - `contracts/API.md` 1절 **타격(결정 0033)** 문단의 `전환 버튼·예비 이어받기로 옮긴 기체는 \`decision_id\`가 없다.`를 다음으로 바꾼다:
    `표적을 지목한 전환(\`target_by_vehicle\`이 있는 Injection)은 그 기체에 \`decision_id\` = 그 Injection id(\`inj-n\`)를 적는다. 운용자가 기체·표적·Role을 골라 누른 것이 그 표적에 대한 결정이다(결정 0058). 전환 버튼·표적 없는 전환·예비 이어받기로 옮긴 기체는 \`decision_id\`가 없다.`
  - 4절 표의 `| 표적 지목 |` 행을 다음 두 행으로 바꾼다:
    `| 기체 메뉴 Role 전환 | \`POST /injections {role_by_vehicle, approve: true}\` | 상황판에서 기체를 누르고 표적 없는 Role을 누른 것. 버튼의 "지금 Role → 새 Role"이 미리 보기이고 누른 것이 승인이라 \`Injection(approved)\`로 기록하고 대기 카드 없이 다음 틱에 적용한다. 운용자 조작 1(결정 0059) |`
    `| 표적 지목 | \`POST /injections {role_by_vehicle, target_by_vehicle, approve: true}\` | 상황판에서 기체 → 표적 Role → 포착된 적(또는 기체 → 지도 표적 → Role)을 누른 것. 메뉴가 미리 보기이고 누른 것이 승인이라 \`Injection(approved)\`로 기록하고 다음 틱에 \`apply_injection\`이 Role·\`target_id\`·\`decision_id\`(= Injection id)를 바꾼다. 그래서 무장 기체의 타격 Role('표적 타격')도 출처 검사를 통과한다. 운용자 조작 1(결정 0048·0049·0058) |`

- [ ] **Step 6: 커밋·ship**

```bash
git add modules/runtime/actions/apply_injection.py modules/runtime/tests/test_apply_injection.py modules/runtime/SPEC.md contracts/API.md
git commit -m "Part1-32.1: a pointed switch is the vehicle's decision (decision 0058): apply_injection writes decision_id = the injection id for vehicles in target_by_vehicle, so a pointed strike role passes safety rule 1; switches without a target keep none; API.md §1 and §4 (menu role switch, pointing)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
scripts/ship.sh
```

---

### Task 2: 메뉴에 띄울 Role과 포착된 적 (순수 함수 두 개)

**Files:**
- Create: `modules/cop-ui/src/features/board/vehicleMenuRoles.ts`, `vehicleMenuRoles.test.ts`
- Create: `modules/cop-ui/src/features/board/seenTargets.ts`, `seenTargets.test.ts`
- Modify: `modules/cop-ui/SPEC.md` (UI-97·UI-98 행 추가)

**Interfaces:**
- Consumes: `Role`, `VehicleSpec`, `ActionKind`, `Target`, `GeoPoint`(`contracts.gen`), `Track`(`./trackState`: `{ k: "seen" | "rf" | "lost" | "never" | "gone"; pos; … }`)
- Produces:
  - `export interface MenuRole { id: string; name: string; strike: boolean }`
  - `vehicleMenuRoles(roles: Role[], spec: VehicleSpec, enemyRoleIds: string[], currentRoleId: string | null): { plain: MenuRole[]; target: MenuRole[] }`
  - `export interface SeenTarget { id: string; kind: string; threat: number; distM: number }` (`kind`는 한글, `threat`는 0.01 단위 그대로)
  - `export const TARGET_KIND_KO: Record<string, string>`
  - `seenTargets(targets: Target[], tracks: Record<string, Track>, from: GeoPoint): SeenTarget[]`

- [ ] **Step 1: 실패하는 테스트 — `vehicleMenuRoles.test.ts`**

```ts
import { describe, expect, it } from "vitest";
import type { ActionKind, Domain, Role, VehicleSpec } from "../../contracts.gen";
import { vehicleMenuRoles } from "./vehicleMenuRoles";

const step = (id: string, kind: ActionKind, target?: string) => ({ id, name: id, do: { kind, params: target ? { target } : {} } });
const role = (id: string, domains: Domain[], ...steps: ReturnType<typeof step>[]): Role =>
  ({ id, name: `${id}名`, domains, entry: steps[0].id, steps });
// The night operation's roles in small (demo/scenarios/baengnyeong_night.json)
const ROLES = [
  role("standby", ["air", "sea", "ground"], step("w", "hold")),
  role("go_home", ["air", "sea", "ground"], step("r", "return_home")),
  role("patrol_a", ["air"], step("p", "patrol_route"), step("rep", "watch_target", "nearest")),
  role("watch", ["air"], step("w", "watch_target", "operator")),
  role("track_fast", ["air"], step("t", "watch_target", "operator")),
  role("approach", ["sea"], step("a", "approach_target", "operator")),
  role("strike", ["air", "sea"], step("s", "strike_target", "operator")),
  role("landing", ["ground"], step("m", "move_to")),
  role("enemy_boat1", ["sea"], step("m", "move_to")),
];
const AIR: ActionKind[] = ["approach_target", "hold", "move_to", "patrol_route", "return_home", "watch_target"];
const spec = (id: string, domain: Domain, capabilities?: ActionKind[]) => ({ id, domain, capabilities }) as VehicleSpec;
const ids = (xs: { id: string }[]) => xs.map((x) => x.id);

describe("vehicleMenuRoles", () => {
  it("gives the armed drone its air roles, target roles last, strike marked", () => {
    const m = vehicleMenuRoles(ROLES, spec("d2", "air", [...AIR, "strike_target"]), ["enemy_boat1"], null);
    expect(ids(m.plain)).toEqual(["standby", "go_home", "patrol_a"]);
    expect(m.target).toEqual([{ id: "watch", name: "watch名", strike: false },
      { id: "track_fast", name: "track_fast名", strike: false }, { id: "strike", name: "strike名", strike: true }]);
  });

  it("gives a recon drone d1 no strike: it cannot do strike_target", () => {
    expect(ids(vehicleMenuRoles(ROLES, spec("d1", "air", AIR), ["enemy_boat1"], null).target)).toEqual(["watch", "track_fast"]);
  });

  it("gives the usv sea roles only and never an enemy's role", () => {
    const m = vehicleMenuRoles(ROLES, spec("usv", "sea", [...AIR, "strike_target"]), ["enemy_boat1"], null);
    expect(ids(m.plain)).toEqual(["standby", "go_home"]);
    expect(ids(m.target)).toEqual(["approach", "strike"]);
  });

  it("leaves out the role it runs now from the target-less list, keeps it among target roles", () => {
    const m = vehicleMenuRoles(ROLES, spec("d2", "air", [...AIR, "strike_target"]), [], "patrol_a");
    expect(ids(m.plain)).toEqual(["standby", "go_home"]);
    expect(ids(vehicleMenuRoles(ROLES, spec("d2", "air", [...AIR, "strike_target"]), [], "watch").target))
      .toEqual(["watch", "track_fast", "strike"]);
  });

  it("drops a role with a step the vehicle cannot do (ground robot cannot watch a target)", () => {
    const m = vehicleMenuRoles(ROLES, spec("ugv", "ground", ["hold", "move_to", "patrol_route", "return_home", "watch_point"]), [], null);
    expect(ids(m.plain)).toEqual(["standby", "go_home", "landing"]);
    expect(m.target).toEqual([]);
  });

  it("skips the capability rule when the operation has no ontology (no capabilities)", () => {
    expect(ids(vehicleMenuRoles(ROLES, spec("x", "air"), [], null).target)).toEqual(["watch", "track_fast", "strike"]);
  });
});
```

- [ ] **Step 2: 실패하는 테스트 — `seenTargets.test.ts`**

```ts
import { describe, expect, it } from "vitest";
import { at, mkTarget } from "./boardFixtures";
import { seenTargets } from "./seenTargets";
import type { Track } from "./trackState";

const tr = (k: Track["k"]): Track => ({ k, pos: at(37.96, 124.7) });

describe("seenTargets", () => {
  it("lists only what our sensors see now, most dangerous first, with the distance from the vehicle", () => {
    const targets = [
      mkTarget({ id: "boat1", threat: 50, pos: at(37.96, 124.7) }),
      mkTarget({ id: "fast1", kind: "fast_boat", threat: 100, pos: at(37.97, 124.7) }),
      mkTarget({ id: "boat2", threat: 72 }), mkTarget({ id: "boat3", threat: 90 }),
      mkTarget({ id: "gone1", threat: 99 }), mkTarget({ id: "never1", threat: 80 }),
    ];
    const tracks = { boat1: tr("seen"), fast1: tr("seen"), boat2: tr("lost"), boat3: tr("rf"), gone1: tr("gone"), never1: tr("never") };
    expect(seenTargets(targets, tracks, at(37.95, 124.7))).toEqual([
      { id: "fast1", kind: "고속정", threat: 100, distM: 2226 },
      { id: "boat1", kind: "보트", threat: 50, distM: 1113 },
    ]);
  });

  it("is empty when nothing is seen", () => {
    expect(seenTargets([mkTarget({ id: "boat1" })], { boat1: tr("lost") }, at(37.95, 124.7))).toEqual([]);
  });
});
```

- [ ] **Step 3: 실패 확인**

Run: `cd modules/cop-ui && npx vitest run src/features/board/vehicleMenuRoles.test.ts src/features/board/seenTargets.test.ts`
Expected: FAIL — `Failed to resolve import "./vehicleMenuRoles"`, `"./seenTargets"`.

- [ ] **Step 4: 구현 — `vehicleMenuRoles.ts`**

```ts
import type { ActionKind, Role, VehicleSpec } from "../../contracts.gen";

export interface MenuRole { id: string; name: string; strike: boolean }

const TARGET_KINDS: ActionKind[] = ["watch_target", "approach_target", "strike_target"];

// What the vehicle menu offers (decisions 0058, 0059): roles of the vehicle's domain whose every action it can do
// (its capabilities; an operation without an ontology has none, then this rule is skipped), never an enemy's role.
// A role whose first step works the target the operator gives (as runtime spot_reports reads it, plus strike) is a
// target role, pointed at a seen enemy or a map target; the rest switch at once and leave out the role it runs now.
export function vehicleMenuRoles(roles: Role[], spec: VehicleSpec, enemyRoleIds: string[], currentRoleId: string | null):
  { plain: MenuRole[]; target: MenuRole[] } {
  const can = spec.capabilities ?? [];
  const usable = roles.filter((r) => !enemyRoleIds.includes(r.id) && (r.domains ?? []).includes(spec.domain)
    && (can.length === 0 || r.steps.every((s) => can.includes(s.do.kind))));
  const first = (r: Role) => r.steps.find((s) => s.id === r.entry);
  const picks = (r: Role) => {
    const s = first(r);
    return !!s && TARGET_KINDS.includes(s.do.kind) && s.do.params?.target === "operator";
  };
  const item = (r: Role): MenuRole => ({ id: r.id, name: r.name, strike: first(r)?.do.kind === "strike_target" });
  return {
    plain: usable.filter((r) => !picks(r) && r.id !== currentRoleId).map(item),
    target: usable.filter(picks).map(item),
  };
}
```

- [ ] **Step 5: 구현 — `seenTargets.ts`**

```ts
import type { GeoPoint, Target } from "../../contracts.gen";
import type { Track } from "./trackState";

export interface SeenTarget { id: string; kind: string; threat: number; distM: number }

export const TARGET_KIND_KO: Record<string, string> = {
  boat: "보트", fast_boat: "고속정", person: "사람", unknown: "미상", drone: "자폭 드론", usv: "적 수상정", ugv: "적 지상로봇",
};
const M_PER_DEG = 111_320;

// The enemies a target role can be pointed at from the vehicle menu: the ones our sensors see right now (track
// "seen", decision 0047). Lost, RF-only, never-seen and struck targets are left out: we do not know where they are
// and a strike would fly to the simulator's true position. Most dangerous first, then nearest.
export function seenTargets(targets: Target[], tracks: Record<string, Track>, from: GeoPoint): SeenTarget[] {
  const mLon = M_PER_DEG * Math.cos((from.lat * Math.PI) / 180);
  return targets
    .filter((t) => tracks[t.id]?.k === "seen")
    .map((t) => ({ id: t.id, kind: TARGET_KIND_KO[t.kind] ?? t.kind, threat: t.threat ?? 0,
      distM: Math.round(Math.hypot((t.pos.lat - from.lat) * M_PER_DEG, (t.pos.lon - from.lon) * mLon)) }))
    .sort((a, b) => b.threat - a.threat || a.distM - b.distM);
}
```

`RosterPanel.tsx`의 지역 상수 `KIND_KO`를 지우고 `import { TARGET_KIND_KO } from "./seenTargets";`로 바꿔 `KIND_KO[t.kind]` → `TARGET_KIND_KO[t.kind]`(같은 표, 한 곳으로).

- [ ] **Step 6: 통과 확인**

Run: `cd modules/cop-ui && npx vitest run src/features/board/`
Expected: 모두 PASS. 거리 기대값(1113, 2226)이 1 m 어긋나면 계산식이 아니라 기대값을 실제 출력으로 맞추되 위도 0.01°≈1113 m 관계는 유지되어야 한다.

- [ ] **Step 7: SPEC 행** — `modules/cop-ui/SPEC.md`의 UI-96 행 바로 아래에 더한다.

```
| UI-97 | vehicleMenuRoles | Role[], VehicleSpec, 적 Role id[], 지금 Role id | {plain, target}: {id, name, strike}[] | 기체 메뉴(결정 0058·0059): 그 기체 영역·능력(모든 step 행동, 능력 목록이 비면 건너뜀)의 Role, 적 Role 제외. 첫 step이 표적을 operator로 받는 감시·근접·타격이면 target(strike 표시), 나머지는 plain(지금 Role 제외) | 리드 | 완료 |
| UI-98 | seenTargets | Target[], Track 묶음, 기체 위치 | {id, kind, threat, distM}[] | 기체 메뉴 표적 Role의 포착 목록: 표적 상태 seen만(놓침·RF만·미탐·무력화 제외), 위험도 높은 순·가까운 순, 종류 한글, 거리 m 정수 | 리드 | 완료 |
```

- [ ] **Step 8: 커밋·ship**

```bash
git add modules/cop-ui/src/features/board/vehicleMenuRoles.ts modules/cop-ui/src/features/board/vehicleMenuRoles.test.ts modules/cop-ui/src/features/board/seenTargets.ts modules/cop-ui/src/features/board/seenTargets.test.ts modules/cop-ui/src/features/board/RosterPanel.tsx modules/cop-ui/SPEC.md
git commit -m "Part1-32.1: vehicleMenuRoles (domain, capabilities, no enemy role; target roles incl. strike for armed vehicles, target-less roles without the running one) and seenTargets (enemies seen now, riskiest first, distance) for the vehicle menu

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
scripts/ship.sh
```

---

### Task 3: 서버 읽기·쓰기 (`postRole`, `fetchBoardData`에 적 Role·전환 버튼)

**Files:**
- Create: `modules/cop-ui/src/features/board/postRole.ts`, `postRole.test.ts`
- Modify: `modules/cop-ui/src/features/board/fetchBoardData.ts`, `fetchBoardData.test.ts`
- Modify: `modules/cop-ui/SPEC.md` (UI-89 행 고침, UI-99 행 추가)

**Interfaces:**
- Consumes: `postJson(url, body) -> Promise<Sent>`(`../cards/postJson`), `fetchOperation() -> Promise<Partial<Operation> | null>`(`../live/fetchOperation`), `EnemySpec.role_id`, `Switch`
- Produces:
  - `postRole(vehicle: string, role: string): Promise<Sent>` — 본문 `{ role_by_vehicle: { [vehicle]: role }, approve: true }`
  - `BoardData = { roles: Role[]; vehicles: VehicleSpec[]; watch: WatchPoint[]; enemyRoles: string[]; switches: Switch[] }`, `NO_BOARD_DATA`도 두 칸 빈 목록

- [ ] **Step 1: 실패하는 테스트 — `postRole.test.ts`**

```ts
import { afterEach, describe, expect, it, vi } from "vitest";
import { postRole } from "./postRole";

describe("postRole", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("asks for the role without a target, approved by the press (decision 0059)", async () => {
    const f = vi.fn((_u: string, _i?: RequestInit) =>
      Promise.resolve({ ok: true, json: () => Promise.resolve({ id: "inj-4" }) } as Response));
    vi.stubGlobal("fetch", f);
    expect(await postRole("d2", "go_home")).toEqual({ ok: true, id: "inj-4" });
    const [url, init] = f.mock.calls[0];
    expect(url).toBe("/injections");
    expect(JSON.parse(init?.body as string)).toEqual({ role_by_vehicle: { d2: "go_home" }, approve: true });
  });

  it("returns the error instead of throwing when the gateway is down", async () => {
    vi.stubGlobal("fetch", vi.fn(() => Promise.reject(new Error("net"))));
    expect(await postRole("d2", "go_home")).toEqual({ ok: false, error: "서버 연결 실패" });
  });
});
```

- [ ] **Step 2: 실패하는 테스트 — `fetchBoardData.test.ts`의 두 테스트를 이렇게 바꾼다.**

```ts
  it("reads roles, vehicle specs, watch points, enemies' roles and the operation's switch buttons", async () => {
    const data: Record<string, unknown> = { "/roles": [{ id: "watch" }], "/vehicles": [{ id: "d1" }], "/watch_points": [{ id: "landing" }],
      "/enemies": [{ id: "boat1", role_id: "enemy_boat1" }], "/operation": { switches: [{ id: "all_home", label: "전 기체 귀환", role_by_vehicle: {} }] } };
    vi.stubGlobal("fetch", vi.fn((u: string) => reply(data[u])));
    expect(await fetchBoardData()).toEqual({ roles: [{ id: "watch" }], vehicles: [{ id: "d1" }], watch: [{ id: "landing" }],
      enemyRoles: ["enemy_boat1"], switches: [{ id: "all_home", label: "전 기체 귀환", role_by_vehicle: {} }] });
  });

  it("gives empty lists for a failed, non-list or unreachable read", async () => {
    vi.stubGlobal("fetch", vi.fn((u: string) =>
      (u === "/roles" ? reply(null, false) : u === "/vehicles" ? reply({}) : u === "/operation" ? reply({ id: "op1" }) : Promise.reject(new Error("net")))));
    expect(await fetchBoardData()).toEqual({ roles: [], vehicles: [], watch: [], enemyRoles: [], switches: [] });
  });
```

- [ ] **Step 3: 실패 확인**

Run: `cd modules/cop-ui && npx vitest run src/features/board/postRole.test.ts src/features/board/fetchBoardData.test.ts`
Expected: postRole FAIL(import 없음), fetchBoardData 두 테스트 FAIL(`enemyRoles`·`switches` 없음).

- [ ] **Step 4: 구현 — `postRole.ts`**

```ts
import type { SwitchIn } from "../../contracts.gen";
import { postJson, type Sent } from "../cards/postJson";

// A target-less role from the vehicle menu (decision 0059): the button showed now -> new, the press is the approval,
// so one approved request the gateway applies next tick (one operator action, no pending card).
export function postRole(vehicle: string, role: string): Promise<Sent> {
  const body: SwitchIn = { role_by_vehicle: { [vehicle]: role }, approve: true };
  return postJson("/injections", body);
}
```

- [ ] **Step 5: 구현 — `fetchBoardData.ts`**

```ts
import type { EnemySpec, Role, Switch, VehicleSpec, WatchPoint } from "../../contracts.gen";
import { fetchOperation } from "../live/fetchOperation";

export interface BoardData { roles: Role[]; vehicles: VehicleSpec[]; watch: WatchPoint[]; enemyRoles: string[]; switches: Switch[] }
export const NO_BOARD_DATA: BoardData = { roles: [], vehicles: [], watch: [], enemyRoles: [], switches: [] };

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

// What the live board needs besides the Frame (Part1-32): role names and first steps, vehicle specs, watch points
// (decision 0047), the roles enemies follow (left out of the vehicle menu) and the operation's switch buttons
// (the roster head, decision 0060). A failed read is an empty list, never a broken screen.
export async function fetchBoardData(): Promise<BoardData> {
  const [roles, vehicles, watch, enemies, op] = await Promise.all([
    list<Role>("/roles"), list<VehicleSpec>("/vehicles"), list<WatchPoint>("/watch_points"), list<EnemySpec>("/enemies"),
    fetchOperation(),
  ]);
  const switches = Array.isArray(op?.switches) ? op.switches : [];
  return { roles, vehicles, watch, enemyRoles: enemies.map((e) => e.role_id), switches };
}
```

- [ ] **Step 6: 통과 확인**

Run: `cd modules/cop-ui && npx vitest run && npx tsc --noEmit -p .`
Expected: 모두 PASS, 타입 오류 없음(`BoardData`를 객체 글자로 만드는 곳이 있으면 두 칸을 더한다).

- [ ] **Step 7: SPEC 행** — UI-89 행을 바꾸고 UI-98 아래에 UI-99를 더한다.

```
| UI-89 | fetchBoardData | — | {roles, vehicles, watch, enemyRoles, switches} | GET /roles·/vehicles·/watch_points·/enemies(적 Role id)·/operation(전환 버튼), 실패·목록 아님·연결 실패는 빈 목록 | 리드 | 완료 |
| UI-99 | postRole | 기체, Role | Sent | POST /injections {role_by_vehicle, approve: true}(기체 메뉴 표적 없는 Role, 결정 0059), throw 없음 | 리드 | 완료 |
```

- [ ] **Step 8: 커밋·ship**

```bash
git add modules/cop-ui/src/features/board/postRole.ts modules/cop-ui/src/features/board/postRole.test.ts modules/cop-ui/src/features/board/fetchBoardData.ts modules/cop-ui/src/features/board/fetchBoardData.test.ts modules/cop-ui/SPEC.md
git commit -m "Part1-32.1: postRole (a target-less role from the vehicle menu, approved by the press, decision 0059); fetchBoardData also reads the enemies' roles and the operation's switch buttons

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
scripts/ship.sh
```

---

### Task 4: 화면 점검 단계 먼저 고치기 (실패 확인용)

화면 연결은 컴포넌트 테스트가 없는 프로젝트라 화면 점검(`scripts/qa/live.json`)이 실패하는 테스트다. 이 Task에서 단계를 먼저 바꾸고 지금 화면에서 실패하는 것을 본 뒤 Task 5에서 구현한다.

**Files:**
- Modify: `scripts/qa/live.json` (L7 블록 교체, L7b·L7c 추가, L15 안내 줄 기대값, L17 전 기체 버튼 추가)
- Modify: `scripts/qa/draft_to_live.json` (I4~I7)

**Interfaces:**
- Produces(Task 5가 맞춰야 할 화면 표지):
  - 펼친 메뉴 `.vmenu`, 표적 없는 Role 버튼은 `.vmenu .vm-plain [data-role]`, 표적 Role 버튼은 `.vmenu .vm-t > button[data-role]`(타격은 `.strike` 클래스), 포착 목록 줄 `.vmenu .vm-pick[data-target]`, 없을 때 `.vmenu .vm-none`
  - 안내 줄 `.direct-hint`: 고른 직후 `"<기체> 선택 · 왼쪽 메뉴에서 Role · 지도를 누르면 그 지점으로 이동 · Esc 취소"`, Role 보낸 뒤 `"전환 inj-n · <기체> → <Role 이름>"`, 지목 보낸 뒤 `"지목 inj-n · <기체> → <표적>"`
  - 아군 머리줄 버튼 `.roster h3 .sw-btn`, 결과 줄 `.roster .sw-note`(`"요청됨 inj-n · 결정 대기에서 승인"`), 오른쪽 `.fold.sw`는 없음

- [ ] **Step 1: `live.json` L7 블록 교체.** `{"clickSel": ".fold.sw summary", "wait": 300},`부터 `{"label": "L7 switch approved", …},`까지(12줄)를 다음으로 바꾼다.

```json
 {"label": "L7 pick d2 in the roster", "eval": "(() => { const r = [...document.querySelectorAll('.roster .ro')].find(x => x.innerText.startsWith('d2')); if (!r) return 'no d2'; r.click(); return 'clicked'; })()", "expect": "clicked"},
 {"wait": 400, "label": "L7 d2's menu: its air roles without the one it runs, target roles with strike (armed drone), no sea or enemy role", "eval": "new Promise((r) => { const w = new WebSocket('ws://' + location.host + '/ws'); w.onmessage = (e) => { const f = JSON.parse(e.data); w.close(); const now = f.vehicles.find((v) => v.id === 'd2').role_id; const plain = [...document.querySelectorAll('.vmenu .vm-plain [data-role]')].map((b) => b.dataset.role); const tg = [...document.querySelectorAll('.vmenu .vm-t > button[data-role]')].map((b) => b.dataset.role); const all = [...plain, ...tg]; r({ now: plain.includes(now), home: plain.includes('go_home') || now === 'go_home', track: tg.includes('track_fast'), strike: tg.includes('strike'), sea: all.some((id) => id === 'approach' || id === 'track_fast_sea'), enemy: all.some((id) => id.startsWith('enemy_')) }); }; })", "expect": {"now": false, "home": true, "track": true, "strike": true, "sea": false, "enemy": false}},
 {"label": "L7 press the first target-less role", "eval": "(() => { const b = document.querySelector('.vmenu .vm-plain [data-role]'); if (!b) return 'no role'; window.__l7 = b.dataset.role; window.__ops = Number(document.querySelector('.loadbar .op b')?.innerText); b.click(); return 'clicked'; })()", "expect": "clicked"},
 {"wait": 800, "label": "L7 sent at once, the menu closed", "eval": "({ hint: document.querySelector('.direct-hint')?.innerText, menu: document.querySelectorAll('.vmenu').length })", "match": "^\\{\"hint\":\"전환 inj-\\d+ · d2 → .+\",\"menu\":0\\}$"},
 {"click": "재생", "wait": 2500},
 {"click": "일시정지", "wait": 800},
 {"label": "L7 one operator action, no approval card, d2 runs the new role", "eval": "new Promise((r) => { const w = new WebSocket('ws://' + location.host + '/ws'); w.onmessage = (e) => { const f = JSON.parse(e.data); w.close(); r({ ops: Number(document.querySelector('.loadbar .op b')?.innerText) - window.__ops, card: [...document.querySelectorAll('.card, .qrow')].some((c) => c.innerText.includes('d2') && c.innerText.includes('전환 승인')), role: f.vehicles.find((v) => v.id === 'd2').role_id === window.__l7 }); }; })", "expect": {"ops": 1, "card": false, "role": true}},
 {"label": "L7b pick the usv (armed)", "eval": "(() => { const r = [...document.querySelectorAll('.roster .ro')].find(x => x.innerText.startsWith('usv')); if (!r) return 'no usv'; r.click(); return 'clicked'; })()", "expect": "clicked"},
 {"wait": 400, "label": "L7b strike is a red target role", "eval": "document.querySelector('.vmenu .vm-t > button[data-role=\"strike\"]')?.classList.contains('strike') ?? false", "expect": true},
 {"clickSel": ".vmenu .vm-t > button[data-role='strike']", "wait": 300},
 {"label": "L7b strike opens the enemies seen now; pick the first", "eval": "(() => { const b = document.querySelector('.vmenu .vm-pick'); if (!b) return document.querySelector('.vmenu .vm-none')?.innerText ?? 'no list'; window.__t = b.dataset.target; b.click(); return 'picked ' + window.__t; })()", "match": "^picked [a-z0-9]+$"},
 {"wait": 800, "label": "L7b pointing sent", "eval": "document.querySelector('.direct-hint')?.innerText", "match": "^지목 inj-\\d+ · usv → [a-z0-9]+$"},
 {"click": "재생", "wait": 2500},
 {"click": "일시정지", "wait": 800},
 {"label": "L7b the usv strikes it with the pointing as its decision, not blocked for provenance", "eval": "new Promise((r) => { const w = new WebSocket('ws://' + location.host + '/ws'); w.onmessage = (e) => { const f = JSON.parse(e.data); w.close(); const u = f.vehicles.find((v) => v.id === 'usv'); r({ role: u.role_id, target: u.target_id === window.__t, decision: /^inj-\\d+$/.test(u.decision_id ?? ''), blocked: f.blocks.some((b) => b.vehicle_id === 'usv' && b.reason === 'no_provenance') }); }; })", "expect": {"role": "strike", "target": true, "decision": true, "blocked": false}},
 {"label": "L7c pick d4 (recon drone)", "eval": "(() => { const r = [...document.querySelectorAll('.roster .ro')].find(x => x.innerText.startsWith('d4')); if (!r) return 'no d4'; r.click(); return 'clicked'; })()", "expect": "clicked"},
 {"wait": 400, "label": "L7c a recon drone has no strike", "eval": "({ menu: document.querySelectorAll('.vmenu').length, strike: !!document.querySelector('.vmenu [data-role=\"strike\"]') })", "expect": {"menu": 1, "strike": false}},
 {"key": "Escape", "wait": 300},
 {"label": "L7c Esc closes the menu", "eval": "document.querySelectorAll('.vmenu').length", "expect": 0},
```

(`Frame.blocks`에 앞선 차단이 남아 있든 그 틱 것만 있든, usv의 `no_provenance` 차단이 없으면 된다. `vehicle_id`·`reason` 칸 이름은 `contracts.gen.ts`의 `Block`과 같다.)

- [ ] **Step 2: `live.json` L15 안내 줄 기대값.** L15 "d4 selected" 단계의 `match` 끝 `\"hint\":\"d4 선택 · 표적을 누르면"`를 `\"hint\":\"d4 선택 · 왼쪽 메뉴에서 Role"`로 바꾼다. L15 "no strike in the menu"(d4는 정찰 드론이라 여전히 false)는 그대로 둔다.

- [ ] **Step 3: `live.json` 전 기체 버튼 단계.** L15의 마지막 단계(`L15 d4 works boat2 …`) 바로 뒤, `{"click": "처음으로", …}` 앞에 넣는다.

```json
 {"label": "L17 no switch fold; the operation's buttons sit in the roster head", "eval": "({ fold: !!document.querySelector('.fold.sw'), head: [...document.querySelectorAll('.roster h3 .sw-btn')].map(b => b.innerText) })", "expect": {"fold": false, "head": ["전 기체 귀환"]}},
 {"clickSel": ".roster h3 .sw-btn", "wait": 800},
 {"label": "L17 the request waits for approval", "eval": "document.querySelector('.roster .sw-note')?.innerText ?? null", "match": "^요청됨 inj-\\d+ · 결정 대기에서 승인$"},
 {"click": "재생", "wait": 2500},
 {"click": "일시정지", "wait": 800},
 {"label": "L17 reject it on its card", "eval": "(() => { const c = [...document.querySelectorAll('.card')].find(x => x.innerText.includes('전환 승인')); const b = c && [...c.querySelectorAll('button')].find(x => x.innerText.trim() === '거부'); if (!b) return 'no reject button'; b.click(); return 'clicked'; })()", "expect": "clicked"},
```

- [ ] **Step 4: `draft_to_live.json` I4~I7.** `{"clickSel": ".fold.sw summary", "wait": 300},`부터 `I6 approve the switch` 다음 `{"click": "일시정지", "wait": 800},`까지를 다음으로 바꾼다(I7 단계와 그 뒤는 그대로).

```json
 {"label": "I4 pick d1 in the roster", "eval": "(() => { const r = [...document.querySelectorAll('.roster .ro')].find(x => x.innerText.startsWith('d1')); if (!r) return 'no d1'; r.click(); return 'clicked'; })()", "expect": "clicked"},
 {"wait": 400, "label": "I4 the saved draft is in d1's menu; press it", "eval": "(() => { const b = [...document.querySelectorAll('.vmenu [data-role]')].find(x => x.innerText.includes('북쪽 해안 순찰 및 고속정 접근')); if (!b) return 'not in menu'; window.__draftId = b.dataset.role; b.click(); return 'pressed'; })()", "expect": "pressed"},
 {"wait": 800, "label": "I5 switch sent at once (no approval card)", "eval": "document.querySelector('.direct-hint')?.innerText ?? null", "match": "^전환 inj-\\d+ · d1 → "},
 {"click": "재생", "wait": 2500},
 {"click": "일시정지", "wait": 800},
```

초안 Role의 첫 step이 표적 Role이면 `.vm-t > button`이라 누르면 목록이 열린다. 그 경우 이 단계는 'pressed'를 돌려도 전환이 안 가서 I5에서 실패한다 → 그때는 초안 Role의 첫 step 종류를 확인하고 계획을 고친다(지금 초안은 '북쪽 해안 순찰'로 시작해 표적 없는 Role로 예상).

- [ ] **Step 5: 지금 화면에서 실패 확인.** 이 worktree 서버를 띄운다(각각 따로, 백그라운드).

```bash
.venv/bin/uvicorn modules.gateway.app:create_app --factory --port 8010
```
```bash
cd modules/cop-ui && KDTH_GATEWAY=http://localhost:8010 npm run dev -- --port 5183 --strictPort
```
그다음:
```bash
QA_BASE=http://localhost:5183 QA_PORT=9349 QA_OUT=logs/qa-p1321 scripts/qa.sh scripts/qa/live.json
```
Expected: L7의 "d2's menu" 단계부터 FAIL(`.vmenu` 없음), L17 FAIL(`fold: true`). L1~L6는 PASS. (qa.sh는 8000·5173이 살아 있는지 먼저 보는데, 다른 세션의 서버가 떠 있어 통과한다. 꺼져 있으면 qa.sh의 그 두 `curl` 확인만 건너뛰도록 `node scripts/qa/run.mjs`를 같은 환경 변수로 직접 돌리고 Chrome은 qa.sh 안의 명령으로 띄운다.)

- [ ] **Step 6: 커밋(아직 ship 안 함 — 화면 점검은 ship이 돌리지 않지만 실패하는 점검을 main에 두지 않는다)**

```bash
git add scripts/qa/live.json scripts/qa/draft_to_live.json
git commit -m "Part1-32.1: screen checks for the vehicle menu first (failing): d2 role at once, usv strike from the seen list, d4 no strike, Esc, roster-head switch button, draft role from d1's menu

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: 기체 메뉴 화면과 '작전 전환' 칸 삭제

**Files:**
- Create: `modules/cop-ui/src/features/board/VehicleMenu.tsx`
- Modify: `modules/cop-ui/src/features/board/RosterPanel.tsx`, `PointMenu.tsx`, `board.css`
- Modify: `modules/cop-ui/src/features/map/useDirectControl.ts`
- Modify: `modules/cop-ui/src/Screen.tsx`, `modules/cop-ui/src/theme.css`, `modules/cop-ui/src/features/cards/cards.css`
- Delete: `modules/cop-ui/src/features/cards/SwitchPanel.tsx`, `features/cards/switchRoleOptions.ts`, `features/cards/switchRoleOptions.test.ts`, `features/board/targetRoles.ts`, `features/board/targetRoles.test.ts`
- Modify: `modules/cop-ui/SPEC.md` (UI-34·UI-65·UI-86 폐기, UI-36·UI-94·UI-96 고침, UI-100 추가)

**Interfaces:**
- Consumes: Task 2 `vehicleMenuRoles`·`MenuRole`·`seenTargets`·`SeenTarget`, Task 3 `postRole`·`BoardData.enemyRoles`·`BoardData.switches`, 기존 `postPoint(vehicle, role, target)`, `postSwitch(body)`(`../cards/injectionRequests`), `boardView().tracks`
- Produces: Task 4의 화면 표지(클래스·안내 줄 문구) 전부

- [ ] **Step 1: `useDirectControl.ts`** — `onPoint`를 공용 `point`로 나누고 `onRole`·`onPointTarget`과 새 안내 줄을 더한다. 반환 타입과 함수 본문의 해당 부분을 이렇게 바꾼다.

```ts
import { postRole } from "../board/postRole";
// …(기존 import 유지)

// Direct control on the map (Part1-11): click a vehicle to select it, click the map to send it there
// (POST /direct), Esc or the same vehicle again cancels. Whether the order passes is the server's safety
// check; a refusal shows up as a block card. frameT is the current frame time: the sent order (cross and
// "보냄" line) shows until a newer frame arrives, then the frame says where vehicles are really heading.
// The vehicle menu (Part1-32.1, decisions 0058, 0059) under the roster row sends a target-less role (onRole) or a
// target role at a seen enemy (onPointTarget); pointing on the map (decisions 0048, 0049) opens a role menu beside
// the target (pick) and sends the same request. Every press is approved at once and deselects the vehicle.
export function useDirectControl(frameT: number): DirectProps & {
  hint: string | null; onRole: (role: string, name: string) => void; onPointTarget: (role: string, target: string) => void;
} {
  // …(state·Esc effect·onVehicleClick·onMapClick·onTargetClick·cancelPick은 그대로)

  const point = async (v: string, role: string, t: string) => {
    const sentAt = frameT;
    setSelected(null);
    setPick(null);
    setStatus({ text: `${v} → ${t} 지목 보내는 중`, sentAt });
    const r = await postPoint(v, role, t);
    setStatus(r.ok ? { text: `지목 ${r.id} · ${v} → ${t}`, sentAt } : { text: `보내기 실패: ${r.error}`, sentAt: null });
  };
  const onPoint = (role: string) => {
    if (selected && pick) point(selected, role, pick.target);
  };
  const onPointTarget = (role: string, target: string) => {
    if (selected) point(selected, role, target);
  };
  const onRole = async (role: string, name: string) => {
    if (!selected) return;
    const v = selected;
    const sentAt = frameT;
    setSelected(null);
    setPick(null);
    setStatus({ text: `${v} → ${name} 보내는 중`, sentAt });
    const r = await postRole(v, role);
    setStatus(r.ok ? { text: `전환 ${r.id} · ${v} → ${name}`, sentAt } : { text: `보내기 실패: ${r.error}`, sentAt: null });
  };

  const shown = status && (status.sentAt === null || frameT <= status.sentAt) ? status.text : null;
  const hint = !selected ? shown
    : pick ? `${selected} → ${pick.target} · 붙일 Role을 고르세요 · Esc 취소`
    : `${selected} 선택 · 왼쪽 메뉴에서 Role · 지도를 누르면 그 지점으로 이동 · Esc 취소`;
  return { selected, pending, pick, onVehicleClick, onMapClick, onTargetClick, onPoint, cancelPick, hint, onRole, onPointTarget };
}
```

기존 `onPoint`(async, 본문에서 직접 postPoint)는 위 `point`·`onPoint`로 대체한다.

- [ ] **Step 2: `VehicleMenu.tsx` 만들기**

```tsx
import { useState } from "react";
import type { SeenTarget } from "./seenTargets";
import type { MenuRole } from "./vehicleMenuRoles";

// The menu under the picked roster row (Part1-32.1, decisions 0058, 0059): move by a map click, target-less roles
// switch at once, a target role opens the enemies seen now under it and a pick points the vehicle at that one.
// Every button shows what changes; the press is the approval.
export function VehicleMenu({ current, plain, target, seen, onRole, onPoint }: {
  current: string; plain: MenuRole[]; target: MenuRole[]; seen: SeenTarget[];
  onRole: (role: string, name: string) => void; onPoint: (role: string, target: string) => void;
}) {
  const [open, setOpen] = useState<string | null>(null);
  return (
    <div className="vmenu">
      <div className="vm-move">이동 · 지도를 누르면 그 지점으로</div>
      {plain.length > 0 && (
        <div className="vm-plain">
          <div className="vm-h">Role 바꾸기 · 누르면 바로</div>
          {plain.map((r) => (
            <button key={r.id} type="button" data-role={r.id} onClick={() => onRole(r.id, r.name)}>
              {r.name}<small>{current} → {r.name}</small>
            </button>
          ))}
        </div>
      )}
      {target.length > 0 && <div className="vm-h">표적에 붙이기 · 포착된 적을 고르세요</div>}
      {target.map((r) => (
        <div key={r.id} className="vm-t">
          <button type="button" data-role={r.id} className={r.strike ? "strike" : ""} aria-expanded={open === r.id}
            onClick={() => setOpen(open === r.id ? null : r.id)}>{r.name}</button>
          {open === r.id && (seen.length > 0 ? seen.map((t) => (
            <button key={t.id} type="button" className="vm-pick" data-target={t.id} onClick={() => onPoint(r.id, t.id)}>
              <b>{t.id}</b><span>{t.kind}</span><em>{(t.threat / 100).toFixed(2)}</em><span>{t.distM} m</span>
            </button>
          )) : <div className="vm-none">지금 포착된 적이 없습니다</div>)}
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 3: `RosterPanel.tsx`** — 머리줄 버튼·결과 줄, 고른 줄 아래 메뉴. 줄은 `<button>`이라 메뉴를 그 안에 넣지 않고 바로 뒤 형제로 둔다.

```tsx
import { Fragment, type ReactNode } from "react";
import type { Switch, Target } from "../../contracts.gen";
import { TARGET_KIND_KO } from "./seenTargets";
// …(Stage, VehicleRow import 유지)

// Left column (Part1-32): our vehicles (what each does, its target, battery) and the targets by risk with their
// own stage. A vehicle row selects it like its map marker and opens the vehicle menu under it (Part1-32.1); with a
// vehicle selected a target row points at it. The operation's switch buttons sit in the head (decision 0060).
export function RosterPanel({ rows, targets, stages, selected, onVehicle, onTarget, menu, switches, onSwitch, switchNote }: {
  rows: VehicleRow[]; targets: Target[]; stages: Record<string, Stage>; selected: string | null;
  onVehicle: (id: string) => void; onTarget: (id: string) => void;
  menu: ReactNode; switches: Switch[]; onSwitch: (id: string) => void; switchNote: string | null;
}) {
  // …(busy·back·idle·counts·ts·gone 계산 그대로)
  return (
    <aside className="roster">
      <h3>아군 <b>{rows.length}</b><small>{counts}</small>
        {switches.map((s) => <button key={s.id} type="button" className="sw-btn" onClick={() => onSwitch(s.id)}>{s.label}</button>)}
      </h3>
      {switchNote && <div className="sw-note">{switchNote}</div>}
      {rows.map((r) => (
        <Fragment key={r.id}>
          <button type="button" className={`ro st-${r.status}${r.id === selected ? " sel" : ""}`} onClick={() => onVehicle(r.id)}>
            {/* …줄 내용 그대로 */}
          </button>
          {r.id === selected && menu}
        </Fragment>
      ))}
      {/* …적 목록 그대로, KIND_KO → TARGET_KIND_KO (Task 2에서 이미 바꿈) */}
    </aside>
  );
}
```

- [ ] **Step 4: `PointMenu.tsx`** — 목록 타입을 `MenuRole`로, 타격 빨강, 안내 문구.

```tsx
import type { MenuRole } from "./vehicleMenuRoles";

// Role menu beside a pointed target (decisions 0048, 0049, 0058): each button says what changes (current role → new
// role · target) and pressing it is the approval. An armed vehicle also gets its strike role (red).
export function PointMenu({ vehicle, target, x, y, roles, current, onPick, onCancel }: {
  vehicle: string; target: string; x: number; y: number; roles: MenuRole[]; current: string;
  onPick: (role: string) => void; onCancel: () => void;
}) {
  return (
    <div className="pickpop" style={{ left: x + 16, top: Math.max(8, y - 20) }}>
      <div className="ph">{vehicle} → {target}</div>
      {roles.length ? roles.map((r) => (
        <button key={r.id} type="button" className={r.strike ? "strike" : ""} onClick={() => onPick(r.id)}>
          {r.name}<small>{current} → {r.name} · 표적 {target}</small></button>
      )) : <div className="pn">{vehicle}가 표적에 쓸 수 있는 Role이 없습니다.</div>}
      <button type="button" className="x" onClick={onCancel}>취소</button>
      <div className="pn">누르면 바로 바뀝니다.</div>
    </div>
  );
}
```

- [ ] **Step 5: `Screen.tsx`** — SwitchPanel·targetRoles import 삭제, 메뉴 계산과 전 기체 버튼 연결, '작전 전환' 접힘 삭제.

```tsx
import { useEffect, useMemo, useState } from "react";
// …(기존 import에서 targetRoles·SwitchPanel 두 줄 삭제)
import { seenTargets } from "./features/board/seenTargets";
import { VehicleMenu } from "./features/board/VehicleMenu";
import { vehicleMenuRoles } from "./features/board/vehicleMenuRoles";
import { postSwitch } from "./features/cards/injectionRequests";

// Live board (Part1-32): header line (stage counts, operator load, link status) in the app header, our vehicles
// (a picked one opens its menu under its row, Part1-32.1) and the targets on the left with the operation's switch
// buttons in its head, the map with the run bar in the middle, the decision queue on the right with the history
// folded under it. A card's "연결 보기" opens its target's graph over the map.
export function Screen(/* …같음 */) {
  // …(tiles·graph·slot·data·direct·board 그대로)
  const [switchNote, setSwitchNote] = useState<string | null>(null);
  const live = frame?.vehicles.find((x) => x.id === direct.selected) ?? null;
  const spec = data.vehicles.find((x) => x.id === direct.selected);
  const current = data.roles.find((r) => r.id === live?.role_id)?.name ?? "대기";
  const menuRoles = spec ? vehicleMenuRoles(data.roles, spec, data.enemyRoles, live?.role_id ?? null) : { plain: [], target: [] };
  const menu = frame && board && live ? (
    <VehicleMenu key={live.id} current={current} plain={menuRoles.plain} target={menuRoles.target}
      seen={seenTargets(frame.targets, board.tracks, live.pos)} onRole={direct.onRole} onPoint={direct.onPointTarget} />
  ) : null;
  const onSwitch = async (id: string) => {
    const r = await postSwitch({ switch_id: id });
    setSwitchNote(r.ok ? `요청됨 ${r.id} · 결정 대기에서 승인` : `요청 실패: ${r.error}`);
  };
  // …useEffect 그대로
  return (
    <div className="layout board">
      {/* …portal 그대로 */}
      {frame && board ? (
        <RosterPanel rows={board.rows} targets={frame.targets} stages={board.stages} selected={direct.selected}
          onVehicle={direct.onVehicleClick} onTarget={(id) => direct.selected && direct.onTargetClick(id, 220, 120)}
          menu={menu} switches={data.switches} onSwitch={onSwitch} switchNote={switchNote} />
      ) : <aside className="roster" />}
      <div className="map-col">
        {/* …MapView·hint 그대로 */}
        {frame && direct.selected && direct.pick && (
          // Pointing (decisions 0048, 0049, 0058): the selected vehicle's target roles beside the pointed target.
          <PointMenu vehicle={direct.selected} target={direct.pick.target} x={direct.pick.x} y={direct.pick.y}
            roles={menuRoles.target} current={current} onPick={direct.onPoint} onCancel={direct.cancelPick} />
        )}
        {/* …RunBar·graph 그대로 */}
      </div>
      <aside className="ops">
        {/* …ops-scroll 그대로 */}
        <div className="folds">
          {/* '작전 전환' details 줄 삭제, '지난 기록' details만 */}
        </div>
      </aside>
    </div>
  );
}
```

- [ ] **Step 6: CSS.** `cards.css`의 `.switchpanel` 여섯 줄(2~7행)과 `theme.css`의 `.switchpanel` 줄들(74~83행 근처, `grep -n switchpanel`로 확인)을 지운다. `board.css`의 pickpop 블록 아래에 레이아웃을 더한다.

```css
/* Vehicle menu under the picked roster row (Part1-32.1) and the operation's buttons in the roster head (decision 0060). */
.board .roster h3 .sw-btn { flex: none; padding: 3px 8px; font-size: 11px; cursor: pointer; }
.board .roster .sw-note { margin: -2px 0 6px; font-size: 11px; }
.board .vmenu { display: flex; flex-direction: column; gap: 4px; padding: 6px 4px 10px 10px; }
.board .vmenu .vm-h { margin-top: 6px; font-size: 11px; }
.board .vmenu .vm-plain { display: flex; flex-direction: column; gap: 4px; }
.board .vmenu button { display: flex; flex-direction: column; align-items: flex-start; gap: 1px; width: 100%; padding: 5px 8px; text-align: left; cursor: pointer; }
.board .vmenu .vm-t { display: flex; flex-direction: column; gap: 3px; }
.board .vmenu .vm-pick { flex-direction: row; align-items: baseline; gap: 8px; margin-left: 10px; width: calc(100% - 10px); }
.board .vmenu .vm-pick em { margin-left: auto; font-style: normal; }
.board .vmenu .vm-none { margin-left: 10px; font-size: 11px; }
```

`theme.css`의 pickpop 색 줄(503~508행 근처) 아래에 색을 더한다.

```css
.board .roster h3 .sw-btn { border: 1px solid var(--warn); border-radius: var(--r); background: transparent; color: var(--warn); font-weight: 700; }
.board .roster .sw-note { color: var(--muted); font-family: var(--font-mono); }
.board .vmenu { border-bottom: 1px solid var(--line); background: var(--s2); }
.board .vmenu .vm-move, .board .vmenu .vm-h, .board .vmenu .vm-none { color: var(--muted); font-size: 11px; }
.board .vmenu button { border: 1px solid var(--line2); border-radius: var(--r); background: var(--s1); color: var(--text); font-size: 12px; font-weight: 600; }
.board .vmenu button:hover { border-color: var(--text); }
.board .vmenu button small { color: var(--muted); font-family: var(--font-mono); font-size: 10px; font-weight: 500; }
.board .vmenu button.strike, .board .pickpop button.strike { border-color: var(--hostile); color: var(--hostile); }
.board .pickpop button.strike { background: var(--hostile-soft); }
.board .vmenu .vm-pick b { font-family: var(--font-mono); }
.board .vmenu .vm-pick span { color: var(--text2); font-size: 11px; }
```

(`--warn`은 theme.css 24행에 있다: #f59e0b, 사진의 주황 버튼 색.)

- [ ] **Step 7: 지울 파일 삭제**

```bash
git rm modules/cop-ui/src/features/cards/SwitchPanel.tsx modules/cop-ui/src/features/cards/switchRoleOptions.ts modules/cop-ui/src/features/cards/switchRoleOptions.test.ts modules/cop-ui/src/features/board/targetRoles.ts modules/cop-ui/src/features/board/targetRoles.test.ts
```

그다음 `grep -rn "SwitchPanel\|switchRoleOptions\|targetRoles" modules/cop-ui/src` 결과가 비어야 한다(주석 포함).

- [ ] **Step 8: 단위 테스트·타입 확인**

Run: `cd modules/cop-ui && npx vitest run && npx tsc --noEmit -p .`
Expected: 모두 PASS, 타입 오류 없음.

- [ ] **Step 9: 화면 점검 통과 확인** (Task 4 Step 5의 서버가 떠 있는 채로. vite는 파일을 바꾸면 다시 읽는다.)

```bash
QA_BASE=http://localhost:5183 QA_PORT=9349 QA_OUT=logs/qa-p1321 scripts/qa.sh scripts/qa/live.json scripts/qa/draft_to_live.json scripts/qa/scenes.json
```
Expected: 전부 PASS. L7b가 `지금 포착된 적이 없습니다`로 실패하면 그 시각(L6 뒤 약 20:00)에 보이는 적이 없다는 뜻이다 → WS Frame에서 `seen_by`가 빈 적만 있는지 확인하고, L7b 블록을 '다음 사건'이 fast1 카드(23:05)에서 멈춘 뒤(L10 뒤)로 옮긴다. 스크린샷 `logs/qa-p1321/live-point-menu.png`를 열어 메뉴 모양을 눈으로 본다.

- [ ] **Step 10: SPEC 행**
  - UI-34 상태 칸 `완료` → `폐기(Part1-32.1, 결정 0060: 작전 전환 칸 삭제, 기체 하나는 기체 메뉴 UI-100, 전 기체 버튼은 아군 머리줄 UI-94)`
  - UI-65 상태 칸 `완료` → `폐기(Part1-32.1: SwitchPanel과 함께 삭제, 기체 메뉴는 vehicleMenuRoles UI-97)`
  - UI-86 상태 칸 `완료` → `폐기(Part1-32.1, 결정 0058: vehicleMenuRoles UI-97의 target이 대신, 무장 기체는 타격 포함)`
  - UI-36 완료 기준 끝에 `, 기체 메뉴의 Role(onRole → postRole)·포착 적 지목(onPointTarget → postPoint)도 보낸 뒤 해제하고 안내 줄에 결과(Part1-32.1)` 추가
  - UI-94 완료 기준 끝에 `, 고른 기체 줄 아래 기체 메뉴(UI-100), 머리줄에 작전 전환 버튼(승인 카드)과 결과 줄(결정 0060)` 추가
  - UI-96 완료 기준의 `targetRoles 버튼` → `vehicleMenuRoles의 target 버튼`, 끝의 `타격 없음(결정 0048·0049)` → `무장 기체는 타격 Role 빨강(결정 0048·0049·0058)`
  - UI-99 아래에 추가:
    `| UI-100 | VehicleMenu | 지금 Role 이름, MenuRole[]×2, SeenTarget[] | 기체 메뉴 | 고른 아군 줄 아래(결정 0058·0059): 이동 안내, 표적 없는 Role 버튼("지금 → 새", 누르면 바로), 표적 Role 버튼(타격 빨강)을 누르면 그 아래 포착 적 목록(종류·위험도·거리)·없으면 안내, 고르면 바로 지목 | 리드 | 완료 |`

- [ ] **Step 11: 커밋·ship**

```bash
git add -A modules/cop-ui
git commit -m "Part1-32.1: the vehicle menu under the picked roster row (decisions 0058, 0059): move hint, target-less roles at once, target roles open the enemies seen now and point the vehicle (strike in red for armed vehicles, also beside a map-pointed target); the switch fold is gone, the operation's buttons sit in the roster head (decision 0060); SwitchPanel, switchRoleOptions and targetRoles removed; screen checks live, draft_to_live pass

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
scripts/ship.sh
```

---

### Task 6: 기록과 알림

**Files:**
- Modify: `demo/BUILT_HERE.md`

- [ ] **Step 1: BUILT_HERE 한 줄** — 표 끝에 (시각은 `TZ=Asia/Seoul date +%H:%M`)

```
| 10/10 HH:MM | cop-ui, runtime, contracts | Part1-32.1 상황판 기체 메뉴(결정 0058·0059·0060·0061): 기체를 누르면 아군 줄 아래에 이동 안내·표적 없는 Role(누르면 바로)·표적 Role(무장 기체는 '표적 타격' 빨강, 누르면 지금 포착된 적 목록에서 골라 바로 지목). 지목 전환 id가 기체의 결정 id라 지목 타격이 출처 검사 통과(runtime apply_injection). '작전 전환' 칸 삭제, '전 기체 귀환'은 아군 머리줄 | kth9245 |
```

- [ ] **Step 2: 커밋·ship·할 일**

```bash
git add demo/BUILT_HERE.md
git commit -m "Part1-32.1: BUILT_HERE line for the vehicle menu

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
scripts/ship.sh
```

리드에게: 황승주에게 runtime `apply_injection` 변경(결정 0058)을 채팅으로 알려 달라고 한다. Task 7이 끝나면 `uv run python scripts/task.py done Part1-32.1`.

---

### Task 7: 발표자 대본 점검을 메뉴 클릭으로 (track 세션 ship 뒤)

track 세션이 `scripts/qa/script.json` P6을 `fetch('/injections', { approve: true })` 두 번으로 바꿔 main에 올렸다는 알림을 받은 뒤에 한다.

**Files:**
- Modify: `scripts/qa/script.json` (P6의 지목 두 번)

- [ ] **Step 1: rebase로 track 세션 변경 받기**

```bash
git fetch origin
git rebase origin/main
```

- [ ] **Step 2: P6 지목 단계 교체.** track 세션이 넣은 d2·usv `fetch('/injections' …)` 단계 둘을 각각 다음 세 단계로 바꾼다(usv는 `d2`→`usv`, `track_fast`→`track_fast_sea`).

```json
 {"label": "P6 pick d2", "eval": "(() => { const r = [...document.querySelectorAll('.roster .ro')].find(x => x.innerText.startsWith('d2')); if (!r) return 'no d2'; r.click(); return 'clicked'; })()", "expect": "clicked"},
 {"clickSel": ".vmenu .vm-t > button[data-role='track_fast']", "wait": 300},
 {"label": "P6 d2 → fast-boat tracking at fast1", "eval": "(() => { const b = document.querySelector('.vmenu .vm-pick[data-target=\"fast1\"]'); if (!b) return 'fast1 not seen'; b.click(); return 'pointed'; })()", "expect": "pointed"},
```

- [ ] **Step 3: 확인**

Run: `QA_BASE=http://localhost:5183 QA_PORT=9349 QA_OUT=logs/qa-p1321 scripts/qa.sh scripts/qa/script.json`
Expected: P1~P8 PASS(P7 타격 허락 카드 → '함께 타격' → P8 무력화). fast1이 그 시각 `seen`이 아니면 'fast1 not seen' → 지도에서 fast1을 누르는 `clickSel` 지목으로 바꾼다(지도 지목은 `seen`이 아니어도 된다).

- [ ] **Step 4: 커밋·ship·완료**

```bash
git add scripts/qa/script.json
git commit -m "Part1-32.1: the presenter's script points d2 and the usv at fast1 through the vehicle menu

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
scripts/ship.sh
uv run python scripts/task.py done Part1-32.1
```
