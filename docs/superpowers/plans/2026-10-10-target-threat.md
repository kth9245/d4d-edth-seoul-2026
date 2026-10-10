# 표적 위협도 판단 Implementation Plan (Part2-28)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 표적 위협 점수를 매 틱 계산해 `Target`에 쓴다. 화면(리드)이 기존 발견 카드(`target_detected`)에 점수·이유를 보이고 점수순으로 정렬한다. 별도 위협 카드는 없다(결정 0039, 보정 0040).

**Architecture:** 점수 계산은 이미 만든 sensing 순수 함수 `score_target`(SNS-03, 완료). 이번에는 (1) 계약에 기본값 있는 필드를 더하고, (2) sim이 방출 시각에 `Target.emitting`을 켜고, (3) gateway 액션이 점수를 `Target`에 쓰고(종류는 `seen_by`가 있을 때만 실제 종류, 아니면 미상), (4) `engine.py`가 호출 순서만 더하고, (5) 시나리오 JSON에 값을 넣는다.

**Tech Stack:** Python, pydantic 계약(`contracts/models`), pytest(`uv run pytest modules/<m>`, 디버깅은 `-n 0`).

**Spec:** `decisions/log/0039-…md`(규칙), `decisions/log/0040-…md`(보정: 위협 카드 없음, 스캔 판별, 화면은 리드), 초안 문서 `~/threat-spike/2026-10-10-threat-level-design.md`.

## Global Constraints

- 새 필드는 모두 기본값을 둔다(기존 예시·시나리오 JSON이 그대로 통과해야 한다).
- 점수는 0.01 단위 정수(0.90 = 90), 누적은 점수(0.01 단위)×ms. 누적 기준 `450_000`, 기준치 40(`score_target`이 이미 적용). 누적은 `Target.threat_accum`에 기록만 한다(카드로 올릴지 거르는 용도는 나중).
- 별도 위협 카드는 만들지 않는다(0040). `ReportKind.threat_high`, `Report.threat`·`speed_mps`는 없다. cop-ui(카드 점수·이유, 점수순 정렬, 지도 "RF" 이름표)는 리드가 한다. 우리는 화면이 읽을 `Target` 필드까지 만든다.
- 화면에는 `rf_detected`만 쓰고 `emitting`은 쓰지 않는다.
- 액션 파일: 공개 함수 1개, 이름 = 파일 이름, 80줄 이하. `engine.py`는 호출 순서만.
- 다른 모듈은 `from modules.<m> import ...`로만 부른다.
- 결정 0024: happy path만. 엣지 케이스를 이유로 코드·테스트를 늘리지 않는다.
- 레거시 공개 API(`load_scenario`·`simulate`·`Engine`)는 바꾸지 않는다.
- 시나리오 좌표는 바꾸지 않는다. 필드만 더한다. 시나리오 B(결정 0036)가 main에 올라간 뒤에만 JSON을 만진다.

## Review Focus

- 스캔 전(`seen_by` 비어 있음)에는 종류가 미상(0.30)으로 계산되고, 잡힌 뒤 실제 종류가 된다(Task 3).
- 관찰이 끊기면 누적이 0이 되고 다시 관찰되면 처음부터 쌓는다(Task 3).
- 무력화된 표적은 점수를 더 이상 갱신하지 않는다(Task 3).
- 방출이 시작되기 전(`emit_start_offset_ms` 이전)에는 `emitting`이 꺼져 있다(Task 2).
- 기존 시나리오·예시 JSON(필드 없음)이 계속 로드된다(Task 1).

---

### Task 1: 계약 필드 추가

**Files:**
- Modify: `contracts/models/events.py` (`Target`)
- Modify: `contracts/models/world.py` (`VehicleSpec`, `EnemySpec`, 새 `WatchPoint`)
- Modify: `contracts/models/frame.py` (`Scenario`), `contracts/models/__init__.py` (export `WatchPoint`)
- Test: `tests/test_contracts_threat.py` (새 파일, 기존 `tests/test_contracts.py` 옆)

**Interfaces:**
- Produces: `Target.emitting: bool = False`, `Target.rf_detected: bool = False`, `Target.threat: int = 0`, `Target.threat_reasons: list[str] = []`, `Target.threat_accum: int = 0`; `VehicleSpec.rf_range_m: float = 0`; `EnemySpec.emit_start_offset_ms: int | None = None`; `WatchPoint(id: str, name: str, pos: GeoPoint, radius_m: float)`; `Scenario.watch_points: list[WatchPoint] = []`.

- [ ] **Step 1: 실패하는 테스트**

