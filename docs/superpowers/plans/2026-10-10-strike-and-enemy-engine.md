# 타격·적 행동 엔진 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 계약에 타격·적 행동을 넣고(Part1-18), 엔진이 "사람 결정이 붙은 타격만 기체로 나가고, 표적 100 m 안이면 무력화"와 "적이 플레이대로 나타나 움직임"을 계산하게 한다(Part2-21~25).

**Architecture:** 계약은 기본값 있는 칸 추가만 한다. 타격 승인은 `apply_decision`이 기체에 남긴 `decision_id`가 `enter_step`을 거쳐 명령 출처로 가고 safety 규칙 1이 확인한다. 적은 runtime·safety를 거치지 않고 sim 액션 둘(`spawn_enemies`·`steer_enemies`)이 속도와 step만 정하며 위치는 기존 `apply_events`가 옮긴다.

**Tech Stack:** Python 3.12, pydantic v2, pytest(xdist), uv. 화면 한 줄은 TypeScript(vitest, tsc).

**Spec:** `docs/superpowers/specs/2026-10-10-strike-phase-design.md`(3·4절, 10절), 결정 0033(타격)·0032(적).

## Global Constraints

- 작업 폴더: worktree `/home/kth9245/HACKERTON/KDTH2026/.claude/worktrees/Part1-18`. 메인 폴더에서 파일을 고치지 않는다. `$(...)`·`&&`로 git을 묶지 않는다(worktree 세션이 거부함).
- 액션 파일: 공개 함수 1개, 이름 = 파일 이름, 80줄 이하. 새 액션은 `uv run python scripts/new_action.py <m> <name> "<설명>" --inputs .. --outputs .. --done ..`로 만든다(SPEC 행·파일·실패 테스트).
- TDD: 실패 테스트 → 실패 확인 → 구현 → 통과(결정 0014).
- 다른 모듈은 `from modules.<m> import <공개 API>`로만. 같은 모듈 안 액션끼리는 `modules.<m>.actions.<name>` import 허용(기존 코드와 같음).
- `contracts/schema/`·`modules/cop-ui/src/contracts.gen.ts`는 손으로 고치지 않는다. `contracts/models/`를 커밋하면 `scripts/check.sh`가 다시 만든다.
- 할 일 기록: 작업 시작 `uv run python scripts/task.py start <번호>`, ship 성공 뒤 `uv run python scripts/task.py done <번호>`. Part2-21~25는 남(황승주·최동호)에게 배정돼 있었으나 리드가 직접 하기로 함(2026-10-10 12:00 리드 "그럼 지금 ㄱㄱ") — 시작하면 채팅으로 두 사람에게 알린다(결정 0019).
- 반영: 작업마다 `scripts/ship.sh`(rebase → 바뀐 모듈 테스트 → smoke → main push). 실패 테스트가 있으면 ship하지 않는다.
- 커밋 메시지 끝: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
- 개발 기준(결정 0024): happy path. 시연 대본에서 생기지 않는 예외 처리는 넣지 않는다.

## Review Focus

시연 흐름에서 실제로 생기는데 눈으로 놓치기 쉬운 것 다섯(각각 담당 작업에 테스트가 있다):
1. 드론2가 boat1과 fast1을 같이 센서에 잡은 상태에서 '타격 승인 요청' 카드가 뜨면, 카드의 표적은 추적 중인 fast1이어야 한다(boat1이면 승인 뒤 엉뚱한 배를 친다) — Task 2 `test_report_card_names_the_tracked_target`.
2. 드론2 카드에서 '함께 타격'을 누르면 수상정이 기다리던 카드도 닫혀야 한다(열린 채 남으면 시연 화면에 처리 안 된 승인 카드가 보임) — Task 2 `test_moved_vehicles_open_cards_close`.
3. 전환 버튼(주입)으로 타격 플레이에 들어간 기체는 결정 id가 없어 타격 명령이 막혀야 한다 — Task 2 `test_switch_clears_decision_id`, Task 3 `test_strike_without_decision_is_blocked`.
4. 무력화된 표적 옆에서 타격 기체가 계속 머물러도 결과 카드가 틱마다 다시 생기면 안 된다 — Task 4 `test_already_neutralized_gives_no_card`.
5. 무력화된 적은 자기 플레이가 남아 있어도 멈춰 있어야 한다 — Task 6 `test_neutralized_enemy_stays_still`.

---

### Task 1: 계약 추가 + play 대응표 행 + 화면 이름표 (Part1-18, 한 커밋)

**Files:**
- Modify: `contracts/models/enums.py` (ActionKind·CommandKind·ReportKind)
- Modify: `contracts/models/world.py` (VehicleState.decision_id, 새 EnemySpec)
- Modify: `contracts/models/events.py` (Target 칸 5개)
- Modify: `contracts/models/frame.py` (Scenario.enemies)
- Modify: `contracts/models/__init__.py` (EnemySpec export, `_MODELS`)
- Modify: `modules/play/actions/expand_action.py` (strike_target 행)
- Modify: `modules/cop-ui/src/features/editor/describe.ts` (ACTION_LABEL)
- Modify: `scripts/gen_examples.py` (enemy_spec 예시)
- Modify: `contracts/API.md` (1·2·3·5절)
- Test: `tests/test_contracts.py`, `modules/play/tests/test_expand_action.py`

**Interfaces:**
- Produces: `ActionKind.strike_target`, `CommandKind.strike`, `ReportKind.target_neutralized`; `VehicleState.decision_id: str | None = None`; `Target.neutralized_ms: int | None = None`, `Target.play_id: str | None = None`, `Target.step_id: str | None = None`, `Target.waypoint_idx: int = 0`, `Target.step_since_ms: int | None = None`; `EnemySpec(id: str, kind: TargetKind, speed_mps: float, appear_offset_ms: int, pos: GeoPoint | None = None, from_enemy: str | None = None, play_id: str)`; `Scenario.enemies: list[EnemySpec] = []`; `expand_action(Action(kind="strike_target"), "air"|"sea") == CommandKind.strike`, ground → None.

- [ ] **Step 1: 시작 기록**

Run: `uv run python scripts/task.py start Part1-18`
Expected: `Part1-18 ... 시작` 한 줄과 main 커밋 sha.

- [ ] **Step 2: 실패 테스트 쓰기**

`tests/test_contracts.py` 맨 끝에 추가(맨 위 import에 `EnemySpec`, `Target`을 더한다):

```python
def test_strike_and_enemy_enum_values():
    from contracts.models import ActionKind, CommandKind, ReportKind

    assert ActionKind("strike_target") and CommandKind("strike")
    assert ReportKind("target_neutralized")


def test_strike_and_enemy_fields_default_to_empty():
    g = GeoPoint(lat=37.9, lon=124.7)
    st = VehicleState(id="d1", t_ms=0, pos=g, heading_deg=0, battery_pct=90, status="ready")
    assert st.decision_id is None
    tg = Target(id="b", kind="boat", pos=g, vel_east_mps=0, vel_north_mps=0,
                first_seen_ms=0, last_seen_ms=0)  # fmt: skip
    assert (tg.neutralized_ms, tg.play_id, tg.step_id, tg.waypoint_idx, tg.step_since_ms) == (
        None, None, None, 0, None,
    )  # fmt: skip
    sc = Scenario.model_validate(_load(EXAMPLES / "scenario.json"))
    assert sc.enemies == []


def test_enemy_appears_at_a_point_or_from_another_enemy():
    e = EnemySpec(id="fast1", kind="fast_boat", speed_mps=6.3, appear_offset_ms=1_380_000,
                  from_enemy="boat1", play_id="enemy_fast1")  # fmt: skip
    assert e.pos is None and e.from_enemy == "boat1"
```

`modules/play/tests/test_expand_action.py`의 parametrize 목록에 세 줄 추가:

```python
(("strike_target", "air", CommandKind.strike),)
(("strike_target", "sea", CommandKind.strike),)
```

