# 표적 위협도 판단 Implementation Plan (Part2-28)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 표적 위협 점수를 매 틱 계산하고, 점수 0.40 이상인 동안의 누적이 4.5를 넘으면 표적당 한 번 `threat_high` 카드를 낸다(결정 0039).

**Architecture:** 점수 계산은 이미 만든 sensing 순수 함수 `score_target`(SNS-03, 완료). 이번에는 (1) 계약에 기본값 있는 필드를 더하고, (2) sim이 방출 시각에 `Target.emitting`을 켜고, (3) gateway 액션 두 개가 점수를 `Target`에 쓰고 카드를 만들고, (4) `engine.py`가 호출 순서만 더하고, (5) 시나리오 JSON에 값을 넣는다.

**Tech Stack:** Python, pydantic 계약(`contracts/models`), pytest(`uv run pytest modules/<m>`, 디버깅은 `-n 0`).

**Spec:** `decisions/log/0039-표적-위협도-규칙-…md`, 초안 문서 `~/threat-spike/2026-10-10-threat-level-design.md`(개정 2).

## Global Constraints

- 새 필드는 모두 기본값을 둔다(기존 예시·시나리오 JSON이 그대로 통과해야 한다).
- 점수는 0.01 단위 정수(0.90 = 90), 누적은 점수(0.01 단위)×ms. 카드 기준 `450_000`, 기준치 40(`score_target`이 이미 적용).
- 액션 파일: 공개 함수 1개, 이름 = 파일 이름, 80줄 이하. `engine.py`는 호출 순서만.
- 다른 모듈은 `from modules.<m> import ...`로만 부른다.
- 결정 0024: happy path만. 엣지 케이스를 이유로 코드·테스트를 늘리지 않는다.
- 레거시 공개 API(`load_scenario`·`simulate`·`Engine`)는 바꾸지 않는다.
- 시나리오 좌표는 바꾸지 않는다. 필드만 더한다(`baengnyeong_night.json`은 리드가 시나리오 B로 고치는 중이니 맨 마지막 task에서 최신 main에 rebase한 뒤 만진다).
- 카드는 선택지 없는 알림 카드(`target_neutralized`와 같은 방식)다. 선택지·"계속 관찰"은 아직 미정이라(문서 7절 1·4·9번) 이 계획에 넣지 않는다.

## Review Focus

- 위협 카드가 같은 표적에 두 번 뜨지 않는다(Task 4 테스트).
- 무력화된 표적은 더 이상 카드를 내지 않는다(Task 3·4).
- 관찰이 끊기면 누적이 0이 되고 다시 관찰되면 처음부터 쌓는다(Task 3).
- 방출이 시작되기 전(`emit_start_offset_ms` 이전)에는 `emitting`이 꺼져 있다(Task 2).
- 기존 시나리오·예시 JSON(필드 없음)이 계속 로드된다(Task 1).

---

### Task 1: 계약 필드 추가

**Files:**
- Modify: `contracts/models/events.py` (`Target`, `Report`)
- Modify: `contracts/models/enums.py` (`ReportKind`)
- Modify: `contracts/models/world.py` (`VehicleSpec`, `EnemySpec`, 새 `WatchPoint`)
- Modify: `contracts/models/frame.py` (`Scenario`), `contracts/models/__init__.py` (export `WatchPoint`)
- Test: `tests/test_contracts_threat.py` (새 파일, 기존 `tests/test_contracts.py` 옆)

**Interfaces:**
- Produces: `Target.emitting: bool = False`, `Target.rf_detected: bool = False`, `Target.threat: int = 0`, `Target.threat_reasons: list[str] = []`, `Target.threat_accum: int = 0`, `Target.threat_reported: bool = False`; `Report.threat: int | None = None`, `Report.speed_mps: float | None = None`; `ReportKind.threat_high`; `VehicleSpec.rf_range_m: float = 0`; `EnemySpec.emit_start_offset_ms: int | None = None`; `WatchPoint(id: str, name: str, pos: GeoPoint, radius_m: float)`; `Scenario.watch_points: list[WatchPoint] = []`.

- [ ] **Step 1: 실패하는 테스트**