```python
from contracts.models import EnemySpec, GeoPoint, Scenario, Target, VehicleSpec, WatchPoint
from modules.sim import load_scenario_json

P = GeoPoint(lat=37.98, lon=124.7)


def test_new_threat_fields_default_off():
    t = Target(
        id="b", kind="boat", pos=P, vel_east_mps=0, vel_north_mps=0, first_seen_ms=0, last_seen_ms=0
    )
    assert (t.emitting, t.rf_detected, t.threat, t.threat_reasons, t.threat_accum) == (
        False,
        False,
        0,
        [],
        0,
    )


def test_watch_point_and_rf_fields_exist():
    w = WatchPoint(id="landing", name="상륙 예상 지점", pos=P, radius_m=2000)
    assert w.radius_m == 2000
    assert VehicleSpec.model_fields["rf_range_m"].default == 0
    assert EnemySpec.model_fields["emit_start_offset_ms"].default is None
    assert Scenario.model_fields["watch_points"].default == []


def test_existing_demo_scenario_still_loads():
    assert load_scenario_json("demo/scenarios/baengnyeong_night.json").watch_points == []
```

- [ ] **Step 2: 실패 확인** — `uv run pytest tests/test_contracts_threat.py -n 0 -q` → ImportError(`WatchPoint`).
- [ ] **Step 3: 구현** — 위 인터페이스대로 필드를 더한다.
- [ ] **Step 4: 통과 확인** — 같은 명령 PASS. 커밋하면 pre-commit이 `scripts/gen_contracts.py`로 스키마·TS를 재생성해 같이 스테이징한다(수동 편집 금지).
- [ ] **Step 5: `uv run pytest tests modules/gateway modules/sim -q`로 기존 테스트가 통과하는지 확인 후 커밋.** 황승주의 0037 계약 변경(이미 main)과 순서가 겹치지 않게 최신 main에 rebase한 뒤 ship.

---

### Task 2: sim `update_emission`

**Files:**
- Create: `modules/sim/actions/update_emission.py` (`uv run python scripts/new_action.py sim update_emission "…"`로 시작)
- Test: `modules/sim/tests/test_update_emission.py`
- Modify: `modules/sim/__init__.py` (export)

**Interfaces:**
- Consumes: Task 1의 `EnemySpec.emit_start_offset_ms`, `Target.emitting`.
- Produces: `update_emission(scenario: Scenario, targets: list[Target], t_ms: int) -> list[Target]` — 적 `e`의 표적은 `t_ms >= started_ms + e.appear_offset_ms + e.emit_start_offset_ms`이면 `emitting=True`(한 번 켜지면 계속). `None`이면 항상 False.

- [ ] **Step 1: 실패하는 테스트** — 시나리오를 `load_scenario_json`으로 읽은 뒤 `enemies`의 `emit_start_offset_ms`만 `model_copy`로 고쳐 쓴다(한 척은 `0`, 한 척은 `None`). 표적 둘을 직접 만들고, appear 시각 직전엔 둘 다 False, 직후엔 `0`인 쪽만 True, `None`인 쪽은 계속 False를 assert한다. `emit_start_offset_ms=60_000`인 적은 appear 후 59.8 s엔 False, 60 s엔 True.
- [ ] **Step 2: 실패 확인** (`NotImplementedError` 또는 ImportError).
- [ ] **Step 3: 구현** (약 10줄: `offsets = {e.id: (e.appear_offset_ms, e.emit_start_offset_ms) ...}` → `model_copy(update={"emitting": True})`).
- [ ] **Step 4: 통과 확인** `uv run pytest modules/sim -q`.
- [ ] **Step 5: 커밋.**

---

### Task 3: gateway `score_targets`

**Files:**
- Create: `modules/gateway/actions/score_targets.py`
- Test: `modules/gateway/tests/test_score_targets.py`

**Interfaces:**
- Consumes: `modules.sensing.score_target`(SNS-03), Task 1 필드, `VehicleState`, `VehicleSpec.rf_range_m`, `WatchPoint`.
- Produces: `score_targets(states: list[VehicleState], specs: dict[str, VehicleSpec], targets: list[Target], watch_points: list[WatchPoint], tick_ms: int) -> list[Target]` — 무력화(`neutralized_ms`)된 표적은 그대로 둔다. 나머지는 `threat`, `threat_reasons`, `rf_detected`, `threat_accum`을 채운다. 종류는 `seen_by`가 비어 있으면 `"unknown"`, 아니면 `Target.kind.value`로 넘긴다(0040, 이유에 `kind_<종류>`가 남아 화면이 "스캔 판별"을 표시할 수 있다). 수신 기체는 `status in (ready, active)`이고 `rf_range_m > 0`인 것(`observe`와 같은 "살아 있는" 정의).