그리고 파일 끝에:

```python
def test_ground_cannot_strike():
    assert expand_action(Action(kind="strike_target"), Domain.ground) is None
```

- [ ] **Step 3: 실패 확인**

Run: `uv run pytest tests/test_contracts.py modules/play/tests/test_expand_action.py -n 0 -q`
Expected: FAIL — `ImportError: cannot import name 'EnemySpec'` (import 줄 때문에 파일 전체가 실패).

- [ ] **Step 4: 계약 구현**

`contracts/models/enums.py`:
- `ActionKind`의 `hold = "hold"` 다음 줄에 `strike_target = "strike_target"  # decision 0033: strike the approved target`
- `CommandKind`의 `relay = "relay"` 다음 줄에 `strike = "strike"`
- `ReportKind`의 `command_blocked = "command_blocked"` 다음 줄에 `target_neutralized = "target_neutralized"  # alert only (decision 0033)`

`contracts/models/world.py`:
- import 줄을 `from .enums import ActionKind, Domain, EmergencyKind, TargetKind, VehicleStatus`로.
- `VehicleState`의 `target_id` 줄 다음에:

```python
    decision_id: str | None = None  # operator decision that moved it into this play (decision 0033)
```

- `VehicleSpec` 클래스 다음에:

```python
class EnemySpec(BaseModel):  # decision 0032: an enemy follows its own play, no safety checks
    id: str
    kind: TargetKind
    speed_mps: float
    appear_offset_ms: int  # ms after operation.started_ms
    pos: GeoPoint | None = None  # where it appears, or
    from_enemy: str | None = None  # at that enemy's current position
    play_id: str
```

`contracts/models/events.py`의 `Target`에서 `seen_by` 줄 다음에:

```python
    neutralized_ms: int | None = None  # struck (decision 0033); it stops moving
    play_id: str | None = None  # enemy progress (decision 0032)
    step_id: str | None = None
    waypoint_idx: int = 0  # -1 = arrived at the move_to destination
    step_since_ms: int | None = None  # when this step began (time_elapsed)
```

`contracts/models/frame.py`:
- import 줄을 `from .world import EnemySpec, Operation, VehicleSpec, VehicleState`로.
- `Scenario`의 `events` 줄 다음에 `    enemies: list[EnemySpec] = []  # decision 0032`

`contracts/models/__init__.py`:
- `from .world import GeoPoint, Operation, Polygon, VehicleSpec, VehicleState` → `from .world import EnemySpec, GeoPoint, Operation, Polygon, VehicleSpec, VehicleState`
- `_MODELS` 첫 줄 `GeoPoint, Polygon, VehicleSpec, VehicleState, Operation,` → `GeoPoint, Polygon, VehicleSpec, VehicleState, Operation, EnemySpec,`

- [ ] **Step 5: play 대응표와 화면 이름표**

`modules/play/actions/expand_action.py`의 `TABLE`에서 `"hold": (K.hold,) * 3,` 다음 줄에:

```python
    "strike_target": (K.strike, K.strike, None),  # decision 0033
```

`modules/cop-ui/src/features/editor/describe.ts`의 `ACTION_LABEL`에서 `hold: "대기",` 다음 줄에:

```ts
  strike_target: "표적 타격",
```

- [ ] **Step 6: 예시 JSON**

`scripts/gen_examples.py`:
- `from example_world import OPERATION, PLAYS, SCENARIO, SPECS, ZONE  # noqa: E402` → `from example_world import OPERATION, PLAYS, SCENARIO, SPECS, ZONE, gp  # noqa: E402`
- `from contracts.models import (  # noqa: E402` 목록에 `EnemySpec,` 추가
- `examples()`가 돌려주는 dict에서 `"operation": OPERATION,` 다음 줄에:

```python
        "enemy_spec": EnemySpec(id="boat1", kind="boat", speed_mps=1.0, appear_offset_ms=660_000,
                                pos=gp(37.985, 124.70), play_id="enemy_boat1"),  # fmt: skip
```

Run: `uv run python scripts/gen_examples.py`
Expected: `[gen_examples] 39 models + 6 scenes -> ...`

Run: `git status --short demo contracts/examples`
Expected: `?? contracts/examples/enemy_spec.json` 하나와, 기본값 칸이 붙은 예시 JSON 수정(`M contracts/examples/...`). `demo/` 아래 변경이 있으면 생성기가 남의 수정을 덮은 것이므로 `git checkout -- demo` 로 되돌린다(demo는 Part1-19에서 고친다).

- [ ] **Step 7: API.md**

`contracts/API.md` 1절 개념 표의 `| 시나리오 | ...` 줄 다음에:

```markdown
| 적 | 대본에 적은 적 하나: 등장 시각(`appear_offset_ms`)·위치(`pos` 또는 `from_enemy`의 현재 위치)·속도 + 따르는 플레이. 행동은 `move_to`·`patrol_route`·`hold`, 조건은 `arrived`·`time_elapsed`(`params.sec`)만. runtime·safety를 거치지 않고 sim이 움직인다(결정 0032) | `EnemySpec`, `Scenario.enemies` |
```

같은 절 `**표적이 필요한 행동**(\`watch_target\`, \`approach_target\`)` → `**표적이 필요한 행동**(\`watch_target\`, \`approach_target\`, \`strike_target\`)`. 그리고 `정해진 표적은 ...` 문단 다음에:

```markdown
**타격(결정 0033).** 선택지가 기체를 다른 플레이로 옮기면 그 기체에 `decision_id`(결정 id)와 `target_id`(카드의 표적)를 적는다. 전환 버튼·예비 이어받기로 옮긴 기체는 `decision_id`가 없다. `strike_target` step의 명령(`strike`)은 출처 `decision_id`와 params `target`(표적의 현재 위치)을 싣고, safety 규칙 1은 `decision_id` 없는 `strike`를 `no_provenance`로 막는다(규칙 2·3은 `target`으로 그대로). 타격 중 기체가 표적 100 m 안이면 sim이 표적을 무력화(`neutralized_ms`, 속도 0)하고 `target_neutralized` 카드(알림만)를 낸다. 결정으로 옮긴 기체가 기다리던 다른 카드는 같이 닫힌다.
```

2절 지표 문단 끝 목록 다음에 한 줄: `- \`mission_success\`: 표적 하나라도 무력화되면 참(결정 0033).`

3절 표에서 `| 1 | sim | ...apply_events... |` 다음 줄에:

```markdown
| 1.5 | sim | 적(결정 0032): `spawn_enemies(scenario, targets, t_ms, dt_ms) -> targets`, `steer_enemies(enemies, plays, targets, t_ms, dt_ms) -> targets` |
```

`| 8 | sim | ...advance... |` 다음 줄에:

```markdown
| 8.5 | sim | `resolve_strikes(states, targets, t_ms) -> (targets, list[Report])`(결정 0033) |
```

5절 표의 `| \`GET /plays\` ...` 줄 다음에:

```markdown
| `GET /enemies` | — | `EnemySpec[]`(시나리오의 적, Part1-21) |
```

- [ ] **Step 8: 통과 확인**

Run: `uv run pytest tests modules/play -q`
Expected: 전부 PASS.

Run (cop-ui 타입 검사와 테스트): `npx --prefix modules/cop-ui tsc -b modules/cop-ui` 그리고 `npm --prefix modules/cop-ui test --silent`
Expected: 오류 없음, vitest 전부 PASS. (tsc가 `contracts.gen.ts`의 새 `ActionKind`를 아직 모르면 Step 9 커밋 뒤 다시 돌린다 — check.sh가 TS를 다시 만든다.)

- [ ] **Step 9: 커밋**

