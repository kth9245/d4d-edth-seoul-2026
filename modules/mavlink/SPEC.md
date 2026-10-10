<!-- prefix: MAV -->
# mavlink SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| MAV-01 | compile_mavlink | Role, Operation, specs | dict[vehicle_id, (plan_json, script_text)] | op.assign의 기체마다 그 Role로 QGC .plan(mission.items[].command가 MAV_CMD 정수) 생성, 스크립트가 py_compile 통과. do→MAV_CMD 대응은 결정 0011. role은 공개 API(expand_action)로만 | 황승주 | 완료 |
| MAV-02 | mavlink_lines | list[PassedCommand], specs | list[str] | 통과한 명령마다 `HH:MM:SS(KST) 기체 메시지 MAV_CMD이름(번호) p1…p7` 줄. NAV(WAYPOINT·LOITER_UNLIM)는 MISSION_ITEM_INT seq줄들 + COMMAND_LONG MISSION_START(300), RTL·DO_SET_MODE는 COMMAND_LONG 한 줄, 대응표가 없는 명령(strike)은 줄 없음. 대응표는 mav_cmd.py(compile_mavlink과 같은 표, 결정 0011·0064) | kth9245 | 완료 |
