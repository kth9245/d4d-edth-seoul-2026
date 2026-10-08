<!-- prefix: RT -->
# runtime SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| RT-01 | step_vehicle | VehicleState, VehicleSpec, Play, targets, t_ms | (state, Command/None, Report/None) | step 진입 때 명령·카드 한 번, on 첫 참으로 전이, pending_report_id면 정지. 명령 kind는 play.expand_action(step.do, spec.domain) | 황승주 | 예정 |
| RT-02 | assign_roles | Play, states, assignments, t_ms | (states, assignments, Report/None) | Role.vehicles 순서의 첫 ready·active 기체. 이탈 시 다음 예비가 role_id·play_id·step_id 이어받고 entered_step=False, 없으면 role_gap Report | 황승주 | 예정 |
| RT-03 | apply_decision | states, Play, Decision, reports | (states, reports) | pending_report_id 지우고 step_by_role대로 전이, resolved_ms·decision_id 기록. 역할 4개 동시 전이 테스트 | 황승주 | 예정 |
| RT-04 | update_metrics | Metrics, TickOutcome(cmds, passed, blocks, new_reports, assignments, inputs, states, targets, plays) | Metrics | 09 2.3 정의 5개 각 1테스트. role_gap 끝 규칙은 09 6절 Part2-13 | 황승주 | 예정 |
| RT-05 | apply_injection | states, Injection(approved), plays | states | proposed대로 배정, resume (play, step) 보관 | 황승주 | 예정 |
| RT-06 | apply_direct | states, DirectControl, t_ms | (states, Command) | operator_direct 명령 생성, 도착 시 resume 복귀 | 황승주 | 예정 |
| RT-07 | apply_emergency | states, Play.emergency | states | battery_below면 지정 step으로, 끝나면 resume | 황승주 | 예정 |