```bash
git add contracts/models contracts/examples contracts/API.md modules/play/actions/expand_action.py modules/play/tests/test_expand_action.py modules/cop-ui/src/features/editor/describe.ts scripts/gen_examples.py tests/test_contracts.py
git commit -m "Part1-18: contracts for strike (decision 0033) and enemies (decision 0032): strike_target/strike/target_neutralized, VehicleState.decision_id, Target strike and enemy progress fields, EnemySpec and Scenario.enemies; play table row and editor label in the same commit

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Run: `git show --stat HEAD`
Expected: `contracts/schema/...`와 `modules/cop-ui/src/contracts.gen.ts`도 커밋에 들어 있음(check.sh 재생성). 없으면 `uv run python scripts/gen_contracts.py` 뒤 `git add contracts/schema modules/cop-ui/src/contracts.gen.ts` 하고 `git commit --amend --no-edit`.

Run: `npx --prefix modules/cop-ui tsc -b modules/cop-ui`
Expected: 오류 없음.

- [ ] **Step 10: ship과 완료 기록**

Run: `scripts/ship.sh`
Expected: `[ship] 완료: <sha> Part1-18: ...`

Run: `uv run python scripts/task.py done Part1-18`

---

### Task 2: runtime — 결정 id·승인 표적·카드 닫기 (Part2-21)

**Files:**
- Modify: `modules/runtime/actions/switch_play.py`
- Modify: `modules/runtime/actions/apply_decision.py`
- Modify: `modules/runtime/actions/enter_step.py`
- Modify: `modules/runtime/SPEC.md` (RT-03·RT-08·RT-09 완료 기준 끝에 한 마디)
- Test: `modules/runtime/tests/test_switch_play.py`, `test_apply_decision.py`, `test_enter_step.py`

**Interfaces:**
- Consumes: Task 1의 `VehicleState.decision_id`, `ActionKind.strike_target`, `expand_action(... strike_target ...) -> CommandKind.strike`.
- Produces: `switch_play(st, play)`가 `decision_id=None`. `apply_decision(states, plays, decision, reports)`가 `play_by_vehicle`로 옮긴 기체에 `decision_id=decision.id`, `target_id=rep.target_id`, 그 기체들의 미처리·선택지 있는 카드 닫기. `enter_step`의 명령 `provenance.decision_id = st.decision_id`, `strike_target`이면 `params["target"] = 표적 위치 dict`, 보고 카드 `target_id`는 정해진 표적 우선.

- [ ] **Step 1: 시작 기록**

Run: `uv run python scripts/task.py start Part2-21`
채팅으로 황승주에게: "Part2-21~23(결정 0033 타격 runtime·safety·sim)은 리드가 가져가서 함"

- [ ] **Step 2: 실패 테스트 쓰기**

`modules/runtime/tests/test_switch_play.py` 끝에:

```python
def test_switch_clears_decision_id():
    st = VehicleState(id="d2", t_ms=0, pos=GeoPoint(lat=37, lon=126), heading_deg=0,
                      battery_pct=80, status="active", decision_id="dec-3")  # fmt: skip
    assert switch_play(st, PLAY).decision_id is None
```

`modules/runtime/tests/test_apply_decision.py` 끝에(`PLAYS`에 strike 플레이를 쓰므로 함수 안에서 만든다):

```python
STRIKE_BOTH = Choice(id="strike_both", label="함께 타격",
                     play_by_vehicle={"d2": "strike", "usv": "strike"})  # fmt: skip
ASK_D2 = Report(id="r-d2", t_ms=0, kind="target_detected", vehicle_id="d2", target_id="fast1",
                text="타격 승인 요청", choices=[STRIKE_BOTH])  # fmt: skip
ASK_USV = Report(id="r-usv", t_ms=0, kind="target_detected", vehicle_id="usv", target_id="fast1",
                 text="타격 승인 요청", choices=[STRIKE_BOTH])  # fmt: skip


def _strike_world():
    plays = {**PLAYS, "strike": play("strike")}
    states = [vs("d2", "track_fast", pending_report_id="r-d2", target_id="fast1"),
              vs("usv", "track_fast_sea", pending_report_id="r-usv", target_id="fast1")]  # fmt: skip
    return plays, states


def test_moved_vehicles_carry_the_decision_and_the_card_target():
    plays, states = _strike_world()
    out, _ = apply_decision(states, plays, decide("strike_both", "r-d2"), [ASK_D2, ASK_USV])
    got = {s.id: (s.play_id, s.decision_id, s.target_id) for s in out}
    assert got == {"d2": ("strike", "dec1", "fast1"), "usv": ("strike", "dec1", "fast1")}


def test_moved_vehicles_open_cards_close():
    plays, states = _strike_world()
    _, reports = apply_decision(states, plays, decide("strike_both", "r-d2"), [ASK_D2, ASK_USV])
    assert [(r.id, r.resolved_ms, r.decision_id) for r in reports] == [
        ("r-d2", 660_000, "dec1"),
        ("r-usv", 660_000, "dec1"),
    ]
```

`modules/runtime/tests/test_enter_step.py` 끝에:

```python
def test_strike_command_carries_decision_and_target_position():
    tg = boat("fast1", 900)
    st, cmd, rep = run(Action(kind="strike_target", params={"target": "operator", "distance_m": 0}),
                       [tg], domain="sea", target_id="fast1", decision_id="dec-3")  # fmt: skip
    assert cmd.kind == "strike" and cmd.provenance.decision_id == "dec-3"
    assert cmd.params == {"distance_m": 0, "target_id": "fast1", "target": tg.pos.model_dump()}
    assert rep is None and st.target_id == "fast1"


def test_report_card_names_the_tracked_target():
    ask = ReportSpec(text="타격 승인 요청", choices=[Choice(id="strike_d2", label="타격")])
    st, cmd, rep = run(Action(kind="watch_target", params={"target": "operator", "distance_m": 300}),
                       [boat("boat1", 300, ("d1",)), boat("fast1", 600, ("d1",))],
                       report=ask, target_id="fast1")  # fmt: skip
    assert rep.target_id == "fast1" and st.pending_report_id == rep.id
```

- [ ] **Step 3: 실패 확인**

Run: `uv run pytest modules/runtime -n 0 -q`
Expected: 새 테스트 5개 FAIL(`decision_id`가 지워지지 않음 / `None != "dec1"` / `r-usv` resolved_ms None / `provenance.decision_id is None` / `rep.target_id == "boat1"`).

- [ ] **Step 4: 구현**

`modules/runtime/actions/switch_play.py`의 update dict에서 `"resume_step_id": None,` 다음 줄에 `            "decision_id": None,`

`modules/runtime/actions/apply_decision.py`의 `apply_decision` 본문을 다음으로 바꾼다(`_choice_exit`는 그대로):

```python
def apply_decision(
    states: list[VehicleState], plays: dict[str, Play], decision: Decision, reports: list[Report]
) -> tuple[list[VehicleState], list[Report]]:
    rep = next(r for r in reports if r.id == decision.report_id)
    ch = next(c for c in rep.choices if c.id == decision.choice_id)
    done = {"resolved_ms": decision.t_ms, "decision_id": decision.id}
    moved = set(ch.play_by_vehicle)

    def closes(r: Report) -> bool:  # this card, and cards the moved vehicles were waiting on
        return r.id == rep.id or (r.vehicle_id in moved and bool(r.choices) and not r.resolved_ms)

    reports = [r.model_copy(update=done) if closes(r) else r for r in reports]
    out = []
    for s in states:
        if rep.kind == "target_select" and s.id == rep.vehicle_id:
            s = s.model_copy(
                update={"target_id": ch.id, "pending_report_id": None, "entered_step": False}
            )
        elif s.id in moved:  # decision 0033: the strike step needs who approved and what
            s = switch_play(s, plays[ch.play_by_vehicle[s.id]])
            s = s.model_copy(update={"decision_id": decision.id, "target_id": rep.target_id})
        elif s.id == rep.vehicle_id:
            s = s.model_copy(update={"pending_report_id": None, **_choice_exit(s, plays, ch.id)})
        out.append(s)
    return out, reports
