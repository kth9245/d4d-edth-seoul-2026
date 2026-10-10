# 경로 선택과 offset 행동 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 편집기 카드 패널에서 "경로 비행 + 반복" 행동과 경로 선택칸(고정·상대 경로)으로 경로를 고르고, 상대 경로는 카드 진입 때 기체 위치 기준으로 계산하며, 카드 연결에 T+ 시각 조건을 단다.

**Architecture:** 시나리오에 `routes`(RouteDef 목록)를 두고 gateway `GET /routes`로 편집기에 준다. 카드에는 고른 경로를 복사(`route` 또는 `offsets` + `route_name`)한다. runtime 새 액션 `route_command`가 카드 진입 때 offsets → 실제 좌표 route, 경로를 가진 `move_to` → `follow_route`(`loop: false`)로 바꾸고, sim `follow_route`가 `loop: false`면 끝점에서 멈춰 "도착"을 낸다. 새 조건 `at_time`은 `step_vehicle`이 작전 시작 시각과 비교한다.

**Tech Stack:** Python 3 · pydantic(contracts) · FastAPI · pytest / React · TypeScript · vitest

**Spec:** `docs/superpowers/specs/2026-10-10-route-select-design.md` (Part1-31, 결정 0044·0045)

## Global Constraints

- 작업은 worktree `.claude/worktrees/Part3-12.3`. 명령은 `$(...)` 없이 따로. 커밋 메시지는 `Part1-31: ...` 영어, 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- TDD(결정 0014). happy path(결정 0024). 액션 파일(`modules/<m>/actions/*.py`)은 80줄 이하, 새 액션은 `scripts/new_action.py`로.
- 계약 행동 종류는 그대로 두 개(`move_to`, `patrol_route`). 편집기에서만 "경로 비행" 하나로 보인다(결정 0045).
- 상대 경로 기준점은 항상 카드에 들어가는 순간의 기체 위치. `at_time`은 `params.offset_ms`(작전 시작 기준), `started_ms`가 없으면 성립하지 않는다.
- `time_elapsed`(적 대본 `params.sec`)는 건드리지 않는다.
- 남의 모듈: sim `follow_route`·gateway `engine.py`(최동호), runtime·play(황승주). 끝나면 채팅으로 알린다.
- 화면 색은 theme.css 토큰만.

## Review Focus

1. 반복을 끈 경로 비행이 끝점에 닿은 뒤에도 다시 첫 점으로 출발하면 안 되고 "도착"이 성립해야 한다 → Task 2 `test_one_way_route_stops_at_the_end_and_arrives`, `test_one_way_route_stays_after_arriving`.
2. `started_ms`를 못 받으면 T+ 조건이 즉시 성립하면 안 된다 → Task 4 `test_at_time_without_the_operation_start_never_fires`.
3. 상대 경로가 기체 위치가 아닌 곳(예: 홈, 첫 좌표)을 기준으로 계산되면 안 된다 → Task 3 `test_offsets_are_measured_from_where_the_vehicle_is`.
4. 행동을 경로 비행에서 다른 행동으로 바꾸면 경로 값(`route`, `offsets`, `route_name`)이 남으면 안 된다 → Task 6 `setActionKind` 테스트 `drops route values when the card leaves route flying`.
5. 지금 카드 값이 목록에 없는 경로(이름 없는 28점 경로, 점 하나 이동)여도 편집 패널이 값을 덮어쓰지 않고 보여 줘야 한다 → Task 6 `routeChoice` 테스트 `keeps an unnamed route as the current value`.

---

### Task 1: 계약 — RouteOffset · RouteDef · Scenario.routes · at_time

**Files:**
- Modify: `contracts/models/world.py`, `contracts/models/frame.py`, `contracts/models/enums.py`, `contracts/models/__init__.py`
- Modify: `scripts/gen_examples.py`
- Generated: `contracts/examples/route_offset.json`, `contracts/examples/route_def.json`, `contracts/schema/*`, `modules/cop-ui/src/contracts.gen.ts`
- Modify: `modules/cop-ui/src/features/editor/describe.ts` (CONDITION_LABEL에 at_time, tsc가 Record 빠짐으로 깨지지 않게)
- Modify: `contracts/API.md`(1·4절 서술), `contracts/README.md`
- Test: `tests/test_contracts.py`(기존 parametrize) + 새 테스트 하나

**Interfaces:**
- Produces: `RouteOffset(north_m: float, east_m: float)`, `RouteDef(id: str, name: str, points: list[GeoPoint] = [], offsets: list[RouteOffset] = [])`, `Scenario.routes: list[RouteDef] = []`, `ConditionKind.at_time`. TS `RouteOffset`, `RouteDef`, `ConditionKind` 에 `"at_time"`.

- [ ] **Step 1: 실패 테스트**

`tests/test_contracts.py` 끝에:

```python
def test_scenario_routes_default_empty_and_at_time_condition():  # decisions 0044, 0045
    from contracts.models import Condition, RouteDef

    sc = Scenario.model_validate(_load(EXAMPLES / "scenario.json"))
    assert isinstance(sc.routes, list)
    r = RouteDef(id="sq", name="사각형", offsets=[{"north_m": 300, "east_m": 0}])
    assert r.points == [] and r.offsets[0].north_m == 300
    assert Condition(kind="at_time", params={"offset_ms": 60_000}).kind.value == "at_time"
```

Run: `uv run pytest tests/test_contracts.py -n 0 -q -k routes_default`
Expected: FAIL (`ImportError: cannot import name 'RouteDef'`)

- [ ] **Step 2: 모델 추가**

`contracts/models/world.py`의 `WatchPoint` 클래스 다음에:

```python
class RouteOffset(
    BaseModel
):  # decision 0044: meters from the base point (the vehicle as the card starts)
    north_m: float
    east_m: float


class RouteDef(
    BaseModel
):  # decision 0044: a named route the editor offers; points or offsets, not both
    id: str
    name: str
    points: list[GeoPoint] = []  # fixed route: these coordinates
    offsets: list[
        RouteOffset
    ] = []  # relative route: from where the vehicle is when the card starts
```

`contracts/models/frame.py`: world import에 `RouteDef` 추가, `Scenario`의 `watch_points` 줄 다음에:

```python
    routes: list[RouteDef] = []  # decision 0044: routes the editor offers for route-flying cards
```

`contracts/models/enums.py`의 `ConditionKind`에 `signal_received` 다음 줄:

```python
    at_time = "at_time"  # decision 0045: T+ params.offset_ms after operation.started_ms
```

`contracts/models/__init__.py`: world import 목록에 `RouteDef, RouteOffset,`, `_MODELS` 첫 줄 `GeoPoint, Polygon, VehicleSpec, VehicleState, Operation, EnemySpec, WatchPoint,` 뒤에 `RouteOffset, RouteDef,`.

- [ ] **Step 3: 예시·TS 생성, describe 라벨**

