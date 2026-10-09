---
id: 0011
title: 워크플로우(플레이)는 MAVLink 기체를 움직일 수 있는 프로그램으로 변환 가능해야 한다 (QGC .plan + pymavlink 실행 스크립트 생성)
status: 확정
decided_by: kth9245
date: 2026-10-09
modules: [play, runtime, contracts, demo]
supersedes: null
---
## 결정
2026-10-09 사람이 말한 것을 그대로 적는다. AI가 "펼치기(expand_action)는 내부 명령 8개로만 바꾸고 실제 프로토콜로는 변환하지 않는다"고 설명한 뒤의 대화.

사람: "그 각 육해공에서 자주쓰는 언어나 프로토콜을 타겟으로 해야 설득력 있을거같은데 각각 뭘로 변환됨"
사람: "아 ㅇㅇ mavlink로 움직이게끔 실제 보여주는게 아니라 실제로 워크플로우가 충분히 mavlink 작동시킬 수 있는 프로그램으로 변환 가능하다 가 되어야함"

(AI 해석)
1. 증명할 명제는 "플레이(워크플로우)가 MAVLink 기체를 작동시킬 수 있는 프로그램으로 변환된다"이다. 시연에서 기체가 MAVLink로 실제로 움직이는 것을 보여 주는 것이 아니다(정책 1·결정 0006: 시뮬레이션만).
2. 변환 대상은 영역별로 다른 세 프로토콜이 아니라 **MAVLink 하나**다. ArduPilot이 공중(Copter/Plane)·지상(Rover)·해상(Rover boat 프레임)을 같은 MAVLink 임무 명령으로 받기 때문이다(docs/research/06 "기체 쪽은 MAVLink"). STANAG 4586·JAUS·IMC는 어댑터를 붙일 자리로만 언급한다.
3. 변환 결과물은 기체마다 둘이다.
   - **임무 파일**: step의 `do`를 MAVLink 명령으로 바꾼 QGroundControl `.plan`(JSON, mission items). move→`MAV_CMD_NAV_WAYPOINT`, patrol_route/search_area→WAYPOINT 열, watch_target/watch_point(air)→`MAV_CMD_NAV_LOITER_UNLIM`/`LOITER_TURNS`, hold→LOITER_UNLIM(공중·해상)/HOLD(지상), return_home→`MAV_CMD_NAV_RETURN_TO_LAUNCH`, approach_target→FOLLOW 모드. 펼치기 표의 None 칸(지상 선회 없음 등)은 ArduPilot Rover에 그 명령이 없는 것과 같다.
   - **실행 스크립트**: 탈출 조건·보고·승인은 MAVLink 임무 파일로 표현되지 않으므로, step 그래프를 pymavlink 스크립트로 낸다. 스크립트는 step별 미션을 올리고(`MISSION_COUNT`/`MISSION_ITEM_INT`), 텔레메트리(`MISSION_ITEM_REACHED`=arrived, `SYS_STATUS.battery_remaining`=battery_below)와 관제 신호(target_found, Decision)를 보고 다음 step의 미션으로 바꾼다. 즉 runtime `step_vehicle`과 같은 전이 규칙을 기체 쪽 프로그램으로 옮긴 것이다.
4. 완료 기준: 템플릿 플레이 2개에서 기체 5대의 `.plan`이 QGC 스키마(fileType "Plan", mission.items[].command 정수 등)로 생성되고, 생성된 스크립트가 `python -m py_compile`을 통과한다. ArduPilot SITL에서 실제로 돌리는 것은 동결 뒤 시간이 남을 때의 추가 단계이며, 되면 BUILT_HERE에 적는다.
5. 액션: play `compile_mavlink(play, op, specs) -> dict[vehicle_id, (plan_json, script_text)]` 하나(80줄을 넘으면 `.plan` 생성과 스크립트 생성으로 둘). 09 6절 번호 Part3-15, 통합 2 뒤(동결 전). 담당은 통합 1을 먼저 끝내는 사람(예상: 최동호)이 `예정` 행을 가져간다. 상황판에는 통과한 명령 옆에 MAVLink 명령 이름을 한 줄로 보여 준다(Frame.log).

## 이유
- 사람의 요구: 내부 명령 8개는 지어낸 이름이라 심사에서 "실제 기체엔 뭐가 나가나"에 답이 없다. 변환 가능성을 실제 산출물로 보여야 설득된다.
- MAVLink 하나로 세 영역을 덮는 것이 가장 싸고, 06 문서의 "ArduPilot SITL로 공중·지상·해상" 주장과 맞는다.
- 임무 파일만으로는 조건·승인이 안 되므로 스크립트가 있어야 "충분히 작동시킬 수 있는 프로그램"이 된다.

## 버린 대안
- 영역별 세 프로토콜(MAVLink/JAUS/IMC) 변환: 24시간 안에 셋을 만들 수 없고, 해상 표준은 통일돼 있지 않다.
- SITL을 붙여 실제로 움직이는 시연: 정책 1(오프라인)·결정 0006(시뮬레이션만)·시간. 변환 결과물이 있으면 SITL은 다음 단계로 말할 수 있다.
- MAVLink 명령 이름만 로그에 찍기: 변환 "가능"의 증거가 되지 않는다. 사람이 "실제로 변환 가능하다"를 요구했다.

## 영향
- modules/play/SPEC.md에 `compile_mavlink` 예정 행(Part3-15). docs/research/09 6절 Part 3 표에 행 추가, 3.2 공개 API에 `compile_mavlink`.
- 의존성 `pymavlink`는 생성된 스크립트가 쓰는 것이지 이 저장소가 import하지 않는다(시연 경로에 외부 라이브러리 추가 없음). 스키마 검증은 QGC `.plan` 필드를 손으로 검사한다.
- 발표 문장: "플레이는 저장 전 검사를 통과한 뒤 기체마다 MAVLink 임무 파일과 실행 스크립트로 변환됩니다. 시연은 같은 규칙을 시뮬레이터에서 돌린 것이고, 변환 결과는 ArduPilot 계열 기체에 그대로 올릴 수 있는 형식입니다."