```

docstring 둘째 줄 끝에 ` 옮긴 기체에는 결정 id·카드 표적(결정 0033).`을 붙인다.

`modules/runtime/actions/enter_step.py`:
- `TARGET_ACTIONS = ("watch_target", "approach_target")` → `TARGET_ACTIONS = ("watch_target", "approach_target", "strike_target")`
- `params = {k: v for k, v in params.items() if k != "target"} | {"target_id": tid}` 다음 줄에(같은 if 블록 안):

```python
        if step.do.kind.value == "strike_target":  # decision 0033: safety rules 2·3 see where
            tg = next((t for t in targets if t.id == tid), None)
            params |= {"target": tg.pos.model_dump()} if tg else {}
```

- `prov = Provenance(source="play_step", play_id=play.id, step_id=step.id, issued_ms=t_ms)` →

```python
    prov = Provenance(source="play_step", play_id=play.id, step_id=step.id, issued_ms=t_ms,
                      decision_id=st.decision_id)  # fmt: skip
```

- `seen = next((tg.id for tg in targets if st.id in tg.seen_by), None)` → `seen = upd.get("target_id") or next((tg.id for tg in targets if st.id in tg.seen_by), None)`

Run: `wc -l modules/runtime/actions/enter_step.py`
Expected: 80 이하.

- [ ] **Step 5: 통과 확인**

Run: `uv run pytest modules/runtime modules/gateway -q`
Expected: 전부 PASS(gateway의 `test_one_decision_switches_four_vehicles`가 그대로 통과해야 한다).

- [ ] **Step 6: SPEC 한 마디와 커밋**

`modules/runtime/SPEC.md`의 RT-03 행 완료 기준 칸 끝에 ` · 결정 0033: 옮긴 기체에 decision_id·카드 표적, 그 기체의 열린 카드 닫기`, RT-08 행 끝에 ` · 결정 0033: 출처 decision_id, strike면 params target(표적 위치), 카드 표적은 정해진 표적 우선`, RT-09 행 끝에 ` · decision_id도 지움`.

```bash
git add modules/runtime
git commit -m "Part2-21: runtime strike approval (decision 0033): a choice stamps decision_id and the card target on the vehicles it moves and closes their open cards; strike commands carry decision_id and the target position; cards name the tracked target

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 7: ship과 완료 기록**

Run: `scripts/ship.sh` → `[ship] 완료`
Run: `uv run python scripts/task.py done Part2-21`

---

### Task 3: safety — 결정 없는 타격 차단 (Part2-22)

**Files:**
- Modify: `modules/safety/actions/check_command.py`
- Modify: `modules/safety/SPEC.md` (SFT-03 완료 기준 끝)
- Test: `modules/safety/tests/test_check_command.py`

**Interfaces:**
- Consumes: Task 1의 `CommandKind.strike`, `Provenance.decision_id`(기존 칸).
- Produces: `check_command`가 `kind == strike`이고 `provenance.decision_id`가 비면 `Block(reason="no_provenance", detail="운용자 결정 없는 타격", alternative=None)`.

- [ ] **Step 1: 시작 기록**

Run: `uv run python scripts/task.py start Part2-22`

- [ ] **Step 2: 실패 테스트 쓰기**

`modules/safety/tests/test_check_command.py` 끝에:

```python
def strike(target: GeoPoint, decision_id: str | None) -> Command:
    prov = Provenance(source="play_step", play_id="ok", step_id="s1", issued_ms=0,
                      decision_id=decision_id)  # fmt: skip
    return Command(id="c1", vehicle_id="d1", kind="strike", provenance=prov,
                   params={"target_id": "fast1", "distance_m": 0, "target": target.model_dump()})  # fmt: skip


def test_strike_with_operator_decision_passes():
    assert isinstance(check(strike(P(37.06, 126.06), "dec-3")), PassedCommand)


def test_strike_without_decision_is_blocked():
    b = check(strike(P(37.06, 126.06), None))
    assert isinstance(b, Block) and b.reason == "no_provenance" and b.alternative is None
    assert b.detail == "운용자 결정 없는 타격"


def test_strike_at_a_target_outside_the_zone_is_blocked():
    b = check(strike(P(37.2, 126.05), "dec-3"))
    assert isinstance(b, Block) and b.reason == "outside_zone"
```

- [ ] **Step 3: 실패 확인**

Run: `uv run pytest modules/safety -n 0 -q`
Expected: `test_strike_without_decision_is_blocked` FAIL(PassedCommand가 나옴). 나머지 둘은 이미 PASS여도 된다(규칙 2·3은 params target으로 기존 코드가 처리).

- [ ] **Step 4: 구현**

`modules/safety/actions/check_command.py`:
- import 목록에 `CommandKind,` 추가.
- `_no_provenance`의 `if p is None:\n        return True` 다음에:

```python
    if cmd.kind == CommandKind.strike and not p.decision_id:  # decision 0033
        return True
```

- `check_command` 안 `return block("no_provenance", "출처 없음")` →

```python
        why = "운용자 결정 없는 타격" if cmd.kind == CommandKind.strike else "출처 없음"
        return block("no_provenance", why)
```

Run: `wc -l modules/safety/actions/check_command.py` → 80 이하.

- [ ] **Step 5: 통과 확인**

Run: `uv run pytest modules/safety modules/gateway -q`
Expected: 전부 PASS.

- [ ] **Step 6: SPEC 한 마디와 커밋**

`modules/safety/SPEC.md` SFT-03 행 완료 기준 끝에 ` · 결정 0033: strike는 출처 decision_id 없으면 no_provenance`.

```bash
git add modules/safety
git commit -m "Part2-22: safety rule 1 blocks a strike without an operator decision id (decision 0033)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 7: ship과 완료 기록**

Run: `scripts/ship.sh`, `uv run python scripts/task.py done Part2-22`

---

### Task 4: sim 타격 이동·무력화 + 작전 성공 (Part2-23)

**Files:**
- Modify: `modules/sim/actions/advance_vehicles.py` (strike 분기)
- Create (new_action): `modules/sim/actions/resolve_strikes.py` (SIM-10), `modules/sim/tests/test_resolve_strikes.py`
- Modify: `modules/sim/__init__.py` (export)
- Modify: `modules/runtime/actions/update_metrics.py` (mission_success)
- Test: `modules/sim/tests/test_advance_vehicles.py`, `modules/runtime/tests/test_update_metrics.py`

**Interfaces:**
- Consumes: Task 1의 `CommandKind.strike`, `Target.neutralized_ms`, `ReportKind.target_neutralized`.
- Produces: `advance`가 strike를 `orbit_or_keep`으로(params `distance_m` 0이면 표적에 붙음). `from modules.sim import resolve_strikes`; `resolve_strikes(states: list[VehicleState], targets: list[Target], t_ms: int) -> tuple[list[Target], list[Report]]`, 사거리 `STRIKE_RANGE_M = 100.0`, 카드 `Report(id=f"rep-{vid}-{t_ms}", kind="target_neutralized", vehicle_id, target_id, text=f"{tid} 무력화({vid})")`. `update_metrics`가 무력화 표적이 있으면 `mission_success=True`.

- [ ] **Step 1: 시작 기록과 새 액션**

Run: `uv run python scripts/task.py start Part2-23`
채팅으로 최동호에게: "sim에 resolve_strikes(SIM-10) 추가하고 advance에 strike 분기 한 줄 넣음(결정 0033)"

Run: `uv run python scripts/new_action.py sim resolve_strikes "타격 중 기체가 표적 100 m 안이면 표적 무력화(neutralized_ms, 속도 0)와 결과 카드" --inputs "states, targets, t_ms" --outputs "(targets, list[Report])" --done "100 m 안·밖, 이미 무력화면 카드 없음, 같은 틱 두 기체면 카드 하나(결정 0033)"`
Expected: `modules/sim/SPEC.md`에 SIM-10 행, `modules/sim/actions/resolve_strikes.py`, `modules/sim/tests/test_resolve_strikes.py` 생성.

- [ ] **Step 2: 실패 테스트 쓰기**

`modules/sim/tests/test_resolve_strikes.py` 전체를 다음으로:

```python
from contracts.models import Command, GeoPoint, PassedCommand, Target, VehicleState
from modules.sim.actions.resolve_strikes import resolve_strikes
from shared.geo import offset_latlon