`scripts/gen_examples.py` import 목록에 `RouteDef,` `RouteOffset,`(알파벳 순 자리), `examples()` 사전 `"scenario_info": ...` 다음에:

```python
        "route_offset": RouteOffset(north_m=300, east_m=0),
        "route_def": RouteDef(
            id="square_300",
            name="사각형 수색 300m",
            offsets=[
                RouteOffset(north_m=300, east_m=0),
                RouteOffset(north_m=300, east_m=300),
                RouteOffset(north_m=0, east_m=300),
                RouteOffset(north_m=0, east_m=0),
            ],
        ),
```

Run: `uv run python scripts/gen_examples.py` 그리고 `uv run python scripts/gen_contracts.py`
`git status --short`로 새 예시 2개·schema·contracts.gen.ts만 바뀌었는지 본다(다른 예시가 바뀌면 diff를 읽고 무관하면 `git checkout -- <파일>`).

`modules/cop-ui/src/features/editor/describe.ts` `CONDITION_LABEL`의 `signal_received: "신호 수신",` 다음에 `at_time: "T+ 시각",`.

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_contracts.py -n 0 -q`
Expected: PASS
Run: `cd modules/cop-ui && npx tsc -b`
Expected: 오류 없음

- [ ] **Step 5: API.md·README**

`contracts/API.md` 1절 표 아래(개념 설명 끝)에 문단:

```markdown
경로(결정 0044·0045): `Scenario.routes`는 편집기가 "경로 비행" 카드에 내놓는 이름 붙은 경로다. `RouteDef`는 `points`(고정 좌표) 또는 `offsets`(카드에 들어가는 순간의 기체 위치에서 북·동 m) 중 하나를 가진다. 카드에는 고른 경로를 복사한다: `move_to`·`patrol_route`의 params `{route: GeoPoint[], route_name}` 또는 `{offsets: RouteOffset[], route_name}`. `patrol_route`는 반복, `move_to`는 한 번 따라가 마지막 점에서 `arrived`. 점 하나 `move_to {target}`는 그대로. runtime `route_command`가 진입 때 offsets를 실제 좌표 route로 바꾸고, 경로를 가진 `move_to`는 `follow_route`(`params.loop: false`)로 낸다. 조건 `at_time`(`params.offset_ms`)은 작전 시작 후 그 시간이 지나면 성립한다(`time_elapsed`는 적 대본의 "카드 시작 후 `sec`").
```

4절 틱 순서 표 5행의 서명을 `step_vehicle(state, specs[id], plays[state.play_id], targets, t_ms, started_ms=op.started_ms)`로.

`contracts/README.md` 표 `world.py` 줄에 `RouteOffset, RouteDef` 추가.

- [ ] **Step 6: Commit**

```bash
git add contracts scripts/gen_examples.py tests/test_contracts.py modules/cop-ui/src/contracts.gen.ts modules/cop-ui/src/features/editor/describe.ts
git commit -m "Part1-31: contract RouteOffset, RouteDef, Scenario.routes and condition at_time; API.md route params (decisions 0044, 0045)"
```

---

### Task 2: sim — 한 번 가는 경로(`loop: false`)

**Files:**
- Modify: `modules/sim/actions/follow_route.py`
- Test: `modules/sim/tests/test_follow_route.py`

**Interfaces:**
- Consumes: 명령 params `loop`(Task 3이 넣음)
- Produces: `follow_route`가 `params["loop"] is False`면 마지막 점 도착 시 `waypoint_idx = -1`, 그 뒤 위치 그대로.

- [ ] **Step 1: 실패 테스트** (`test_follow_route.py`의 `ISLAND = ...` 줄 위에)

```python
ONCE = ROUTE.model_copy(
    update={
        "command": ROUTE.command.model_copy(
            update={"params": {**ROUTE.command.params, "loop": False}}
        )
    }
)


def test_one_way_route_stops_at_the_end_and_arrives():  # decision 0045
    st = follow_route(_state(_at(east_m=495, north_m=500), 1), SPEC, ONCE, 1000)
    assert dist_m(st.pos, B) < 1
    assert st.waypoint_idx == -1  # runtime reads this as "arrived"


def test_one_way_route_stays_after_arriving():
    at_b = _state(B, -1)
    assert follow_route(at_b, SPEC, ONCE, 1000).pos == B


def test_one_way_route_still_passes_its_middle_points():
    st = follow_route(_state(_at(north_m=495), 0), SPEC, ONCE, 1000)
    assert st.waypoint_idx == 1
