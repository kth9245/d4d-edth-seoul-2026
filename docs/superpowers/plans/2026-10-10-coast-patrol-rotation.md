# 해안 순찰 24시간 교대 + "전 기체 순찰" 버튼 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 드론 3대가 북(A)·남(B) 해안을 교대로 늘 1대씩 순찰하는 엔진 로직과, 시연 화면의 노란 "전 기체 순찰" 버튼.

**Architecture:** 계약 3칸(기본값으로 기존 동작 유지) → sim 충전 → runtime 새 액션 `rotate_patrols`(틱 순서 4.5) → 별도 24h 시나리오와 24시간 증명 테스트 → 시연 시나리오에 해안 플레이·전환 버튼 추가(화면 코드는 그대로, 버튼은 `operation.switches`에서 자동 생성).

**Tech Stack:** Python 3.12, pydantic, pytest(-n auto), 팀 스크립트(new_action.py·task.py·ship.sh).

**Spec:** `docs/superpowers/specs/2026-10-10-coast-patrol-rotation-design.md` (결정 0037)

## Global Constraints

- 체공 90분·교체 10분은 **24h 시나리오에만**. 시연 시나리오 드론 체공 40분 그대로(시간표 보존), `recharge_min`만 10.
- 착륙 배터리 하한 30%, 교대 시작 여유 5%(기준 35%), 인계 거리 500 m.
- A = 북쪽 해안 `coast_a`("해안 순찰 A · 북"), B = 남쪽 `coast_b`("해안 순찰 B · 남").
- 액션 파일 80줄 이하, 다른 모듈은 공개 API로만, 모든 변경 TDD, 작업마다 worktree → `scripts/ship.sh` → `task.py done`.
- 화면에 `confirm/alert/prompt` 금지.

## Review Focus

1. 대기 기체가 없을 때 순찰 기체 배터리가 바닥남 → 하한선 우선: 귀환 배터리 기준(30% + 귀환 소모) 도달 시 교대 없이도 귀환. Task 3 테스트 `test_no_relief_still_goes_home_at_the_floor`.
2. 시연 시나리오에 충전이 들어가 19분 d1 귀환 뒤 d1이 다시 ready가 됨 → 기존 시간표·smoke 테스트가 그대로 통과해야 함. Task 5 검증 단계.
3. 버튼을 다시 눌러 같은 플레이에 기체가 둘 → 교대 쌍으로 오인. 인계는 교대 출발 기록(배정 사유)이 있는 쌍만. Task 3 테스트 `test_two_on_one_play_without_relief_record_is_not_a_handover`.
4. 교대 기체가 순찰 기체를 못 따라잡음 → 교대 시작 시 만날 경로점 m을 고정하고, 인계 전까지 순찰 기체는 m에 머물게 함. Task 3 테스트 `test_relief_and_outgoing_meet_at_the_fixed_waypoint`.
5. 24시간 동안 A·B가 같은 때 교대 기준 도달 → d2 시작 배터리 60%로 엇갈림. Task 4 증명 테스트가 공백 0초로 잡음.

---

### Task 1: 계약 3칸 (리드 영역, 사용자 지시로 진행)

**Files:**
- Modify: `contracts/models/world.py` (`VehicleSpec`, `Operation`), `contracts/API.md`
- Regenerate: `uv run python scripts/gen_contracts.py` (schema·TS)
- Test: `tests/test_contracts.py`

**Interfaces:**
- Produces: `VehicleSpec.recharge_min: float = 0`, `Operation.rotation: list[str] = []`(교대 기체), `Operation.rotation_plays: list[str] = []`(교대로 지키는 순찰 플레이).

- [ ] Step 1: 테스트 `test_rotation_fields_default_to_no_rotation`: 기존 예시 `operation.json`·`vehicle_spec` 로드 시 `rotation == []`, `rotation_plays == []`, `recharge_min == 0`.
- [ ] Step 2: 실행 → FAIL(AttributeError).
- [ ] Step 3: 세 칸 추가, API.md 1절(칸 설명)·3절(틱 순서 4.5 `rotate_patrols`), gen_contracts.
- [ ] Step 4: `uv run pytest tests/test_contracts.py tests/test_gen_contracts.py` → PASS.
- [ ] Step 5: 커밋·ship.

### Task 2: sim 충전 (최동호 영역, 사용자 지시로 진행)

**Files:**
- Modify: `modules/sim/actions/advance_vehicles.py` (SIM-08)
- Test: `modules/sim/tests/test_advance_vehicles.py`

- [ ] Step 1: 테스트 `test_maintenance_recharges_to_ready`: `recharge_min=10`, 배터리 30%, maintenance, 기지 위 → 10분 분량 틱 뒤 배터리 100, 상태 ready, play_id·step_id None. `test_no_recharge_when_recharge_min_is_zero`: 그대로 maintenance.
- [ ] Step 2: FAIL 확인.
- [ ] Step 3: maintenance 분기에서 `spec.recharge_min > 0`이면 배터리 `+100/recharge_min × dt분`, 100 이상이면 100·ready·play/step 비움.
- [ ] Step 4: `uv run pytest modules/sim` PASS. 커밋·ship.

### Task 3: runtime `rotate_patrols` (RT-10, 황승주)

**Files:**
- Create: `uv run python scripts/new_action.py runtime rotate_patrols "..."` → `modules/runtime/actions/rotate_patrols.py`, `modules/runtime/tests/test_rotate_patrols.py`
- Modify: `modules/runtime/__init__.py`(공개), `modules/runtime/AGENTS.md` 공개 API 줄