HOME = GeoPoint(lat=37.95, lon=124.70)
T = 1_000_000


def _at(north_m: float) -> GeoPoint:
    lat, lon = offset_latlon(HOME.lat, HOME.lon, 0, north_m)
    return GeoPoint(lat=lat, lon=lon)


def _striker(vid: str, kind: str = "strike", target_id: str = "fast1") -> VehicleState:
    cmd = Command(id=f"c-{vid}", vehicle_id=vid, kind=kind, params={"target_id": target_id})
    return VehicleState(id=vid, t_ms=T, pos=HOME, heading_deg=0, battery_pct=80, status="active",
                        active=PassedCommand(command=cmd, checks=[], passed_ms=0))  # fmt: skip


def _fast1(north_m: float, neutralized_ms: int | None = None) -> Target:
    return Target(id="fast1", kind="fast_boat", pos=_at(north_m), vel_east_mps=-2,
                  vel_north_mps=6, first_seen_ms=0, last_seen_ms=0,
                  neutralized_ms=neutralized_ms)  # fmt: skip


def test_within_100_m_neutralizes_and_stops_the_target():
    targets, cards = resolve_strikes([_striker("d2")], [_fast1(60)], T)
    tg = targets[0]
    assert (tg.neutralized_ms, tg.vel_east_mps, tg.vel_north_mps) == (T, 0, 0)
    assert [(c.id, c.kind.value, c.vehicle_id, c.target_id, c.text) for c in cards] == [
        (f"rep-d2-{T}", "target_neutralized", "d2", "fast1", "fast1 무력화(d2)")
    ]
    assert cards[0].choices == []


def test_beyond_100_m_does_nothing():
    targets, cards = resolve_strikes([_striker("d2")], [_fast1(150)], T)
    assert targets[0].neutralized_ms is None and cards == []


def test_already_neutralized_gives_no_card():
    targets, cards = resolve_strikes([_striker("d2")], [_fast1(10, neutralized_ms=T - 200)], T)
    assert targets[0].neutralized_ms == T - 200 and cards == []


def test_other_commands_never_strike():
    targets, cards = resolve_strikes([_striker("d2", kind="keep_distance")], [_fast1(10)], T)
    assert targets[0].neutralized_ms is None and cards == []


def test_two_strikers_in_one_tick_give_one_card():
    targets, cards = resolve_strikes([_striker("d2"), _striker("usv")], [_fast1(10)], T)
    assert targets[0].neutralized_ms == T and [c.vehicle_id for c in cards] == ["d2"]
```

`modules/sim/tests/test_advance_vehicles.py` 끝에(`Target` import 추가):

```python
def test_strike_flies_onto_the_target():
    tg = Target(id="fast1", kind="fast_boat", pos=_at(north_m=100), vel_east_mps=0,
                vel_north_mps=0, first_seen_ms=0, last_seen_ms=0)  # fmt: skip
    pc = _passed(CommandKind.strike, target_id="fast1", distance_m=0)
    (st,) = advance_vehicles([_state(status=VehicleStatus.active)], SPECS, [pc], 1000, [tg])
    assert dist_m(st.pos, tg.pos) == pytest.approx(90, abs=0.5)
```

`modules/runtime/tests/test_update_metrics.py` 끝에:

```python
def test_mission_succeeds_once_a_target_is_neutralized():
    struck = Target(id="fast1", kind="fast_boat", pos=G, vel_east_mps=0, vel_north_mps=0,
                    first_seen_ms=0, last_seen_ms=0, neutralized_ms=5000)  # fmt: skip
    m = update_metrics(Metrics(), TickOutcome(states=[vs("d2")], targets=[struck]))
    assert m.mission_success is True
    assert update_metrics(Metrics(), TickOutcome(states=[vs("d2")])).mission_success is None
```

- [ ] **Step 3: 실패 확인**

Run: `uv run pytest modules/sim modules/runtime -n 0 -q`
Expected: `test_resolve_strikes.py` 전부 FAIL(NotImplementedError), `test_strike_flies_onto_the_target` FAIL(움직이지 않음, 거리 100), `test_mission_succeeds...` FAIL(None).

- [ ] **Step 4: 구현**

`modules/sim/actions/resolve_strikes.py` 전체:

```python
"""SIM-10 resolve_strikes: 타격 중(active가 strike) 기체가 그 표적 100 m 안이면 표적을 무력화한다(결정 0033)
무력화 = neutralized_ms 기록 + 속도 0(다음 틱부터 apply_events가 움직이지 않음). 결과 카드는 알림만, 표적당 한 장.
SPEC: modules/sim/SPEC.md#SIM-10
"""

from contracts.models import CommandKind, Report, Target, VehicleState
from shared.geo import dist_m

STRIKE_RANGE_M = 100.0


def resolve_strikes(
    states: list[VehicleState], targets: list[Target], t_ms: int
) -> tuple[list[Target], list[Report]]:
    by_id = {t.id: t for t in targets}
    cards: list[Report] = []
    for st in states:
        cmd = st.active.command if st.active else None
        if cmd is None or cmd.kind != CommandKind.strike:
            continue
        tg = by_id.get(cmd.params.get("target_id"))
        if tg is None or tg.neutralized_ms is not None or dist_m(st.pos, tg.pos) > STRIKE_RANGE_M:
            continue
        by_id[tg.id] = tg.model_copy(
            update={"neutralized_ms": t_ms, "vel_east_mps": 0.0, "vel_north_mps": 0.0}
        )
        cards.append(Report(id=f"rep-{st.id}-{t_ms}", t_ms=t_ms, kind="target_neutralized",
                            vehicle_id=st.id, target_id=tg.id, text=f"{tg.id} 무력화({st.id})"))  # fmt: skip
    return [by_id[t.id] for t in targets], cards
```

`modules/sim/actions/advance_vehicles.py`: `if kind in (K.orbit, K.keep_distance):` → `if kind in (K.orbit, K.keep_distance, K.strike):  # strike: fly onto the target (decision 0033)`

`modules/sim/__init__.py`: import 줄 `from modules.sim.actions.resolve_strikes import resolve_strikes`를 `load_scenario_json` 줄 다음에 추가하고 `__all__`에 `"resolve_strikes",`(`"load_scenario_json",` 다음).

`modules/runtime/actions/update_metrics.py`의 `return m` 바로 앞에:

```python
    if any(t.neutralized_ms is not None for t in outcome.targets):  # decision 0033
        m.mission_success = True
```

- [ ] **Step 5: 통과 확인**

Run: `uv run pytest modules/sim modules/runtime modules/gateway -q`
Expected: 전부 PASS.

- [ ] **Step 6: SPEC 한 마디와 커밋**

`modules/sim/SPEC.md` SIM-08 행 완료 기준 끝에 ` · strike도 orbit_or_keep(결정 0033)`, `modules/runtime/SPEC.md` RT-04 행 끝에 ` · mission_success = 표적 하나라도 무력화(결정 0033)`.