```python
from contracts.models import EnemySpec, GeoPoint, Report, Scenario, Target, VehicleSpec, WatchPoint
from modules.sim import load_scenario_json

P = GeoPoint(lat=37.98, lon=124.7)


def test_new_threat_fields_default_off():
    t = Target(id="b", kind="boat", pos=P, vel_east_mps=0, vel_north_mps=0,
               first_seen_ms=0, last_seen_ms=0)
    assert (t.emitting, t.rf_detected, t.threat, t.threat_reasons, t.threat_accum) == (
        False, False, 0, [], 0)
    r = Report(id="r", t_ms=0, kind="threat_high", text="")
    assert (r.threat, r.speed_mps) == (None, None)


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
- [ ] **Step 3: 구현** — 위 인터페이스대로 필드를 더한다. `Target`에 넣는 `threat_reported`는 "이 표적의 `threat_high` 카드를 이미 냈다"는 표시다(Task 4가 쓴다. 보고서를 뒤져 찾는 것보다 단순하다).
- [ ] **Step 4: 통과 확인** — 같은 명령 PASS. 커밋하면 pre-commit이 `scripts/gen_contracts.py`로 스키마·TS를 재생성해 같이 스테이징한다(수동 편집 금지).
- [ ] **Step 5: `uv run pytest tests modules/gateway modules/sim -q`로 기존 테스트가 그대로 통과하는지 확인 후 커밋.** 리드에게 계약 변경 알림(결정 0039 승인됨).

---

### Task 2: sim `update_emission`

**Files:**
- Create: `modules/sim/actions/update_emission.py` (`uv run python scripts/new_action.py sim update_emission "…"`로 시작)
- Test: `modules/sim/tests/test_update_emission.py`
- Modify: `modules/sim/__init__.py` (export)

**Interfaces:**
- Consumes: Task 1의 `EnemySpec.emit_start_offset_ms`, `Target.emitting`.
- Produces: `update_emission(scenario: Scenario, targets: list[Target], t_ms: int) -> list[Target]` — 적 `e`의 표적은 `t_ms >= started_ms + e.appear_offset_ms + e.emit_start_offset_ms`이면 `emitting=True`(한 번 켜지면 계속). `None`이면 항상 False.

- [ ] **Step 1: 실패하는 테스트** — 시나리오를 `load_scenario_json`으로 읽은 뒤 `enemies`의 `emit_start_offset_ms`만 `model_copy`로 고쳐 쓴다(fast1 `0`, boat1 `None`). 표적 둘을 직접 만들고, `appear` 시각 직전엔 `emitting`이 둘 다 False, 직후엔 fast1만 True, boat1은 계속 False를 assert한다.
- [ ] **Step 2: 실패 확인** (`NotImplementedError` 또는 ImportError).
- [ ] **Step 3: 구현** (약 10줄: `offsets = {e.id: e.emit_start_offset_ms ...}` → `model_copy(update={"emitting": True})`).
- [ ] **Step 4: 통과 확인** `uv run pytest modules/sim -q`.
- [ ] **Step 5: 커밋.**

---

### Task 3: gateway `score_targets` (GW-10)

**Files:**
- Create: `modules/gateway/actions/score_targets.py`
- Test: `modules/gateway/tests/test_score_targets.py`

**Interfaces:**
- Consumes: `modules.sensing.score_target`(SNS-03), Task 1 필드, `VehicleState`, `VehicleSpec.rf_range_m`, `Scenario.watch_points`.
- Produces: `score_targets(states: list[VehicleState], specs: dict[str, VehicleSpec], targets: list[Target], watch_points: list[WatchPoint], tick_ms: int) -> list[Target]` — 무력화(`neutralized_ms`)된 표적과 아직 나타나지 않은 표적은 그대로 둔다. 나머지는 `threat`, `threat_reasons`, `rf_detected`, `threat_accum`을 채운다. 수신 기체는 `status in (ready, active)`이고 `rf_range_m > 0`인 것(`observe`와 같은 "살아 있는" 정의).

- [ ] **Step 1: 실패하는 테스트** — 기체 d2(`rf_range_m=2000`, 표적과 500 m)와 fast1(`emitting=True`, 속도 6.3 m/s, `seen_by=["d2"]`, 기준점 반경 안)을 만들어 `threat == 100`, `rf_detected` True, `threat_accum == 100 * tick_ms`를 assert. 두 번째 호출에서 `threat_accum`이 `2 * 100 * tick_ms`로 이어지고, `seen_by=[]`로 바꾸면 0이 되는 것도 같은 파일의 테스트로 둔다. 무력화된 표적은 입력과 같은지도 하나.
- [ ] **Step 2: 실패 확인.**
- [ ] **Step 3: 구현** — `speed = hypot(vel_east_mps, vel_north_mps)`, `observed = bool(seen_by)`, `receivers = [(s.pos, specs[s.id].rf_range_m) for s in states if s.status in LIVE]`, `watch = [(w.pos, w.radius_m) for w in watch_points]`, 결과를 `model_copy(update=...)`.
- [ ] **Step 4: 통과 확인** `uv run pytest modules/gateway -q`.
- [ ] **Step 5: 커밋.**

---

### Task 4: gateway `threat_reports` (GW-11)

**Files:**
- Create: `modules/gateway/actions/threat_reports.py`
- Test: `modules/gateway/tests/test_threat_reports.py`

**Interfaces:**
- Consumes: Task 3가 채운 `Target.threat_accum`.
- Produces: `threat_reports(targets: list[Target], t_ms: int) -> tuple[list[Target], list[Report]]` — `threat_accum >= 450_000`이고 `threat_reported`가 False이고 `neutralized_ms`가 None인 표적마다 `Report(id=f"rep-threat-{tg.id}", t_ms=t_ms, kind="threat_high", target_id=tg.id, vehicle_id=tg.seen_by[0] if tg.seen_by else None, text="{id} 관측 위험 점수 {점수/100:.2f} — 운영자 검토용 요청(자동 표적 지정·교전 판단 아님)", threat=tg.threat, speed_mps=속력)`를 만들고 표적의 `threat_reported`를 True로 바꿔 돌려준다.

- [ ] **Step 1: 실패하는 테스트** — 누적 450_000인 표적 → 카드 1장, `threat_reported` True. 같은 표적을 다시 넣으면 카드 0장(중복 방지). 449_999이면 0장. 무력화된 표적은 0장.
- [ ] **Step 2: 실패 확인.**
- [ ] **Step 3: 구현.**
- [ ] **Step 4: 통과 확인.**
- [ ] **Step 5: 커밋.**

---

### Task 5: `engine.py` 연결

**Files:**
- Modify: `modules/gateway/engine.py` (tick 2와 3 사이에 호출 두 줄, 새 카드를 `new_reports`에 합침), `modules/gateway/__init__.py` 확인
- Modify: `contracts/API.md` §3 틱 순서(`2.5 update_emission`, `2.6 score_targets·threat_reports`)
- Test: `modules/gateway/tests/test_engine_threat.py`

**Interfaces:**
- Consumes: Task 2·3·4의 세 함수. 호출 위치: `spawn_enemies/steer_enemies` 직후에 `update_emission`, `observe` 직후에 `score_targets`와 `threat_reports`. 새 카드는 `new_reports += cards`(기존 `new_reports` 초기화 이후라 `reports, assigns = ...` 줄 뒤에 둔다).

- [ ] **Step 1: 실패하는 테스트** — 데모 시나리오를 `init_engine`으로 만든 뒤 `watch_points`·`rf_range_m`·`emit_start_offset_ms`를 `model_copy`로 직접 넣고(Task 6 전이라 JSON은 아직 그대로), 틱 루프를 fast1 등장 후 10 s까지 돌려 `threat_high` 카드가 `fast1`에 대해 정확히 한 장 있는지 assert.
- [ ] **Step 2: 실패 확인** (카드 없음).
- [ ] **Step 3: 구현** (`engine.py`는 호출 순서만).
- [ ] **Step 4: 통과 확인** `uv run pytest modules/gateway -q` + `uv run python scripts/smoke.py`.
- [ ] **Step 5: 커밋.**

---

### Task 6: 시나리오 값과 시연 시나리오 테스트

**Files:**
- Modify: `demo/scenarios/baengnyeong_night.json` (최신 `origin/main`에 rebase한 뒤)
- Modify: `demo/BUILT_HERE.md` (위협도 판단 한 줄)
- Test: `modules/gateway/tests/test_demo_threat.py`

- [ ] **Step 1: 실패하는 테스트** — `test_demo_timeline.py`와 같은 운영자 스크립트(그 파일의 `_inputs`를 import하지 말고 필요한 만큼 복사하거나, 기존 파일에서 공용 헬퍼로 뽑을지 리드와 합의)로 35분을 돌린 뒤: ① 위협 카드가 적마다 최대 한 장, ② 가장 빠르게 오른 표적(fast 계열)의 카드가 처음 관찰 후 5 s 안에 뜬다, ③ 느리고 점수가 낮은 boat 계열 표적도 카드가 뜬다. 정확한 시각은 시나리오 B가 확정되면 값으로 굳힌다(처음엔 위 상대 조건만).
- [ ] **Step 2: 실패 확인.**
- [ ] **Step 3: JSON 편집** — `d1`·`d2`: `"rf_range_m": 2000`(usv·ugv는 기본 0), fast 계열 적: `"emit_start_offset_ms": 0`, boat 계열 적: 필드 없음(무음), `"watch_points": [{"id":"landing","name":"상륙 예상 지점","pos":{"lat":37.978,"lon":124.70},"radius_m":2000}]`. 좌표·시각은 건드리지 않는다.
- [ ] **Step 4: 통과 확인** `uv run pytest -q`(전체) + `scripts/smoke.py`. `scripts/example_world.py`·`gen_examples.py`는 JSON을 읽으므로 예시 재생성이 필요하면 리드 작업 흐름대로 돌린다.
- [ ] **Step 5: 커밋, `scripts/ship.sh`, `task.py done Part2-28`.**

---

## Self-Review

- 스펙 커버: 점수·누적(SNS-03 완료, Task 3), 방출(Task 2), 카드 1회(Task 4), 틱 순서(Task 5), 시나리오(Task 6), 계약(Task 1). 카드 선택지·UI 정렬·`target_found` 연결은 미정이라 제외(Global Constraints에 명시). cop-ui의 `threat_high` 표시와 위협도 순 정렬은 리드 영역이라 별도 요청.
- 타입 일관성: `threat_accum`은 점수(0.01)×ms 정수, 기준 `450_000`. `Target.threat_reported`는 Task 1에서 정의하고 Task 4가 쓴다.
- 위험: Task 6은 리드의 Part1-23.4(시나리오 B)와 같은 파일을 만진다. 맨 마지막에 최신 main에 rebase해서 필드만 더한다.
