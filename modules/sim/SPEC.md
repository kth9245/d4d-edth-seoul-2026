<!-- prefix: SIM -->
# sim SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| SIM-01 | load_scenario | path | Scenario | 잘못된 값은 로딩 시 ValueError로 위치와 이유 표시 | 리드 | 완료 |
| SIM-02 | object_positions | Scenario, t_ms | list[TruthPoint] | 등속 이동, appear_s 이전 객체 제외 | 리드 | 완료 |
| SIM-03 | emit_detections | list[TruthPoint], t_ms, seed | list[Detection] | 레이더 탐지 1개/객체, 위치 잡음 σ≈3m, 재현 가능 | 리드 | 완료 |
| SIM-04 | load_scenario_json | path | Scenario | JSON을 Scenario.model_validate, 잘못된 값은 ValueError에 위치. operation.started_ms가 비거나 assign이 없는 플레이를 가리키면 ValueError(결정 0018). 레거시 load_scenario는 그대로 | 최동호 | 완료 |
| SIM-05 | move_straight | VehicleState, VehicleSpec, PassedCommand(move·return_home·hold), dt_ms | VehicleState | 1틱에 speed×dt 이동, 도착 시 waypoint_idx=-1, return_home 도착 시 maintenance, 배터리 선형 감소 | 최동호 | 완료 |
| SIM-06 | follow_route | VehicleState, VehicleSpec, PassedCommand(follow_route), dt_ms | VehicleState | 경로점 순회, 끝나면 처음으로 | 최동호 | 완료 |
| SIM-07 | orbit_or_keep | VehicleState, VehicleSpec, PassedCommand(orbit·keep_distance), Target, dt_ms | VehicleState | orbit 반지름 유지, keep_distance 거리 유지. 밀리면 hold로 대체 | 최동호 | 완료 |
| SIM-08 | advance_vehicles | states, specs, passed: list[PassedCommand], dt_ms, targets | states | 이번 틱 PassedCommand로 active 갱신, 없으면 active 계속 수행. 명령 없는 틱 테스트 | 최동호 | 완료 |
| SIM-09 | apply_events | Scenario, states, targets, t_ms, dt_ms | (states, targets) | 사건 시각 = operation.started_ms + offset_ms(결정 0018). spawn_target·vehicle_battery_set·target_move·split_target·vehicle_link_lost 각 1테스트. params 키는 09 2.2 | 최동호 | 완료 |