```bash
git add modules/sim modules/runtime
git commit -m "Part2-23: sim resolve_strikes SIM-10 (strike within 100 m neutralizes the target, one alert card), advance flies strike onto the target, mission_success once a target is neutralized (decision 0033)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 7: ship과 완료 기록**

Run: `scripts/ship.sh`, `uv run python scripts/task.py done Part2-23`

---

### Task 5: gateway — 틱에 무력화 연결, 타격 기록 줄 (Part2-24)

**Files:**
- Modify: `modules/gateway/engine.py`
- Modify: `modules/gateway/actions/tick_log.py`
- Test: `modules/gateway/tests/test_tick_log.py`, `modules/gateway/tests/test_engine.py`

**Interfaces:**
- Consumes: Task 4의 `resolve_strikes`.
- Produces: `tick_log(scenario, t_ms, dt_ms, inputs, blocks, passed: list[PassedCommand] = (), hits: list[Report] = ()) -> list[str]`. 새 줄 `"[계산] HH:MM:SS 타격 명령 통과: <기체> → <표적>, 운용자 결정 <dec> 확인"`, `"[계산] HH:MM:SS <카드 text>"`. 틱 순서 8 다음 8.5에서 무력화.

- [ ] **Step 1: 시작 기록**

Run: `uv run python scripts/task.py start Part2-24`
채팅으로 최동호에게: "Part2-24·25(engine.py 타격·적 연결)는 리드가 가져감"

- [ ] **Step 2: 실패 테스트 쓰기**

`modules/gateway/tests/test_tick_log.py` 끝에(import에 `Command`, `PassedCommand`, `Provenance`, `Report` 추가):

```python
def test_strike_pass_and_neutralized_lines():
    prov = Provenance(source="play_step", issued_ms=T, decision_id="dec-3")
    cmd = Command(id="c1", vehicle_id="d2", kind="strike", params={"target_id": "fast1"},
                  provenance=prov)  # fmt: skip
    hit = Report(id="r", t_ms=T, kind="target_neutralized", vehicle_id="d2", target_id="fast1",
                 text="fast1 무력화(d2)")  # fmt: skip
    lines = tick_log(SC, T + 200, 200, TickInputs(), [],
                     [PassedCommand(command=cmd, checks=[], passed_ms=T)], [hit])  # fmt: skip
    assert lines == [
        "[계산] 21:11:00 타격 명령 통과: d2 → fast1, 운용자 결정 dec-3 확인",
        "[계산] 21:11:00 fast1 무력화(d2)",
    ]
```

(시각 `T + 200`은 21:11:00.2라 `%H:%M:%S`로 21:11:00. 같은 틱에 사건 대본 줄이 없도록 T+200을 쓴다.)

`modules/gateway/tests/test_engine.py` 끝에:

```python
def test_strike_next_to_a_target_neutralizes_it_and_logs():
    from dataclasses import replace

    from contracts.models import Command, PassedCommand, Target, VehicleStatus

    es = init_engine(SC)
    d1 = es.states[0]
    tg = Target(id="x", kind="boat", pos=d1.pos, vel_east_mps=0, vel_north_mps=0,
                first_seen_ms=0, last_seen_ms=0)  # fmt: skip
    cmd = Command(
        id="c", vehicle_id=d1.id, kind="strike", params={"target_id": "x", "distance_m": 0}
    )
    # model_copy does not validate: give the enum, not the string (step_vehicle reads .value)
    d1 = d1.model_copy(update={"entered_step": True, "status": VehicleStatus.active,
                               "active": PassedCommand(command=cmd, checks=[], passed_ms=0)})  # fmt: skip
    es = replace(es, states=[d1, *es.states[1:]], targets=[tg])
    es, fr = tick(es, TickInputs())
    assert fr.targets[0].neutralized_ms == es.t_ms
    assert any(line.endswith("x 무력화(d1)") for line in fr.log)
    assert fr.metrics.mission_success is True
```

- [ ] **Step 3: 실패 확인**

Run: `uv run pytest modules/gateway -n 0 -q`
Expected: 두 테스트 FAIL(tick_log 인자 개수 TypeError / neutralized_ms None).

- [ ] **Step 4: 구현**

`modules/gateway/actions/tick_log.py`:

```python
"""GW-07 tick_log: 이번 틱의 기록 줄(Frame.log). [대본]은 사건 대본, [계산]은 엔진이 계산한 것(09 4.5)
시각은 KST(결정 0012). 타격 통과·무력화 줄은 결정 0033.
SPEC: modules/gateway/SPEC.md#GW-07
"""

from datetime import datetime

from contracts.models import Block, CommandKind, PassedCommand, Report, Scenario, TickInputs
from shared.kst import KST


def tick_log(
    scenario: Scenario,
    t_ms: int,
    dt_ms: int,
    inputs: TickInputs,
    blocks: list[Block],
    passed: list[PassedCommand] = (),
    hits: list[Report] = (),
) -> list[str]:
    hhmm = datetime.fromtimestamp(t_ms / 1000, KST).strftime("%H:%M:%S")
    start = scenario.operation.started_ms
    lines = [
        f"[대본] {hhmm} {ev.kind} {ev.params.get('id', '')}"
        for ev in scenario.events
        if t_ms - dt_ms < start + ev.offset_ms <= t_ms
    ]
    lines += [f"[계산] {hhmm} 결정 {d.id} → {d.choice_id}" for d in inputs.decisions]
    lines += [f"[계산] {hhmm} 전환 {i.id} {i.status}" for i in inputs.injections]
    lines += [f"[계산] {hhmm} 직접 조종 {d.id} {d.vehicle_id}" for d in inputs.direct]
    lines += [f"[계산] {hhmm} 차단 {b.vehicle_id} {b.reason.value}" for b in blocks]
    lines += [
        f"[계산] {hhmm} 타격 명령 통과: {c.vehicle_id} → {c.params.get('target_id')}, "
        f"운용자 결정 {c.provenance.decision_id} 확인"
        for c in (pc.command for pc in passed)
        if c.kind == CommandKind.strike
    ]
    lines += [f"[계산] {hhmm} {r.text}" for r in hits]
    return lines
```

`modules/gateway/engine.py`:
- `from modules.sim import advance, apply_events` → `from modules.sim import advance, apply_events, resolve_strikes`
- `states = advance(states, specs, passed, dt, targets)  # 8` 다음 줄에:

```python
    targets, hits = resolve_strikes(states, targets, t)  # 8.5 decision 0033
```

- `new_reports += cards` → `new_reports += cards + hits`
- 마지막 줄 `tick_log(sc, t, dt, inputs, blocks)` → `tick_log(sc, t, dt, inputs, blocks, passed, hits)`

- [ ] **Step 5: 통과 확인**

Run: `uv run pytest modules/gateway -q`
Expected: 전부 PASS. 그리고 `uv run python scripts/smoke.py` → 통과.

- [ ] **Step 6: 커밋**

```bash
git add modules/gateway
git commit -m "Part2-24: tick resolves strikes after advance (8.5) and logs each passed strike with its operator decision and each neutralized target (decision 0033)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 7: ship과 완료 기록**

Run: `scripts/ship.sh`, `uv run python scripts/task.py done Part2-24`

---

### Task 6: 적 등장·진행 (Part2-25)

**Files:**
- Create (new_action): `modules/sim/actions/spawn_enemies.py` (SIM-11), `modules/sim/tests/test_spawn_enemies.py`
- Create (new_action): `modules/sim/actions/steer_enemies.py` (SIM-12), `modules/sim/tests/test_steer_enemies.py`
- Modify: `modules/sim/__init__.py`, `modules/gateway/engine.py`, `modules/gateway/actions/tick_log.py`
- Test: `modules/gateway/tests/test_engine.py`, `modules/gateway/tests/test_tick_log.py`

**Interfaces:**
- Consumes: Task 1의 `EnemySpec`, `Scenario.enemies`, `Target.play_id/step_id/waypoint_idx/step_since_ms/neutralized_ms`.
- Produces: `spawn_enemies(scenario: Scenario, targets: list[Target], t_ms: int, dt_ms: int) -> list[Target]`; `steer_enemies(enemies: list[EnemySpec], plays: dict[str, Play], targets: list[Target], t_ms: int, dt_ms: int) -> list[Target]`; 둘 다 `from modules.sim import ...`. tick_log 새 줄 `"[대본] HH:MM:SS 적 등장 <id>"`.

- [ ] **Step 1: 시작 기록과 새 액션 둘**

Run: `uv run python scripts/task.py start Part2-25`

Run: `uv run python scripts/new_action.py sim spawn_enemies "적(결정 0032)이 등장 시각에 pos 또는 from_enemy 위치에서 Target으로 나타남, 진행 상태는 플레이 entry" --inputs "scenario, targets, t_ms, dt_ms" --outputs "targets" --done "등장 틱에만 하나, from_enemy 위치, play_id·step_id·step_since_ms"`

Run: `uv run python scripts/new_action.py sim steer_enemies "적의 현재 step 행동(move_to·patrol_route·hold)대로 속도만 정하고 arrived·time_elapsed로 step 전이, 위치는 apply_events가 옮김" --inputs "enemies, plays, targets, t_ms, dt_ms" --outputs "targets" --done "목적지 방향 속도, 도착 틱에 위치 맞춤·속도 0·waypoint -1, time_elapsed 전이, 무력화면 그대로"`

Expected: SIM-11·SIM-12 행과 파일·실패 테스트.

- [ ] **Step 2: 실패 테스트 쓰기**

`modules/sim/tests/test_spawn_enemies.py` 전체:

```python
from contracts.models import (
    Action,
    EnemySpec,
    GeoPoint,
    Operation,
    Play,
    Polygon,
    Scenario,
    Step,
    Target,
)
from modules.sim.actions.spawn_enemies import spawn_enemies

