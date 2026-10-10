<!-- prefix: SFT -->
# safety SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| SFT-01 | point_in_polygon | GeoPoint, Polygon | bool | 안·밖·경계 테스트 | 황승주 | 완료 |
| SFT-02 | return_feasible | VehicleState, VehicleSpec, 목적지 GeoPoint | (bool, 대안 GeoPoint/None) | 왕복 시간 > 가용 80%면 False와 최대 거리 지점(선분 200등분, 09 6절) | 황승주 | 완료 |
| SFT-03 | check_command | Command, VehicleState, VehicleSpec, Operation, plays, injections | PassedCommand / Block | 규칙 1→2→3, 규칙마다 통과·차단·대안 테스트. PassedCommand 생성은 여기뿐(grep 테스트) · 결정 0033: strike는 출처 decision_id 없으면 no_provenance | 황승주 | 완료 |