- [ ] **Step 1: 실패하는 테스트** — 기체 d2(`rf_range_m=2000`, 표적과 500 m)와 fast1(`emitting=True`, 속도 6.3 m/s, `seen_by=["d2"]`, 기준점 반경 안)을 만들어 `threat == 100`, `rf_detected` True, `threat_accum == 100 * tick_ms`를 assert. 두 번째 호출에서 `threat_accum`이 `2 * 100 * tick_ms`로 이어지고, `seen_by=[]`로 바꾸면 `threat_accum == 0`이고 이유에 `kind_unknown`이 있는 것도 같은 파일의 테스트로 둔다. 무력화된 표적은 입력과 같은지도 하나.
- [ ] **Step 2: 실패 확인.**
- [ ] **Step 3: 구현** — `speed = hypot(vel_east_mps, vel_north_mps)`, `observed = bool(seen_by)`, `receivers = [(s.pos, specs[s.id].rf_range_m) for s in states if s.status in LIVE]`, `watch = [(w.pos, w.radius_m) for w in watch_points]`, 결과를 `model_copy(update=...)`.
- [ ] **Step 4: 통과 확인** `uv run pytest modules/gateway -q`.
- [ ] **Step 5: 커밋.**

---

### Task 4: `engine.py` 연결

**Files:**
- Modify: `modules/gateway/engine.py` (호출 두 줄), `contracts/API.md` §3 틱 순서(`1.6 update_emission`, `2.5 score_targets`)
- Test: `modules/gateway/tests/test_engine_threat.py`

**Interfaces:**
- Consumes: Task 2·3의 두 함수. `update_emission`은 `steer_enemies` 직후, `score_targets`는 `observe` 직후.

- [ ] **Step 1: 실패하는 테스트** — 데모 시나리오를 `init_engine`으로 만든 뒤 `watch_points`·`rf_range_m`·`emit_start_offset_ms`를 `model_copy`로 직접 넣고(Task 5 전이라 JSON은 아직 그대로), 틱 루프를 fast 계열 적 등장 후 10 s까지 돌려 그 표적의 `threat`가 100이고 `threat_accum`이 450_000을 넘었는지 assert.
- [ ] **Step 2: 실패 확인** (`threat`가 0).
- [ ] **Step 3: 구현** (`engine.py`는 호출 순서만).
- [ ] **Step 4: 통과 확인** `uv run pytest modules/gateway -q` + `uv run python scripts/smoke.py`.
- [ ] **Step 5: 커밋, `scripts/ship.sh`.**

---

### Task 5: 시나리오 값과 시연 시나리오 테스트

**선행:** 시나리오 B(결정 0036)가 main에 올라간 뒤에 시작한다. 올라온 뒤 위협도 숫자를 다시 돌려 시각을 확인한다. B의 카드 시각: boat1 16:21, boat2 16:22, boat3 17:52, fast1 23:00.

**Files:**
- Modify: `demo/scenarios/baengnyeong_night.json` (최신 `origin/main`에 rebase한 뒤)
- Modify: `demo/BUILT_HERE.md` (위협도 판단 한 줄)
- Test: `modules/gateway/tests/test_demo_threat.py`

- [ ] **Step 1: 실패하는 테스트** — `test_demo_timeline.py`와 같은 운영자 스크립트로 35분을 돌린 뒤: ① 적 3척이 모두 관찰되면 `threat`가 채워졌다, ② fast 계열은 처음 관찰된 틱에 `threat == 100`, ③ 방출을 늦게 시작하는 적 한 척은 발견 카드가 뜬 **뒤**에 `rf_detected`가 켜지며 `threat`가 정확히 30 오른다(점수가 오르고 카드가 맨 위로 올라가는 장면, 리드 7번).
- [ ] **Step 2: 실패 확인.**
- [ ] **Step 3: JSON 편집** — `d1`·`d2`: `"rf_range_m": 2000`(usv·ugv는 기본 0). 적 한 척 이상(boat2 또는 fast1): 발견 카드가 뜬 **뒤** 방출을 시작하도록 `emit_start_offset_ms`와 `rf_range_m`을 맞춘다. 나머지 적은 필드 없음(무음). `"watch_points": [{"id":"landing","name":"상륙 예상 지점","pos":{"lat":37.978,"lon":124.70},"radius_m":2000}]`. 좌표·시각은 건드리지 않는다.
- [ ] **Step 4: 통과 확인** `uv run pytest -q`(전체) + `scripts/smoke.py`. 예시 재생성이 필요하면 리드 작업 흐름대로 돌린다.
- [ ] **Step 5: 커밋, `scripts/ship.sh`, `task.py done Part2-28`, 리드에게 `Target` 필드가 올라갔다고 알림(화면 작업 시작 신호).**

---

## Self-Review

- 스펙 커버: 점수·누적(SNS-03 완료, Task 3), 방출(Task 2), 틱 순서(Task 4), 시나리오(Task 5), 계약(Task 1), 스캔 판별(Task 3). 카드 점수 표시·정렬·RF 이름표는 리드(cop-ui). 카드로 올릴지 거르는 누적 기준 연결은 나중.
- 타입 일관성: `threat_accum`은 점수(0.01)×ms 정수, 기준 `450_000`. 모든 새 `Target` 필드는 Task 1에서 정의하고 Task 3이 쓴다.
- 위험: Task 5는 리드의 시나리오 B와 같은 파일을 만진다. B가 올라온 뒤 rebase해서 필드만 더한다.