START = 1_791_633_600_000
G = GeoPoint(lat=37.985, lon=124.70)
ZONE = Polygon(points=[G, GeoPoint(lat=37.9, lon=124.7), GeoPoint(lat=37.9, lon=124.8)])
PLAY = Play(id="enemy_boat1", name="b", domains=["sea"], entry="go", approved=True,
            steps=[Step(id="go", name="go", do=Action(kind="hold"))])  # fmt: skip
SC = Scenario(id="s", vehicles=[], plays=[PLAY],
              operation=Operation(id="op1", name="op", area=ZONE, zone=ZONE, vehicle_ids=[],
                                  started_ms=START),
              enemies=[EnemySpec(id="boat1", kind="boat", speed_mps=1, appear_offset_ms=660_000,
                                 pos=G, play_id="enemy_boat1"),
                       EnemySpec(id="fast1", kind="fast_boat", speed_mps=6.3,
                                 appear_offset_ms=1_380_000, from_enemy="boat1",
                                 play_id="enemy_boat1")])  # fmt: skip
T1, T2 = START + 660_000, START + 1_380_000


def test_enemy_appears_only_in_its_tick_with_play_progress():
    assert spawn_enemies(SC, [], T1 - 200, 200) == []
    (tg,) = spawn_enemies(SC, [], T1, 200)
    assert (tg.id, tg.kind.value, tg.pos, tg.vel_east_mps, tg.vel_north_mps) == (
        "boat1",
        "boat",
        G,
        0,
        0,
    )
    assert (tg.play_id, tg.step_id, tg.waypoint_idx, tg.step_since_ms) == (
        "enemy_boat1",
        "go",
        0,
        T1,
    )
    assert spawn_enemies(SC, [tg], T1 + 200, 200) == [tg]


def test_from_enemy_appears_at_that_enemys_current_position():
    moved = GeoPoint(lat=37.97, lon=124.70)
    boat1 = Target(id="boat1", kind="boat", pos=moved, vel_east_mps=0, vel_north_mps=-1,
                   first_seen_ms=0, last_seen_ms=0)  # fmt: skip
    out = spawn_enemies(SC, [boat1], T2, 200)
    assert [t.id for t in out] == ["boat1", "fast1"] and out[1].pos == moved
```

`modules/sim/tests/test_steer_enemies.py` 전체:

```python
import pytest

from contracts.models import (
    Action,
    Condition,
    EnemySpec,
    Exit,
    GeoPoint,
    Play,
    Step,
    Target,
)
from modules.sim.actions.steer_enemies import steer_enemies
from shared.geo import offset_latlon

HOME = GeoPoint(lat=37.98, lon=124.70)
T = 1_000_000


def _at(east_m: float = 0, north_m: float = 0) -> GeoPoint:
    lat, lon = offset_latlon(HOME.lat, HOME.lon, east_m, north_m)
    return GeoPoint(lat=lat, lon=lon)


DEST = _at(east_m=1000)
PLAY = Play(id="enemy_fast1", name="f", domains=["sea"], entry="run", approved=True, steps=[
    Step(id="run", name="run", do=Action(kind="move_to", params={"target": DEST.model_dump()}),
         on=[Exit(cond=Condition(kind="arrived"), go_step="wait")]),
    Step(id="wait", name="wait", do=Action(kind="hold"),
         on=[Exit(cond=Condition(kind="time_elapsed", params={"sec": 60}), go_step="run")]),
])  # fmt: skip
ENEMIES = [EnemySpec(id="fast1", kind="fast_boat", speed_mps=5, appear_offset_ms=0,
                     pos=HOME, play_id="enemy_fast1")]  # fmt: skip


def _fast1(pos: GeoPoint = HOME, step: str = "run", **kw) -> Target:
    return Target(id="fast1", kind="fast_boat", pos=pos, vel_east_mps=0, vel_north_mps=0,
                  first_seen_ms=0, last_seen_ms=0, play_id="enemy_fast1", step_id=step,
                  step_since_ms=T - 200, **kw)  # fmt: skip


def steer(tg: Target, t_ms: int = T) -> Target:
    (out,) = steer_enemies(ENEMIES, {PLAY.id: PLAY}, [tg], t_ms, 200)
    return out


def test_move_to_sets_speed_toward_the_destination():
    out = steer(_fast1())
    assert out.vel_east_mps == pytest.approx(5, abs=0.01)
    assert out.vel_north_mps == pytest.approx(0, abs=0.01)


def test_arrival_snaps_to_destination_and_stops():
    out = steer(_fast1(pos=_at(east_m=999.5)))
    assert (out.pos, out.vel_east_mps, out.vel_north_mps, out.waypoint_idx) == (DEST, 0, 0, -1)


def test_arrived_exit_moves_to_the_next_step():
    out = steer(_fast1(pos=DEST, waypoint_idx=-1))
    assert (out.step_id, out.waypoint_idx, out.step_since_ms) == ("wait", 0, T)
    assert (out.vel_east_mps, out.vel_north_mps) == (0, 0)


def test_time_elapsed_exit_waits_for_its_seconds():
    held = _fast1(pos=DEST, step="wait")
    assert steer(held, T + 30_000).step_id == "wait"
    assert steer(held, T - 200 + 60_000).step_id == "run"


def test_neutralized_enemy_stays_still():
    struck = _fast1(neutralized_ms=T - 1000)
    assert steer(struck) == struck


def test_targets_without_a_play_are_left_alone():
    plain = Target(id="boat9", kind="boat", pos=HOME, vel_east_mps=0, vel_north_mps=-1,
                   first_seen_ms=0, last_seen_ms=0)  # fmt: skip
    assert steer_enemies(ENEMIES, {PLAY.id: PLAY}, [plain], T, 200) == [plain]
```

`modules/gateway/tests/test_tick_log.py` 끝에:

```python
def test_enemy_appearance_is_a_script_line():
    from contracts.models import EnemySpec

    sc = SC.model_copy(update={"events": [], "enemies": [
        EnemySpec(id="boat1", kind="boat", speed_mps=1, appear_offset_ms=660_000, pos=G,
                  play_id="p")]})  # fmt: skip
    assert tick_log(sc, T, 200, TickInputs(), []) == ["[대본] 21:11:00 적 등장 boat1"]
