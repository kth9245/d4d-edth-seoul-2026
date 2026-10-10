<!-- prefix: SIM -->
# sim SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| SIM-01 | load_scenario | path | Scenario | 잘못된 값은 로딩 시 ValueError로 위치와 이유 표시 | 리드 | 완료 |
| SIM-02 | object_positions | Scenario, t_ms | list[TruthPoint] | 등속 이동, appear_s 이전 객체 제외 | 리드 | 완료 |
| SIM-03 | emit_detections | list[TruthPoint], t_ms, seed | list[Detection] | 레이더 탐지 1개/객체, 위치 잡음 σ≈3m, 재현 가능 | 리드 | 완료 |
| SIM-04 | load_scenario_json | path | Scenario | JSON을 Scenario.model_validate, 잘못된 값은 ValueError에 위치. operation.started_ms가 비거나 assign이 없는 Role을 가리키면 ValueError(결정 0018). 레거시 load_scenario는 그대로 · ontology가 있으면 fill_vehicle_kinds로 capabilities·kind_path(결정 0038) | 최동호 | 완료 |
| SIM-05 | move_straight | VehicleState, VehicleSpec, PassedCommand(move·return_home·hold), dt_ms | VehicleState | 1틱에 speed×dt 이동, 도착 시 waypoint_idx=-1, return_home 도착 시 maintenance, 배터리 선형 감소 · 해상(land 인자)은 섬을 돌아가 도착(결정 0034) | 최동호 | 완료 |
| SIM-06 | follow_route | VehicleState, VehicleSpec, PassedCommand(follow_route), dt_ms | VehicleState | 경로점 순회, 끝나면 처음으로(params.loop false면 끝점에서 멈추고 waypoint_idx -1 = 도착, 결정 0045) · 해상(land 인자)은 섬을 돌아가 경로점 도착(결정 0034) | 최동호 | 완료 |
| SIM-07 | orbit_or_keep | VehicleState, VehicleSpec, PassedCommand(orbit·keep_distance), Target, dt_ms | VehicleState | orbit 반지름 유지, keep_distance 거리 유지. 밀리면 hold로 대체 · 해상(land 인자)은 표적까지 직선이 막히면 섬을 돌아감(결정 0034) | 최동호 | 완료 |
| SIM-08 | advance_vehicles | states, specs, passed: list[PassedCommand], dt_ms, targets, land | states | 이번 틱 PassedCommand로 active 갱신, 없으면 active 계속 수행. 명령 없는 틱 테스트 · strike도 orbit_or_keep(결정 0033) · land는 해상 기체에만(공중·지상은 직선, 결정 0034) | 최동호 | 완료 |
| SIM-09 | apply_events | Scenario, states, targets, t_ms, dt_ms | (states, targets) | 사건 시각 = operation.started_ms + offset_ms(결정 0018). spawn_target·vehicle_battery_set·target_move·split_target·vehicle_link_lost 각 1테스트. params 키는 09 2.2 | 최동호 | 완료 |
| SIM-10 | resolve_strikes | states, targets, t_ms | (targets, list[Report]) | 100 m 안·밖, 이미 무력화면 카드 없음, 같은 틱 두 기체면 카드 하나(결정 0033) | kth9245 | 완료 |
| SIM-11 | spawn_enemies | scenario, targets, t_ms, dt_ms | targets | 등장 틱에만 하나, from_enemy 위치, role_id·step_id·step_since_ms · 적의 heat·noise도 표적에 복사(결정 0071) · 모선(from_enemy)이 무력화됐으면 나타나지 않음(사용자 10/11) | kth9245 | 완료 |
| SIM-12 | steer_enemies | enemies, roles, targets, t_ms, dt_ms, land | targets | 목적지 방향 속도, 도착 틱에 위치 맞춤·속도 0·waypoint -1, time_elapsed 전이, 무력화면 그대로 · 배는 land를 돌아가 도착(결정 0034) | kth9245 | 완료 |
| SIM-13 | sea_aim | pos, goal, land | GeoPoint | 열린 직선이면 goal, 막히면 가까운 쪽 모서리, 모서리 위면 다음 모서리, 목표가 육지면 해안 50 m 바다 점, 육지 위 출발·land 없음이면 goal | kth9245 | 완료 |
| SIM-14 | update_emission | scenario, targets, t_ms | targets | appear_offset_ms + emit_start_offset_ms 시각부터 emitting=True, None이면 무음, 한 번 켜지면 계속 (결정 0039) | 최동호 | 완료 |
