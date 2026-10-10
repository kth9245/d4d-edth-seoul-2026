<!-- prefix: RT -->
# runtime SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| RT-01 | step_vehicle | VehicleState, VehicleSpec, Role(기체의 현재 Role), targets, t_ms, started_ms(at_time, 결정 0045) | (state, Command/None, Report/None) | 결정 대기·ready/active 아님이면 그대로, 안 들어간 step이면 enter_step(RT-08), 들어갔으면 on 첫 참으로 전이, 직접 조종 도착이면 resume step으로. 원본: 스파이크 port | 황승주 | 완료 |
| RT-02 | apply_reserves | states, Operation, roles, assignments, t_ms | (states, assignments, Report/None) | 이탈(returning·lost·maintenance) 기체의 op.reserve 첫 ready·active 기체가 그 기체의 Role을 entry step부터 entered_step=False로 시작(결정 0022), Assignment "예비 투입: <id> 대신", vehicle_gap Report(결정 0016) | 황승주 | 완료 |
| RT-03 | apply_decision | states, roles, Decision, reports | (states, reports) | 선택지 role_by_vehicle대로 기체들을 새 Role entry로(entered_step=False), 보고한 기체 pending_report_id 지움, resolved_ms·decision_id 기록. target_select면 target_id = choice_id. 기체 4대 동시 전환 테스트 · 결정 0033: 옮긴 기체에 decision_id·카드 표적, 그 기체의 열린 카드 닫기 | 황승주 | 완료 |
| RT-04 | update_metrics | Metrics, TickOutcome(contracts) | Metrics | 09 2.3 정의 5개 각 1테스트(role_gap → vehicle_gap_ms). 공백 끝 규칙은 contracts/API.md 2절 · mission_success = 표적 하나라도 무력화(결정 0033) | 황승주 | 완료 |
| RT-05 | apply_injection | states, roles, Injection(approved) | states | role_by_vehicle대로 새 Role entry로 전환. 원래 Role은 끝, 자동 복귀 없음(결정 0016) | 황승주 | 완료 |
| RT-06 | apply_direct | states, DirectControl, t_ms | (states, Command) | operator_direct 명령 생성, 도착 시 resume 복귀 | 황승주 | 완료 |
| RT-07 | apply_emergency | states, roles | states | 기체의 현재 Role emergency 규칙(battery_low_pct 등)에 걸리면 그 Role의 지정 step으로 | 황승주 | 완료 |
| RT-08 | enter_step | VehicleState, VehicleSpec, Role, Step, targets, t_ms | (state, Command/None, Report/None) | nearest·operator·고정 표적 각 1테스트, move_to의 target 좌표는 그대로, 귀환 step이면 returning. 원본: 스파이크 port/modules/runtime/actions/enter_step.py · 결정 0033: 출처 decision_id, strike면 params target(표적 위치), 카드 표적은 정해진 표적 우선 | 황승주 | 완료 |
| RT-09 | switch_role | VehicleState, Role | VehicleState | role_id·step_id=entry·entered_step False·target·pending·resume 비움 1테스트. 원본: 스파이크 port · decision_id도 지움(결정 0033) | 황승주 | 완료 |
| RT-10 | rotate_patrols | states, specs, Operation, roles, assignments, t_ms | (states, assignments) | 출발·만남·인계·대기 없음·하한선·기록 없는 쌍 테스트 | 황승주 | 완료 |
| RT-11 | fleet_choices | report, states, op, roles | report | auto_choices 카드의 선택지를 그때 함대 상황으로 만든다. 카드에 정해진 선택지가 있으면 그것을 맨 앞에 두고 "발생 지역 순찰"·"함께 감시"를 덧붙이며 "유지"는 정해진 선택지가 없을 때만 붙인다. 자기 카드가 열린 드론은 후보에서 뺀다(결정 0046). 함께 감시는 카드를 올린 드론과만(결정 0048) | 황승주 | 완료 |
| RT-12 | relieve_hover |  |  |  | 황승주 | 완료 |
| RT-13 | route_command | Action, Domain, 기체 위치, params | (CommandKind/None, params) | 상대 경로가 기체 위치 기준 좌표, move_to+route는 follow_route loop false, 그 밖은 expand_action 그대로 | kth9245 | 완료 |
| RT-14 | relief_due | VehicleState, VehicleSpec, 교대 기체 비행 분 | bool | 기준 배터리(귀환량 2배 빼고 35%) 또는 교대 비행 중 순찰기 소모+7% ≥ 하한선 위 여유면 참. 멀리서 오는 교대도 하한선 전에 인계(사용자 10/10) | 황승주 | 완료 |