```

`modules/gateway/tests/test_engine.py` 끝에:

```python
def test_enemy_appears_and_moves_by_its_play():
    from contracts.models import Action, EnemySpec, Play, Step

    dest = {"lat": 37.985, "lon": 124.75, "alt_m": 0}
    play = Play(id="enemy_x", name="x", domains=["sea"], entry="go", approved=True,
                steps=[Step(id="go", name="go", do=Action(kind="move_to", params={"target": dest}))])  # fmt: skip
    enemy = EnemySpec(id="x", kind="boat", speed_mps=5, appear_offset_ms=SC.tick_ms,
                      pos={"lat": 37.985, "lon": 124.70}, play_id="enemy_x")  # fmt: skip
    sc = SC.model_copy(update={"enemies": [enemy], "plays": [*SC.plays, play]})
    es = init_engine(sc)
    es, fr = tick(es, TickInputs())
    first = next(t for t in fr.targets if t.id == "x")
    assert first.vel_east_mps > 4.9 and any("적 등장 x" in line for line in fr.log)
    es, fr = tick(es, TickInputs())
    assert next(t for t in fr.targets if t.id == "x").pos.lon > first.pos.lon
```

- [ ] **Step 3: 실패 확인**

Run: `uv run pytest modules/sim modules/gateway -n 0 -q`
Expected: 새 sim 테스트 FAIL(NotImplementedError), gateway 두 테스트 FAIL(등장 줄 없음 / 표적 x 없음 StopIteration).

- [ ] **Step 4: 구현**

`modules/sim/actions/spawn_enemies.py` 전체:

```python
"""SIM-11 spawn_enemies: 적(결정 0032)이 started_ms + appear_offset_ms 틱에 Target으로 나타난다
위치는 pos, 또는 from_enemy 적의 지금 위치. 진행 상태는 그 플레이의 entry step에서 시작.
SPEC: modules/sim/SPEC.md#SIM-11
"""

from contracts.models import Scenario, Target


def spawn_enemies(scenario: Scenario, targets: list[Target], t_ms: int, dt_ms: int) -> list[Target]:
    start = scenario.operation.started_ms
    entry = {p.id: p.entry for p in scenario.plays}
    out = list(targets)
    for e in scenario.enemies:
        if not t_ms - dt_ms < start + e.appear_offset_ms <= t_ms:
            continue
        src = next((t for t in out if t.id == e.from_enemy), None)
        out.append(Target(id=e.id, kind=e.kind, pos=src.pos if src else e.pos,
                          vel_east_mps=0, vel_north_mps=0, first_seen_ms=0, last_seen_ms=0,
                          play_id=e.play_id, step_id=entry[e.play_id], step_since_ms=t_ms))  # fmt: skip
    return out
```

`modules/sim/actions/steer_enemies.py` 전체:

```python
"""SIM-12 steer_enemies: 적(결정 0032)의 지금 step 행동대로 속도만 정하고 arrived·time_elapsed로 step을 넘긴다
위치는 다음 틱 apply_events가 속도로 옮긴다. 이번 틱 안에 닿으면 위치를 목적지로 맞추고 멈춘다.
행동은 move_to·patrol_route·hold만. runtime·safety를 거치지 않는다. 무력화된 적은 그대로.
SPEC: modules/sim/SPEC.md#SIM-12
"""

from contracts.models import ConditionKind, EnemySpec, GeoPoint, Play, Step, Target
from shared.geo import dist_m, enu_delta_m

STOP = {"vel_east_mps": 0.0, "vel_north_mps": 0.0}


def _dest(step: Step, idx: int) -> GeoPoint | None:
    p = step.do.params
    if step.do.kind.value == "move_to":
        return GeoPoint(**p["target"])
    if step.do.kind.value == "patrol_route":
        return GeoPoint(**p["route"][idx % len(p["route"])])
    return None  # hold


def _next_step(step: Step, tg: Target, t_ms: int) -> str | None:
    waited_ms = t_ms - (tg.step_since_ms or t_ms)
    for ex in step.on:
        if ex.cond.kind == ConditionKind.arrived and tg.waypoint_idx < 0:
            return ex.go_step
        sec = float(ex.cond.params.get("sec", 0))
        if ex.cond.kind == ConditionKind.time_elapsed and waited_ms >= sec * 1000:
            return ex.go_step
    return None


def _steer(tg: Target, step: Step, speed: float, dt_ms: int) -> Target:
    dest = _dest(step, tg.waypoint_idx) if tg.waypoint_idx >= 0 else None
    if dest is None:
        return tg.model_copy(update=STOP)
    d = dist_m(tg.pos, dest)
    if d <= speed * dt_ms / 1000:
        idx = -1 if step.do.kind.value == "move_to" else tg.waypoint_idx + 1
        return tg.model_copy(update={**STOP, "pos": dest, "waypoint_idx": idx})
    east, north = enu_delta_m(tg.pos.lat, tg.pos.lon, dest.lat, dest.lon)
    return tg.model_copy(
        update={"vel_east_mps": speed * east / d, "vel_north_mps": speed * north / d}
    )


def steer_enemies(
    enemies: list[EnemySpec], plays: dict[str, Play], targets: list[Target], t_ms: int, dt_ms: int
) -> list[Target]:
    speed = {e.id: e.speed_mps for e in enemies}
    out = []
    for tg in targets:
        play = plays.get(tg.play_id or "")
        if play is None or tg.neutralized_ms is not None:
            out.append(tg)
            continue
        step = next(s for s in play.steps if s.id == tg.step_id)
        nxt = _next_step(step, tg, t_ms)
        if nxt:
            tg = tg.model_copy(update={"step_id": nxt, "waypoint_idx": 0, "step_since_ms": t_ms})
            step = next(s for s in play.steps if s.id == nxt)
        out.append(_steer(tg, step, speed.get(tg.id, 0.0), dt_ms))
    return out
```

Run: `wc -l modules/sim/actions/spawn_enemies.py modules/sim/actions/steer_enemies.py` → 둘 다 80 이하.

`modules/sim/__init__.py`: import 두 줄(`from modules.sim.actions.spawn_enemies import spawn_enemies`, `from modules.sim.actions.steer_enemies import steer_enemies`)과 `__all__`에 `"spawn_enemies", "steer_enemies",`.

`modules/gateway/engine.py`:
- `from modules.sim import advance, apply_events, resolve_strikes` → `from modules.sim import advance, apply_events, resolve_strikes, spawn_enemies, steer_enemies`
- `states, targets = apply_events(sc, es.states, es.targets, t, dt)  # 1` 다음에:

```python
targets = steer_enemies(
    sc.enemies, plays, spawn_enemies(sc, targets, t, dt), t, dt
)  # 1.5 decision 0032
```

`modules/gateway/actions/tick_log.py`의 `lines = [...]` 사건 대본 줄 목록 다음에:

```python
    lines += [
        f"[대본] {hhmm} 적 등장 {e.id}"
        for e in scenario.enemies
        if t_ms - dt_ms < start + e.appear_offset_ms <= t_ms
    ]
```

docstring 둘째 줄 끝에 ` 적 등장 줄은 결정 0032.`

- [ ] **Step 5: 통과 확인**

Run: `uv run pytest modules/sim modules/gateway -q`
Expected: 전부 PASS. `uv run python scripts/smoke.py` 통과.

- [ ] **Step 6: 커밋**

```bash
git add modules/sim modules/gateway
git commit -m "Part2-25: enemies follow their plays (decision 0032): sim spawn_enemies SIM-11 and steer_enemies SIM-12 (speed and step only, apply_events moves them, no runtime/safety), tick step 1.5, '[대본] 적 등장' log line

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 7: ship과 완료 기록**

Run: `scripts/ship.sh`, `uv run python scripts/task.py done Part2-25`

---

## 다음(이 계획 밖)

- Part1-19 시나리오·플레이(리드): `scripts/example_world.py`에 boat1·fast1 enemies와 `enemy_boat1`·`enemy_fast1` 플레이, `track_fast` 수정·`track_fast_sea`·`strike`, 전환 버튼, 기체 capabilities에 `strike_target`, `spawn_target`·`split_target` 사건 삭제 → `gen_examples.py`로 `demo/` 갱신. 숫자는 Part2-19.
- Part1-20 화면, Part1-21 편집기 적 열 + `GET /enemies`.