```

Run: `uv run pytest modules/sim/tests/test_follow_route.py -n 0 -q`
Expected: FAIL 2개(`waypoint_idx == 2` 대신 -1, 멈추지 않고 A로 감)

- [ ] **Step 2: 구현**

`follow_route.py` docstring 첫 줄을 `"""SIM-06 follow_route: 경로점을 차례로 돌고 끝나면 처음으로, loop false면 끝점에서 멈춤(결정 0045)`로. 본문:

```python
    route = [GeoPoint(**q) for q in pc.command.params["route"]]
    once = pc.command.params.get("loop") is False  # decision 0045: a move along a route
    if once and st.waypoint_idx < 0:
        return st  # arrived at the end; runtime moves the card on
    i = max(st.waypoint_idx, 0) % len(route)
    wp = to_sea(route[i], land)
    pos = move_toward(st.pos, sea_aim(st.pos, wp, land), spec.speed_mps * dt_ms / 1000)
    upd: dict = {"pos": pos}
    if dist_m(pos, wp) < 1:
        upd["waypoint_idx"] = -1 if once and i == len(route) - 1 else i + 1
    return st.model_copy(update=upd)
```

- [ ] **Step 3: 통과 + sim 전체**

Run: `uv run pytest modules/sim/tests/test_follow_route.py -n 0 -q` → PASS
Run: `uv run pytest modules/sim -p no:cacheprovider` → 전부 PASS

- [ ] **Step 4: Commit**

```bash
git add modules/sim/actions/follow_route.py modules/sim/tests/test_follow_route.py
git commit -m "Part1-31: sim follow_route with loop false stops at the last point and reports arrival (decision 0045)"
```

---

### Task 3: runtime — `route_command` (상대 경로 계산, 한 번 가는 이동)

**Files:**
- Create (new_action.py): `modules/runtime/actions/route_command.py`, `modules/runtime/tests/test_route_command.py`, `modules/runtime/SPEC.md` 행
- Modify: `modules/runtime/actions/enter_step.py`(import 한 줄, 호출 한 줄)
- Test: `modules/runtime/tests/test_enter_step.py`

**Interfaces:**
- Consumes: `expand_action`(modules.play), `offset_latlon`(shared.geo)
- Produces: `route_command(action: Action, domain: Domain, pos: GeoPoint, params: dict) -> tuple[CommandKind | None, dict]`

- [ ] **Step 1: 액션 만들기**

Run: `uv run python scripts/new_action.py runtime route_command "경로 비행 카드의 명령 종류와 params: offsets는 진입 때 기체 위치 기준 실제 좌표 route로, 경로를 가진 move_to는 한 번 따라가는 follow_route(loop false) (결정 0044·0045)" --inputs "Action, Domain, 기체 위치, params" --outputs "(CommandKind|None, params)" --done "상대 경로가 기체 위치 기준 좌표, move_to+route는 follow_route loop false, 그 밖은 expand_action 그대로"`
Expected: 액션 파일·실패 테스트·SPEC 행 생성. 출력의 RT 번호를 기록.

- [ ] **Step 2: 실패 테스트** — 생성된 `modules/runtime/tests/test_route_command.py` 전체를 다음으로:

```python
from contracts.models import Action, CommandKind, GeoPoint
from modules.runtime.actions.route_command import route_command
from shared.geo import dist_m, offset_latlon

HERE = GeoPoint(lat=37.97, lon=124.70)
FIXED = [{"lat": 37.98, "lon": 124.66, "alt_m": 0}, {"lat": 37.98, "lon": 124.74, "alt_m": 0}]
SQUARE = [{"north_m": 300, "east_m": 0}, {"north_m": 300, "east_m": 300}]


def test_offsets_are_measured_from_where_the_vehicle_is():
    kind, p = route_command(
        Action(kind="patrol_route"), "air", HERE, {"offsets": SQUARE, "route_name": "sq"}
    )
    assert kind == CommandKind.follow_route
    assert "offsets" not in p and p["route_name"] == "sq"
    lat, lon = offset_latlon(HERE.lat, HERE.lon, 300, 300)
    assert dist_m(GeoPoint(**p["route"][1]), GeoPoint(lat=lat, lon=lon)) < 0.5
    assert dist_m(GeoPoint(**p["route"][0]), HERE) > 299


def test_patrol_keeps_looping():
    kind, p = route_command(Action(kind="patrol_route"), "air", HERE, {"route": FIXED})
    assert kind == CommandKind.follow_route and "loop" not in p


def test_a_move_with_a_route_follows_it_once():
    kind, p = route_command(
        Action(kind="move_to"), "air", HERE, {"route": FIXED, "route_name": "n"}
    )
    assert kind == CommandKind.follow_route and p["loop"] is False and p["route"] == FIXED


def test_a_relative_move_follows_once_from_here():
    kind, p = route_command(
        Action(kind="move_to"), "air", HERE, {"offsets": [{"north_m": 1000, "east_m": 0}]}
    )
    assert kind == CommandKind.follow_route and p["loop"] is False
    assert dist_m(GeoPoint(**p["route"][0]), HERE) > 999


def test_a_point_move_and_other_actions_are_unchanged():
    target = {"lat": 37.99, "lon": 124.70, "alt_m": 0}
    assert route_command(Action(kind="move_to"), "air", HERE, {"target": target}) == (
        CommandKind.move,
        {"target": target},
    )
    assert route_command(Action(kind="hold"), "air", HERE, {}) == (CommandKind.hold, {})
```

Run: `uv run pytest modules/runtime/tests/test_route_command.py -n 0 -q`
Expected: FAIL (생성된 스켈레톤이 NotImplemented 또는 서명 다름)

- [ ] **Step 3: 구현** — `modules/runtime/actions/route_command.py` 전체(첫 줄 RT 번호는 Step 1 출력대로):

```python
"""RT-NN route_command: 경로 비행 카드의 명령 종류와 params (결정 0044·0045)
상대 경로(offsets)는 지금 기체 위치를 기준점으로 실제 좌표 route로 바꾼다. 경로를 가진 move_to는
한 번만 따라가는 follow_route(loop false)로 내고, 끝점에서 sim이 도착을 낸다. 그 밖은 expand_action 그대로.
SPEC: modules/runtime/SPEC.md#RT-NN
"""

from contracts.models import Action, CommandKind, Domain, GeoPoint
from modules.play import expand_action
from shared.geo import offset_latlon


def route_command(
    action: Action, domain: Domain, pos: GeoPoint, params: dict
) -> tuple[CommandKind | None, dict]:
    kind = expand_action(action, domain)
    if "offsets" in params:
        pts = [
            offset_latlon(pos.lat, pos.lon, o["east_m"], o["north_m"]) for o in params["offsets"]
        ]
        route = [GeoPoint(lat=lat, lon=lon).model_dump() for lat, lon in pts]
        params = {k: v for k, v in params.items() if k != "offsets"} | {"route": route}
    if kind is not None and action.kind.value == "move_to" and "route" in params:
        return CommandKind.follow_route, params | {"loop": False}
    return kind, params
```

Run: `uv run pytest modules/runtime/tests/test_route_command.py -n 0 -q` → PASS (5)

- [ ] **Step 4: enter_step 연결 — 실패 테스트** (`test_enter_step.py` 끝에)

```python
def test_a_relative_route_card_flies_its_shape_from_where_the_vehicle_is():  # decision 0044
    from contracts.models import CommandKind

    step = Step(id="s1", name="수색", do=Action(kind="patrol_route", params={
        "offsets": [{"north_m": 300, "east_m": 0}], "route_name": "sq"}))  # fmt: skip
    play = Play(id="p", name="p", domains=["air"], entry="s1", approved=True, steps=[step])
    here = GeoPoint(lat=37.5, lon=126.5)
    _, cmd, _ = enter_step(vs().model_copy(update={"pos": here}), spec(), play, step, [], 0)
    assert cmd.kind == CommandKind.follow_route
    assert abs(cmd.params["route"][0]["lat"] - (here.lat + 300 / 111_195)) < 1e-4
```

(`vs(**kw)`는 `pos=HOME`을 고정으로 넣어 `pos=`를 넘기면 겹치므로 `model_copy`로 바꾼다.)

Run: `uv run pytest modules/runtime/tests/test_enter_step.py -n 0 -q -k relative_route` → FAIL(`KeyError: 'route'` 없음/offsets 그대로)

- [ ] **Step 5: enter_step 수정**

`modules/runtime/actions/enter_step.py`: `from modules.play import expand_action` 줄을 `from modules.runtime.actions.route_command import route_command`로, `kind = expand_action(step.do, spec.domain)` 줄을 `kind, params = route_command(step.do, spec.domain, st.pos, params)`로. (파일 줄 수 그대로 79)

Run: `uv run pytest modules/runtime -p no:cacheprovider` → 전부 PASS
Run: `wc -l modules/runtime/actions/enter_step.py modules/runtime/actions/route_command.py` → 둘 다 80 이하

- [ ] **Step 6: Commit**

```bash
git add modules/runtime/actions/route_command.py modules/runtime/tests/test_route_command.py modules/runtime/SPEC.md modules/runtime/actions/enter_step.py modules/runtime/tests/test_enter_step.py
git commit -m "Part1-31: runtime route_command: offsets become coordinates from where the vehicle is as the card starts, a move with a route follows it once (decisions 0044, 0045)"
```

---

### Task 4: runtime `at_time` 조건 + engine이 작전 시작 시각을 넘김

**Files:**
- Modify: `modules/runtime/actions/step_vehicle.py`, `modules/gateway/engine.py`
- Test: `modules/runtime/tests/test_step_vehicle.py`, Create `modules/gateway/tests/test_engine_at_time.py`

**Interfaces:**
- Produces: `step_vehicle(st, spec, play, targets, t_ms, started_ms: int | None = None)`

- [ ] **Step 1: 실패 테스트** (`test_step_vehicle.py` 끝에)

```python
TIMED = Play(id="p", name="p", domains=["air"], entry="patrol", approved=True, steps=[
    Step(id="patrol", name="순찰", do=Action(kind="hold"), on=[ex("at_time", "home", offset_ms=60_000)]),
    Step(id="home", name="귀환", do=Action(kind="return_home")),
])  # fmt: skip
START = 1_000_000


def test_at_time_fires_at_its_T_plus_offset():  # decision 0045
    before, _, _ = step_vehicle(vs(), SPEC, TIMED, [], START + 59_999, START)
    after, _, _ = step_vehicle(vs(), SPEC, TIMED, [], START + 60_000, START)
    assert before.step_id == "patrol" and after.step_id == "home"


def test_at_time_without_the_operation_start_never_fires():
    st, _, _ = step_vehicle(vs(), SPEC, TIMED, [], START + 10**9)
    assert st.step_id == "patrol"
```

Run: `uv run pytest modules/runtime/tests/test_step_vehicle.py -n 0 -q -k at_time` → FAIL(`TypeError` 인자 6개)

- [ ] **Step 2: 구현** — `step_vehicle.py`:
- `_true` 서명을 `def _true(cond: Condition, st: VehicleState, targets: list[Target], tracking: bool, t_ms: int, started_ms: int | None) -> bool:`로(줄이 길면 black이 나눔), `battery_below` 분기 다음에:

```python
    if cond.kind == ConditionKind.at_time:  # decision 0045: T+ from the operation start
        return started_ms is not None and t_ms - started_ms >= int(cond.params.get("offset_ms", 0))
```

- 마지막 주석을 `# time_elapsed·operator_choice·signal_received: 시연 플레이에서 안 씀`으로 그대로 둔다.
- `step_vehicle` 서명에 `started_ms: int | None = None` 추가, 루프의 `_true(ex.cond, st, targets, tracking)`를 `_true(ex.cond, st, targets, tracking, t_ms, started_ms)`로.

Run: `uv run pytest modules/runtime -p no:cacheprovider` → 전부 PASS, `wc -l modules/runtime/actions/step_vehicle.py` → 80 이하

- [ ] **Step 3: engine 실패 테스트** — `modules/gateway/tests/test_engine_at_time.py`:

```python
from contracts.models import Condition, Exit, TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json

SC = load_scenario_json("demo/scenarios/baengnyeong_night.json")


def test_the_engine_gives_step_vehicle_the_operation_start():  # decision 0045
    pid = SC.operation.assign["d1"]
    play = next(p for p in SC.plays if p.id == pid)
    entry = next(s for s in play.steps if s.id == play.entry)
    other = next(s.id for s in play.steps if s.id != play.entry)
    timed = entry.model_copy(
        update={
            "on": [
                Exit(cond=Condition(kind="at_time", params={"offset_ms": 1000}), go_step=other),
                *entry.on,
            ]
        }
    )
    play = play.model_copy(update={"steps": [timed if s.id == entry.id else s for s in play.steps]})
    sc = SC.model_copy(update={"plays": [play if p.id == pid else p for p in SC.plays]})
    es = init_engine(sc)
    steps = []
    for _ in range(10):  # 10 ticks of 200 ms = 2 s
        es, _ = tick(es, TickInputs())
        steps.append(next(v.step_id for v in es.states if v.id == "d1"))
    assert steps[2] == play.entry  # 600 ms
    assert steps[-1] == other
```

Run: `uv run pytest modules/gateway/tests/test_engine_at_time.py -n 0 -q` → FAIL(마지막이 entry 그대로)

- [ ] **Step 4: engine 수정** — `modules/gateway/engine.py`의
`s, cmd, rep = step_vehicle(s, specs[s.id], plays.get(s.play_id), targets, t)`를
`s, cmd, rep = step_vehicle(s, specs[s.id], plays.get(s.play_id), targets, t, sc.operation.started_ms)`로.

Run: `uv run pytest modules/gateway -p no:cacheprovider` → 전부 PASS

- [ ] **Step 5: Commit**

```bash
git add modules/runtime/actions/step_vehicle.py modules/runtime/tests/test_step_vehicle.py modules/gateway/engine.py modules/gateway/tests/test_engine_at_time.py
git commit -m "Part1-31: at_time condition fires at T+ offset_ms from the operation start; engine passes started_ms to step_vehicle (decision 0045)"
```

---

### Task 5: 시나리오 경로 목록 + `GET /routes` (그 뒤 서버 쪽 ship)

**Files:**
- Modify: `demo/scenarios/baengnyeong_night.json`, `demo/scenarios/baengnyeong_24h.json`
- Generated: `contracts/examples/scenario.json`(gen_examples)
- Create: `tests/test_demo_routes.py`
- Modify: `modules/gateway/app.py`, `modules/gateway/tests/test_app.py`, `modules/cop-ui/vite.config.ts`, `contracts/API.md` 5절

**Interfaces:**
- Produces: 두 시나리오의 `routes`, 기존 순찰 카드의 `route_name`, `GET /routes -> RouteDef[]`

- [ ] **Step 1: 실패 테스트** — `tests/test_demo_routes.py`:

```python
import json
from pathlib import Path

import pytest

from contracts.models import Scenario
from modules.safety import point_in_polygon

ROOT = Path(__file__).resolve().parent.parent
FILES = ["baengnyeong_night.json", "baengnyeong_24h.json"]
RELATIVE = {"square_300", "zigzag_600", "orbit_200", "north_1km"}


@pytest.mark.parametrize("name", FILES)
def test_demo_routes(name):  # decision 0044
    sc = Scenario.model_validate(json.loads((ROOT / "demo/scenarios" / name).read_text("utf-8")))
    ids = [r.id for r in sc.routes]
    assert len(ids) == len(set(ids)) and len({r.name for r in sc.routes}) == len(ids)
    assert RELATIVE <= set(ids) and "base_to_north" in ids
    for r in sc.routes:
        assert bool(r.points) != bool(r.offsets), r.id  # one kind each
        assert all(point_in_polygon(p, sc.operation.zone) for p in r.points), r.id
    names = {r.name for r in sc.routes}
    for p in sc.plays:  # every patrol card on the demo names a route from the list
        for s in p.steps:
            if s.do.kind.value == "patrol_route" and not p.id.startswith("enemy"):
                assert s.do.params.get("route_name") in names, (p.id, s.id)
```

Run: `uv run pytest tests/test_demo_routes.py -n 0 -q` → FAIL(`routes` 빈 목록)

- [ ] **Step 2: 데이터 넣기** — 일회용 스크립트(저장소에 남기지 않음, scratchpad에 둔다)로 두 JSON에 `routes`를 넣고 순찰 카드에 `route_name`을 붙인다. 들여쓰기·키 순서는 `json.dump(..., ensure_ascii=False, indent=2)`로 원래 파일 형식과 같은지 `git diff --stat`으로 확인(전체 재정렬이 생기면 원래 indent 값에 맞춘다).

고정 경로(각 시나리오에 있는 플레이에서 그대로 복사):
- 야간: `patrol_a`(이름 "순찰 A", patrol_a의 patrol route), `patrol_b`(이름 "북동 순찰", patrol_b의 patrol route), `coast_a`("해안 A(북)"), `coast_b`("해안 B(남)")
- 24h: `coast_a`, `coast_b`
- 두 시나리오: `base_to_north`("기지 → 북쪽 해역", points `[{lat 37.97, lon 124.70}, {lat 37.99, lon 124.70}]`)

상대 경로(두 시나리오 같음, north_m·east_m):
- `square_300` "사각형 수색 300m": (300,0) (300,300) (0,300) (0,0)
- `zigzag_600` "지그재그 수색 600m": (200,-300) (200,300) (400,300) (400,-300) (600,-300) (600,300)
- `orbit_200` "원 선회 200m": (200,0) (141,141) (0,200) (-141,141) (-200,0) (-141,-141) (0,-200) (141,-141)
- `north_1km` "북쪽으로 1km": (1000,0)

`route_name`: 각 플레이의 patrol_route 카드에 그 route와 같은 고정 경로 이름(patrol_b의 patrol2도 "북동 순찰").

Run: `uv run python scripts/gen_examples.py` (scenario.json 예시가 야간 JSON과 같아야 함, 결정 0035)
Run: `uv run pytest tests/test_demo_routes.py tests/test_contracts.py -n 0 -q` → PASS

- [ ] **Step 3: `GET /routes` 실패 테스트** (`modules/gateway/tests/test_app.py`의 `test_scenario_paths_replace_the_demo_list` 다음에)

```python
def test_routes_come_from_the_running_operation():  # decision 0044
    client, _ = fake_app()
    night = {r["id"] for r in client.get("/routes").json()}
    assert {"patrol_a", "square_300"} <= night
    client.post("/scenarios/baengnyeong_24h/activate")
    day = {r["id"] for r in client.get("/routes").json()}
    assert "patrol_a" not in day and "square_300" in day
```

Run: `uv run pytest modules/gateway/tests/test_app.py -n 0 -q -k routes_come` → FAIL(404 → JSON detail)

- [ ] **Step 4: 엔드포인트·proxy·API.md**

`modules/gateway/app.py`의 `@app.get("/enemies")` 핸들러 다음에:

```python
    @app.get("/routes")
    async def routes():  # decision 0044: routes the editor offers for route-flying cards
        return live.scenario.routes
```

`modules/cop-ui/vite.config.ts` 정규식 `|scenarios)`를 `|scenarios|routes)`로.
`contracts/API.md` 5절 표 `GET /enemies` 줄 다음에 `` | `GET /routes` | — | `RouteDef[]`(실행 작전의 경로 목록, 결정 0044) | ``.

Run: `uv run pytest modules/gateway -p no:cacheprovider` → PASS
Run: `cd modules/cop-ui && npx vitest run src/viteProxy.test.ts` → PASS

- [ ] **Step 5: Commit 후 ship(서버 쪽 완성)**

```bash
git add demo/scenarios/baengnyeong_night.json demo/scenarios/baengnyeong_24h.json contracts/examples tests/test_demo_routes.py modules/gateway/app.py modules/gateway/tests/test_app.py modules/cop-ui/vite.config.ts contracts/API.md
git commit -m "Part1-31: demo route lists (fixed patrol and coast routes, base to north, four relative shapes), route_name on patrol cards, GET /routes (decision 0044)"
```

Run: `scripts/ship.sh` (rebase 충돌은 규칙대로, 실패 테스트는 고치고 다시)

---

### Task 6: 편집기 로직 — 경로 적용·반복·T+·카드 문구·경로 불러오기

**Files:**
- Modify: `modules/cop-ui/src/features/editor/editStep.ts`, `describe.ts`, `loadEditorData.ts`
- Test: `editStep.test.ts`, `describe.test.ts`, `loadEditorData.test.ts`
- Modify: `modules/cop-ui/SPEC.md` (UI 행)

**Interfaces:**
- Consumes: TS `RouteDef`, `Play`, `Step`, `Condition`
- Produces:
  - `ROUTE_KINDS: ActionKind[] = ["move_to", "patrol_route"]`
  - `applyRoute(play: Play, stepId: string, route: RouteDef): Play` — 행동 종류 유지, params를 `{route: points, route_name}` 또는 `{offsets, route_name}`로 교체
  - `setLoop(play: Play, stepId: string, loop: boolean): Play` — 종류만 `patrol_route`/`move_to`, 점 하나 이동에서 반복이면 `route: [target]`
  - `routeChoice(params: Record<string, unknown>, routes: RouteDef[]): string` — 목록의 경로 id 또는 `""`(목록에 없음)
  - `defaultCondition("at_time")` → `{offset_ms: 60000}`, `EDIT_CONDITIONS`에 `"at_time"`
  - `describeAction`: 경로 비행 문구, `describeCondition`: at_time은 `T+m:ss`
  - `EditorData.routes: RouteDef[]`(GET /routes)

- [ ] **Step 1: 실패 테스트**

`editStep.test.ts` 끝에(파일 위 import에 `applyRoute, routeChoice, setLoop` 추가, `RouteDef` 타입 import):

```ts
const SQUARE: RouteDef = { id: "square_300", name: "사각형 수색 300m", points: [], offsets: [{ north_m: 300, east_m: 0 }] };
const NORTH: RouteDef = { id: "base_to_north", name: "기지 → 북쪽 해역", points: [{ lat: 37.97, lon: 124.7, alt_m: 0 }], offsets: [] };
const routePlay: Play = { id: "r", name: "r", domains: ["air"], entry: "a", approved: true, steps: [
  { id: "a", name: "a", do: { kind: "move_to", params: { target: { lat: 37.9, lon: 124.7, alt_m: 0 } } }, on: [] },
] };

describe("route flying", () => {
  it("copies a relative route into the card and keeps the kind", () => {
    const s = step(applyRoute(routePlay, "a", SQUARE), "a");
    expect(s.do).toEqual({ kind: "move_to", params: { offsets: SQUARE.offsets, route_name: "사각형 수색 300m" } });
  });
  it("copies a fixed route's points as the route", () => {
    expect(step(applyRoute(routePlay, "a", NORTH), "a").do.params).toEqual({ route: NORTH.points, route_name: "기지 → 북쪽 해역" });
  });
  it("turns looping on and off without touching the route", () => {
    const named = applyRoute(routePlay, "a", NORTH);
    const loop = step(setLoop(named, "a", true), "a").do;
    expect(loop).toEqual({ kind: "patrol_route", params: { route: NORTH.points, route_name: "기지 → 북쪽 해역" } });
    expect(step(setLoop(setLoop(named, "a", true), "a", false), "a").do.kind).toBe("move_to");
  });
  it("makes a one-point route when a point move starts looping", () => {
    expect(step(setLoop(routePlay, "a", true), "a").do.params).toEqual({ route: [{ lat: 37.9, lon: 124.7, alt_m: 0 }] });
  });
  it("drops route values when the card leaves route flying", () => {
    const p = applyRoute(routePlay, "a", SQUARE);
    expect(step(setActionKind(p, "a", "hold"), "a").do.params).toEqual({});
  });
  it("finds the listed route by name and keeps an unnamed route as the current value", () => {
    expect(routeChoice({ offsets: SQUARE.offsets, route_name: "사각형 수색 300m" }, [NORTH, SQUARE])).toBe("square_300");
    expect(routeChoice({ route: [NORTH.points[0], NORTH.points[0]] }, [NORTH, SQUARE])).toBe("");
  });
  it("defaults a T+ condition to one minute", () => {
    expect(defaultCondition("at_time", routePlay.steps[0])).toEqual({ kind: "at_time", params: { offset_ms: 60000 } });
  });
});
```

`describe.test.ts`: 기존 두 기대를 바꾸고 새 기대 추가:

```ts
    expect(describeAction({ kind: "patrol_route", params: { route } })).toBe("경로 비행 · 경로 2곳 · 반복");
```
```ts
      .toBe("경로 비행 · 37.975, 124.700 · 한 번");
```
```ts
  it("names the route, whether it repeats and whether it is relative", () => {
    expect(describeAction({ kind: "patrol_route", params: { route: [], route_name: "해안 A(북)" } })).toBe("경로 비행 · 해안 A(북) · 반복");
    expect(describeAction({ kind: "move_to", params: { offsets: [{ north_m: 1, east_m: 0 }], route_name: "북쪽으로 1km" } }))
      .toBe("경로 비행 · 북쪽으로 1km · 한 번 · 기체 위치 기준");
    expect(describeCondition({ kind: "at_time", params: { offset_ms: 90_000 } })).toBe("T+1:30");
  });
```

(두 기존 기대가 있는 `it` 블록의 위치·`route` 변수는 파일 그대로 쓴다. `describeCondition`이 import에 없으면 추가.)

`loadEditorData.test.ts` 첫 테스트의 `body`에 `"/routes": [{ id: "square_300", name: "사각형", points: [], offsets: [] }]`를 넣고 `expect(d.routes.map((r) => r.id)).toEqual(["square_300"]);` 추가.

Run: `cd modules/cop-ui && npx vitest run src/features/editor/editStep.test.ts src/features/editor/describe.test.ts src/features/editor/loadEditorData.test.ts`
Expected: FAIL(applyRoute 등 없음, 문구 다름, routes 없음)

- [ ] **Step 2: 구현**

`editStep.ts` — import에 `RouteDef` 추가, `EDIT_CONDITIONS`에 `"at_time"`을 `operator_choice` 다음에, 상수·함수 추가:

```ts
// Decision 0045: the editor shows move_to and patrol_route as one action, "경로 비행", with "반복" (looping).
export const ROUTE_KINDS: ActionKind[] = ["move_to", "patrol_route"];

const isPoint = (v: unknown): v is GeoPoint => !!v && typeof v === "object" && "lat" in v && "lon" in v;

// A route from the list copied into the card: fixed points as `route`, a relative shape as `offsets`
// (runtime measures them from where the vehicle is when the card starts, decision 0044).
export function applyRoute(play: Play, stepId: string, route: RouteDef): Play {
  return updateStep(play, stepId, (s) => {
    const params = route.offsets?.length ? { offsets: route.offsets, route_name: route.name } : { route: route.points ?? [], route_name: route.name };
    return { ...s, do: { kind: s.do.kind, params } };
  });
}

// "반복": patrol_route loops, move_to follows the route once. The route stays; a point move gets a one-point route.
export function setLoop(play: Play, stepId: string, loop: boolean): Play {
  return updateStep(play, stepId, (s) => {
    const kind: ActionKind = loop ? "patrol_route" : "move_to";
    if (s.do.kind === kind) return s;
    const { target, ...rest } = s.do.params ?? {};
    const params = loop && !rest.route && !rest.offsets && isPoint(target) ? { ...rest, route: [target] } : { ...s.do.params };
    return { ...s, do: { kind, params } };
  });
}

// Which listed route the card holds (by its name), or "" when it holds another one (unnamed, a point move).
export function routeChoice(params: Record<string, unknown>, routes: RouteDef[]): string {
  return routes.find((r) => r.name === params.route_name)?.id ?? "";
}
```

`defaultCondition`에 `if (kind === "at_time") return { kind, params: { offset_ms: 60000 } };` 추가.

`describe.ts` — `import { mmss } from "../run/mmss";` 추가, `ACTION_LABEL`의 `move_to`·`patrol_route`를 둘 다 `"경로 비행"`으로, `describeAction`을:

```ts
// Route flying (decision 0045): the route's name (or how many points), once or repeating, and whether it is relative.
function routeText(a: Action): string {
  const p = a.params ?? {};
  const name = typeof p.route_name === "string" ? p.route_name
    : Array.isArray(p.route) ? `경로 ${p.route.length}곳`
    : Array.isArray(p.offsets) ? `상대 경로 ${p.offsets.length}곳` : targetText(p.target);
  const parts = [ACTION_LABEL[a.kind], name, a.kind === "patrol_route" ? "반복" : "한 번"];
  if (Array.isArray(p.offsets)) parts.push("기체 위치 기준");
  return parts.filter(Boolean).join(" · ");
}

export function describeAction(a: Action): string {
  if (a.kind === "move_to" || a.kind === "patrol_route") return routeText(a);
  const p = a.params ?? {};
  const parts = [ACTION_LABEL[a.kind]];
  if (p.target !== undefined) parts.push(targetText(p.target));
  if (typeof p.distance_m === "number") parts.push(`${p.distance_m}m 거리`);
  return parts.filter(Boolean).join(" · ");
}
```

`describeCondition`의 battery 줄 다음에 `if (c.kind === "at_time") return \`T+${mmss(Number(p.offset_ms ?? 0))}\`;`.

`loadEditorData.ts` — `RouteDef` import, `EditorData`에 `routes: RouteDef[]`, Promise.all에 `getJson<RouteDef[]>(f, "/routes")`를 다섯째로, 반환에 `routes`, 모양 검사에 `!Array.isArray(routes)` 추가, 주석의 엔드포인트 목록에 `/routes`.

Run: 같은 vitest 명령 → PASS. `npx tsc -b` → 오류 없음(StepNode 등 ACTION_LABEL 사용처 확인).

- [ ] **Step 3: SPEC 행** (`modules/cop-ui/SPEC.md` 끝)

```markdown
| UI-52 | applyRoute·setLoop·routeChoice·ROUTE_KINDS | Play, 카드 id, RouteDef/반복 | 새 Play / 경로 id | 경로 비행(결정 0044·0045): 고른 경로를 카드에 복사(고정=route, 상대=offsets, route_name), 반복=patrol_route·한 번=move_to(점 하나 이동은 반복 시 한 점 route), 행동을 바꾸면 경로 값 지움, 목록에 없는 경로는 "" | 리드 | 완료 |
| UI-53 | describeAction·describeCondition(경로·T+) | Action/Condition | 카드 문구 | "경로 비행 · 이름|경로 N곳 · 한 번|반복 · 기체 위치 기준", at_time은 T+m:ss | 리드 | 완료 |
```

- [ ] **Step 4: Commit**

```bash
git add modules/cop-ui/src/features/editor/editStep.ts modules/cop-ui/src/features/editor/editStep.test.ts modules/cop-ui/src/features/editor/describe.ts modules/cop-ui/src/features/editor/describe.test.ts modules/cop-ui/src/features/editor/loadEditorData.ts modules/cop-ui/src/features/editor/loadEditorData.test.ts modules/cop-ui/SPEC.md
git commit -m "Part1-31: editor logic for route flying: applyRoute, setLoop, routeChoice, T+ condition, card text, routes in the editor data (decisions 0044, 0045)"
```

---

### Task 7: 편집 패널 화면 — 경로 비행·반복·경로 선택칸·T+ 입력

**Files:**
- Modify: `modules/cop-ui/src/features/editor/StepEditor.tsx`, `PlayWorkflow.tsx`, `EditorScreen.tsx`, `modules/cop-ui/src/index.css`
- Modify: `scripts/qa/card_edit.json` (C3 기대값)

**Interfaces:**
- Consumes: Task 6의 함수들, `EditorData.routes`
- Produces: `StepEditor` prop `routes: RouteDef[]`, `PlayWorkflow` prop `routes?: RouteDef[]`

- [ ] **Step 1: StepEditor** — import에 `RouteDef`, `applyRoute, routeChoice, ROUTE_KINDS, setLoop` 추가. Props에 `routes?: RouteDef[]; // decision 0044: what the route select offers`, 인자 `routes = []`.

행동 선택칸을 다음으로 바꾼다(경로 비행 = `"route"` 값):

```tsx
        <select aria-label="행동" value={isRoute ? "route" : step.do.kind}
          onChange={(e) => onChange(setActionKind(play, step.id, (e.target.value === "route" ? "patrol_route" : e.target.value) as ActionKind, fallbackPoint))}>
          <option value="route">경로 비행</option>
          {(isRoute ? nonRoute : withCurrent(nonRoute, step.do.kind)).map((k) => <option key={k} value={k}>{ACTION_LABEL[k] ?? k}</option>)}
        </select>
```

(`targeted` 정의 옆에 `const isRoute = ROUTE_KINDS.includes(step.do.kind);`와 `const nonRoute = EDIT_ACTIONS.filter((k) => !ROUTE_KINDS.includes(k));`. 다른 행동에서 "경로 비행"을 고르면 반복 켠 순찰(`patrol_route`)로 시작한다.)

기존 `{(step.do.kind === "move_to" || step.do.kind === "patrol_route") && (<div className="se-note">…좌표는 그대로 둡니다…</div>)}` 블록을 다음으로 바꾼다:

```tsx
        {isRoute && (
          <div className="se-route">
            <label className="se-check">
              <input type="checkbox" aria-label="반복" checked={step.do.kind === "patrol_route"}
                onChange={(e) => onChange(setLoop(play, step.id, e.target.checked))} /> 반복
            </label>
            <select aria-label="경로" value={routeChoice(params, routes)}
              onChange={(e) => { const r = routes.find((x) => x.id === e.target.value); if (r) onChange(applyRoute(play, step.id, r)); }}>
              {routeChoice(params, routes) === "" && <option value="">지금 값 유지: {describeAction(step.do)}</option>}
              <optgroup label="고정 경로">
                {routes.filter((r) => !r.offsets?.length).map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
              </optgroup>
              <optgroup label="상대 경로 (기체 위치 기준)">
                {routes.filter((r) => r.offsets?.length).map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
              </optgroup>
            </select>
          </div>
        )}
```

연결 조건 분기들 옆(`battery_below` 블록 다음)에:

```tsx
              {ex.cond.kind === "at_time" && (() => {
                const ms = Number(ex.cond.params?.offset_ms ?? 0);
                const setMs = (m: number, s: number) => put({ ...ex, cond: { ...ex.cond, params: { offset_ms: (m * 60 + s) * 1000 } } });
                return (
                  <span className="se-num">T+
                    <input aria-label={`연결 ${i + 1} 분`} type="number" min={0} value={Math.floor(ms / 60000)}
                      onChange={(e) => num(e.target.value) !== null && setMs(num(e.target.value)!, Math.floor(ms / 1000) % 60)} />분
                    <input aria-label={`연결 ${i + 1} 초`} type="number" min={0} max={59} value={Math.floor(ms / 1000) % 60}
                      onChange={(e) => num(e.target.value) !== null && setMs(Math.floor(ms / 60000), num(e.target.value)!)} />초
                  </span>
                );
              })()}
```

- [ ] **Step 2: 데이터 연결** — `PlayWorkflow.tsx` Props에 `routes?: RouteDef[]`, 인자 기본 `routes = []`, `<StepEditor … routes={routes} …>`. `EditorScreen.tsx`의 `<PlayWorkflow … plays={…} />`에 `routes={data.routes}`.

- [ ] **Step 3: CSS** (`index.css` 끝, 배치만)

```css
.se-route { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 6px; }
.se-check { display: flex; gap: 4px; align-items: center; }
```

- [ ] **Step 4: 기존 화면 점검 기대값** — `scripts/qa/card_edit.json`:
- `{"select": ["select[aria-label='행동']", "patrol_route"], …}`의 값을 `"route"`로.
- C3 기대 `{"name": "해안 순찰", "action": "순찰 경로", "text": "순찰 경로 1점", "edited": true}`를 `{"name": "해안 순찰", "action": "경로 비행", "text": "경로 비행 · 경로 1곳 · 반복", "edited": true}`로.

Run: `node scripts/qa/run.mjs --check scripts/qa/card_edit.json` → OK

- [ ] **Step 5: 타입·테스트·빌드**

Run: `cd modules/cop-ui && npx tsc -b` → 오류 없음
Run: `cd modules/cop-ui && npx vitest run` → 전부 PASS
Run: `cd modules/cop-ui && npm run build` → 성공

- [ ] **Step 6: Commit**

```bash
git add modules/cop-ui/src scripts/qa/card_edit.json
git commit -m "Part1-31: card panel shows route flying with 반복 and a route select (fixed and relative groups) only on route cards, T+ minutes and seconds on at_time links (decisions 0044, 0045)"
```

---

### Task 8: 실제 화면 확인 · 기록 · 검토 · 반영

**Files:**
- Create: `scripts/qa/route_select.json`
- Modify: `demo/BUILT_HERE.md`

- [ ] **Step 1: 점검 목록** — `scripts/qa/route_select.json`(24시간 작전, "대기" 플레이 = d3·d4):

```json
[
 {"viewport": [1366, 768]},
 {"nav": "/?qa=routes#editor", "wait": 5000},
 {"click": "백령도 해안 순찰 24시간 교대(가상)", "wait": 2500},
 {"click": "대기", "wait": 1500},
 {"clickSel": ".react-flow__node", "wait": 500},
 {"label": "R0 a hold card has no route select or 반복", "eval": "({ route: !!document.querySelector(\"select[aria-label='경로']\"), loop: !!document.querySelector(\"input[aria-label='반복']\") })", "expect": {"route": false, "loop": false}},
 {"click": "+ 뒤에 카드 추가", "wait": 1200},
 {"select": ["select[aria-label='행동']", "route"], "wait": 400},
 {"label": "R1 route flying shows 반복 and the route list (fixed and relative groups)", "eval": "({ loop: document.querySelector(\"input[aria-label='반복']\")?.checked, groups: [...document.querySelectorAll(\"select[aria-label='경로'] optgroup\")].map(g => g.label), relative: [...document.querySelectorAll(\"select[aria-label='경로'] optgroup:last-child option\")].map(o => o.innerText) })", "expect": {"loop": true, "groups": ["고정 경로", "상대 경로 (기체 위치 기준)"], "relative": ["사각형 수색 300m", "지그재그 수색 600m", "원 선회 200m", "북쪽으로 1km"]}},
 {"select": ["select[aria-label='경로']", "square_300"], "wait": 400},
 {"label": "R2 the card names the relative route", "eval": "document.querySelector(\".react-flow__node[data-id='step-1'] .sn-text\")?.innerText", "expect": "경로 비행 · 사각형 수색 300m · 반복 · 기체 위치 기준"},
 {"clickSel": ".react-flow__node", "wait": 500},
 {"label": "R3 the hold card's new link is arrival", "eval": "document.querySelector(\"select[aria-label='연결 1 조건']\")?.value", "expect": "arrived"},
 {"select": ["select[aria-label='연결 1 조건']", "at_time"], "wait": 300},
 {"type": ["input[aria-label='연결 1 분']", "0"], "wait": 200},
 {"type": ["input[aria-label='연결 1 초']", "30"], "wait": 300},
 {"label": "R4 the link reads T+0:30 on the graph", "eval": "document.querySelector('.react-flow')?.innerText.includes('T+0:30')", "expect": true},
 {"click": "저장", "wait": 1500},
 {"label": "R5 saved", "eval": "document.querySelector('.save-ok')?.innerText ?? document.querySelector('.save-bad')?.innerText", "match": "저장됨"},
 {"nav": "/?qa=routes#editor", "wait": 4000},
 {"click": "▶ 시뮬레이션", "wait": 4000},
 {"label": "R6 live, paused at the start; remember d3 and d4", "eval": "(window.__before = Object.fromEntries([...document.querySelectorAll('.mk.vehicle')].map(i => [i.querySelector('span').innerText, i.parentElement.style.transform])), document.querySelector('.runbar .clock')?.innerText)", "match": "T\\+0:0"},
 {"click": "×30", "wait": 3000},
 {"click": "⏸ 일시정지", "wait": 600},
 {"label": "R7 past T+0:30 d3 and d4 have left the base on the square", "eval": "(() => { const now = Object.fromEntries([...document.querySelectorAll('.mk.vehicle')].map(i => [i.querySelector('span').innerText, i.parentElement.style.transform])); return ['d3', 'd4'].every(k => now[k] !== window.__before[k]); })()", "expect": true},
 {"shot": "routes-live-24h.png"}
]
```

(실제 화면에서 요소 이름이 다르면 — 예: "저장" 결과 문구, 클릭 대상 글자 — 화면을 보고 선택자만 고친다. 기대 값의 뜻은 바꾸지 않는다. 저장된 플레이는 이 gateway 메모리에만 있고 끝나면 버린다.)

Run: `node scripts/qa/run.mjs --check scripts/qa/route_select.json` → OK

- [ ] **Step 2: 실제 실행** — 빌드한 UI로 8021 포트 gateway(`KDTH_UI_DIST=<worktree>/modules/cop-ui/dist .venv/bin/uvicorn modules.gateway.app:create_app --factory --port 8021`, 백그라운드), Chrome 9349(`--headless=new --remote-debugging-port=9349 --use-angle=swiftshader --enable-unsafe-swiftshader --user-data-dir=<scratchpad>/chrome`), `QA_PORT=9349 QA_BASE=http://localhost:8021 QA_OUT=<scratchpad>/qa node scripts/qa/run.mjs scripts/qa/route_select.json scripts/qa/card_edit.json`. 스크린샷을 직접 본다. 끝나면 두 프로세스를 pid로 끈다(pkill -f에 자기 명령이 걸리지 않게).

- [ ] **Step 3: BUILT_HERE 한 줄 + 커밋**

```markdown
| 10/10 HH:MM | contracts, runtime, sim, gateway, cop-ui, demo | Part1-31 경로 선택과 offset 행동(결정 0044·0045): 시나리오 경로 목록(고정·상대), 편집기 '경로 비행 + 반복'과 경로 선택칸(경로 카드에만), 상대 경로는 카드 진입 때 기체 위치 기준, 반복 없는 경로는 끝점에서 도착, 연결 조건 T+ 시각(at_time). 화면 점검 scripts/qa/route_select.json | kth9245 |
```

```bash
git add scripts/qa/route_select.json demo/BUILT_HERE.md
git commit -m "Part1-31: route select screen QA checklist and BUILT_HERE line"
```

- [ ] **Step 4: 전체 검토 → 수정 → ship → 완료**
- 전체 브랜치 검토(가장 강한 모델의 새 검토자). Critical·Important는 실패 테스트 먼저 쓰고 고친다.
- `scripts/ship.sh`, `uv run python scripts/task.py done Part1-31`.
- 리드에게 채팅용 알림 문구를 준다: 황승주(runtime `route_command`·`step_vehicle` started_ms, play 정적 검사는 상대 경로 생략), 최동호(sim `follow_route` loop, engine.py 한 줄).
