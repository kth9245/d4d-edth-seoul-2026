<!-- prefix: MAV -->
# mavlink SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| MAV-01 | compile_mavlink | Play, Operation, specs | dict[vehicle_id, (plan_json, script_text)] | op.assign의 기체마다 그 플레이로 QGC .plan(mission.items[].command가 MAV_CMD 정수) 생성, 스크립트가 py_compile 통과. do→MAV_CMD 대응은 결정 0011. play는 공개 API(expand_action)로만 | 황승주 | 완료 |