**Interfaces:**
- Consumes: Task 1 칸, `switch_play`, `shared.geo.dist_m`.
- Produces: `rotate_patrols(states: list[VehicleState], specs: dict[str, VehicleSpec], op: Operation, plays: dict[str, Play], assignments: list[Assignment], t_ms: int) -> tuple[list[VehicleState], list[Assignment]]`.

규칙(`op.rotation`·`rotation_plays` 비면 입력 그대로):
- 순찰 기체 S = rotation 기체 중 `active`·play ∈ rotation_plays. 소모율 = `100/endurance_min`(%/분), 귀환 소모 = 소모율 × dist(S, home)/speed/60.
- **하한선**: `battery − 귀환 소모 ≤ 30`이면 S를 `go_home`으로(사유 "교대 귀환(하한선): S").
- **교대 출발**: S가 그 플레이 유일 기체이고 출발 기록이 없으며 `battery − 2 × 귀환 소모 ≤ 35`이면 rotation 순서상 S 다음부터 첫 R(ready, 배터리 ≥ 99.9, play ∉ rotation_plays) → `switch_play(R, plays[S.play_id])`. m = S의 현재 `waypoint_idx`. 배정 사유 `"교대 출발: R → S @m"`.
- **만남**: 출발 기록(사유 파싱)이 있는 쌍은 매 틱 R·S의 `waypoint_idx = m`(R은 enter_step 뒤 0이 되므로 매 틱 덮어씀, S는 m에 머묾).
- **인계**: 쌍이 500 m 안 → S `go_home`, 사유 `"교대 완료: R ← S"`, 출발 기록 제거.

- [ ] Step 1: 테스트(이름·단정): `test_no_rotation_returns_input`, `test_relief_starts_at_the_threshold`(R play=S play, 배정 사유 "교대 출발: d3 → d1 @2"), `test_no_relief_before_the_threshold`, `test_relief_and_outgoing_meet_at_the_fixed_waypoint`(쌍 모두 waypoint_idx 2), `test_handover_within_500_m_sends_outgoing_home`(S play go_home, 사유 "교대 완료: d3 ← d1"), `test_no_ready_relief_keeps_patrolling`, `test_no_relief_still_goes_home_at_the_floor`, `test_two_on_one_play_without_relief_record_is_not_a_handover`.
- [ ] Step 2: FAIL 확인.
- [ ] Step 3: 구현(80줄 이하).
- [ ] Step 4: `uv run pytest modules/runtime` PASS. 커밋·ship·task done.

### Task 4: engine 4.5 호출 + 24h 시나리오 + 증명 테스트

**Files:**
- Modify: `modules/gateway/engine.py`(4 다음 `states, assigns = rotate_patrols(states, specs, sc.operation, plays, assigns, t)`)
- Create: `scripts/make_coast_routes.py`(`Scenario.land` 바다 쪽 400 m, 약 900 m 간격, 북/남 분할, 왕복 순서), `demo/scenarios/baengnyeong_24h.json`, `tests/test_patrol_rotation_24h.py`

24h 시나리오: d1·d2·d3(공중, 90분, recharge 10, 속도 15, home 기존), assign `{d1: coast_a, d2: coast_b, d3: standby}`, rotation `[d1,d2,d3]`, rotation_plays `[coast_a, coast_b]`, reserve `{}`, plays coast_a·coast_b·standby·go_home, 사건 `vehicle_battery_set {id: d2, pct: 60}` 0초, `tick_ms 1000`, 작전 구역·영역은 시연 시나리오와 같음, `land` 같음.

- [ ] Step 1: 테스트 `test_both_coasts_always_covered_for_24h`(30분 이후 매 틱 coast_a·coast_b 각각 active·비귀환 ≥1), `test_landings_keep_30_percent`(기지 도착 순간 배터리 ≥ 30), 교대 완료 횟수 출력.
- [ ] Step 2: FAIL 확인(시나리오 없음).
- [ ] Step 3: 스크립트로 경로 생성·JSON 작성, engine 호출 추가.
- [ ] Step 4: `uv run pytest tests/test_patrol_rotation_24h.py` PASS, 전체 pytest·smoke PASS. 커밋·ship.

### Task 5: 시연 시나리오 "전 기체 순찰" 버튼

**Files:**
- Modify: `demo/scenarios/baengnyeong_night.json`(결정 0035 원본): plays에 coast_a·coast_b(Task 4 경로), `operation.switches`에 `{"id": "patrol_all", "label": "전 기체 순찰", "play_by_vehicle": {"d1": "coast_a", "d2": "coast_b", "d3": "go_home"}}`, `rotation [d1,d2,d3]`, `rotation_plays [coast_a, coast_b]`, d1·d2·d3 `recharge_min 10`.
- 필요 시 `demo/plays/coast_a.json`·`coast_b.json`(편집기 목록), `uv run python scripts/gen_examples.py`.
- Test: `tests/test_demo_scenario.py`에 `test_patrol_all_switch_rotates_the_three_drones`(버튼 승인 뒤 d1 coast_a·d2 coast_b, check_operation 통과).

- [ ] Step 1: 테스트 작성 → FAIL.
- [ ] Step 2: JSON 수정.
- [ ] Step 3: 전체 pytest(시간표·smoke 포함) PASS — 깨지면 원인 보고(남의 테스트 수정 금지).
- [ ] Step 4: 개발 서버 화면에 노란 "전 기체 순찰" 버튼 확인 → 누르고 승인 → d1·d2 해안으로 이동 확인. 커밋·ship·BUILT_HERE.
