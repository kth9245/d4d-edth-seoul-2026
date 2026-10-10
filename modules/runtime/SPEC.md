<!-- prefix: RT -->
# runtime SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| RT-01 | step_vehicle | VehicleState, VehicleSpec, Play(기체의 현재 플레이), targets, t_ms | (state, Command/None, Report/None) | 결정 대기·ready/active 아님이면 그대로, 안 들어간 step이면 enter_step(RT-08), 들어갔으면 on 첫 참으로 전이, 직접 조종 도착이면 resume step으로. 원본: 스파이크 port | 황승주 | 완료 |
| RT-02 | apply_reserves | states, Operation, plays, assignments, t_ms | (states, assignments, Report/None) | 이탈(returning·lost·maintenance) 기체의 op.reserve 첫 ready·active 기체가 그 기체의 플레이를 entry step부터 entered_step=False로 시작(결정 0022), Assignment "예비 투입: <id> 대신", vehicle_gap Report(결정 0016) | 황승주 | 완료 |
| RT-03 | apply_decision | states, plays, Decision, reports | (states, reports) | 선택지 play_by_vehicle대로 기체들을 새 플레이 entry로(entered_step=False), 보고한 기체 pending_report_id 지움, resolved_ms·decision_id 기록. target_select면 target_id = choice_id. 기체 4대 동시 전환 테스트 | 황승주 | 완료 |
| RT-04 | update_metrics | Metrics, TickOutcome(contracts) | Metrics | 09 2.3 정의 5개 각 1테스트(role_gap → vehicle_gap_ms). 공백 끝 규칙은 contracts/API.md 2절 | 황승주 | 완료 |
| RT-05 | apply_injection | states, plays, Injection(approved) | states | play_by_vehicle대로 새 플레이 entry로 전환. 원래 플레이는 끝, 자동 복귀 없음(결정 0016) | 황승주 | 완료 |
| RT-06 | apply_direct | states, DirectControl, t_ms | (states, Command) | operator_direct 명령 생성, 도착 시 resume 복귀 | 황승주 | 완료 |
| RT-07 | apply_emergency | states, plays | states | 기체의 현재 플레이 emergency 규칙(battery_low_pct 등)에 걸리면 그 플레이의 지정 step으로 | 황승주 | 완료 |
| RT-08 | enter_step | VehicleState, VehicleSpec, Play, Step, targets, t_ms | (state, Command/None, Report/None) | nearest·operator·고정 표적 각 1테스트, move_to의 target 좌표는 그대로, 귀환 step이면 returning. 원본: 스파이크 port/modules/runtime/actions/enter_step.py | 황승주 | 완료 |
| RT-09 | switch_play | VehicleState, Play | VehicleState | play_id·step_id=entry·entered_step False·target·pending·resume 비움 1테스트. 원본: 스파이크 port | 황승주 | 완료 |
