---
id: 0064
title: 탭 이름 상황판을 시뮬레이션으로, 헤더 MAVLink 버튼이 새 창에 GET /mavlink 명령 로그(통과한 명령만)
status: 확정
decided_by: kth9245
date: 2026-10-10
modules: [cop-ui, gateway, contracts, mavlink]
supersedes: null
---
## 결정
2026-10-10 23시, 사람이 말한 것을 그대로 적는다.

사람: "상황판 이름을 시뮬레이션으로 바꾸고 오른쪽 상단 명령에서 mavlink 명령어 로그 보게 할 수 있나"
AI가 로그를 여는 자리를 물음 → 사람: "옆에 'MAVLink' 버튼 새로", 메모 "버튼 누르면 새창 열리면서 mavlink 명령어 뜨게"
AI가 설계를 보임 → 사람: "ㄱㄱ 근데 꼭 필요한것만 하고 싶은데 — 변환 결과만 표시, 실제 전송 안 함 이런건 빼고"

(AI 해석)
1. 위쪽 탭 글자 「상황판」을 「시뮬레이션」으로 바꾼다. 주소 `#live`는 그대로.
2. 헤더 오른쪽(운용자 조작 숫자 칸과 LIVE 표시 사이)에 `MAVLink` 버튼. 누르면 `window.open`으로 `#mavlink`를 새 창에 연다. 그 창은 탭 없이 로그 줄만 보이고 1초마다 `GET /mavlink`를 다시 읽는다. "변환만·전송 안 함" 같은 안내 문구는 넣지 않는다.
3. `GET /mavlink` → `string[]`: 이번 실행(reset 뒤)에 안전 검사를 통과한 명령(`EngineState.passed`)을 시간순으로 MAVLink 메시지 줄로 바꾼 것. 줄 형식은 `HH:MM:SS(KST) <기체> <메시지> <MAV_CMD 이름>(<번호>) p1 … p7`. NAV 명령(WAYPOINT·LOITER_UNLIM)은 `MISSION_ITEM_INT seq<n>` 줄들 뒤에 `COMMAND_LONG MAV_CMD_MISSION_START(300)`, RTL·DO_SET_MODE는 `COMMAND_LONG` 한 줄.
4. 명령 종류 → MAV_CMD 대응은 결정 0011의 `compile_mavlink` 표 하나만 쓴다. 표를 `modules/mavlink/mav_cmd.py`로 옮겨 `compile_mavlink`과 새 액션 MAV-02 `mavlink_lines(passed, specs) -> list[str]`이 함께 쓴다(`compile_mavlink` 동작은 그대로).
5. 꼭 필요한 것만: MAVLink 표준 명령이 없는 명령(타격)과 차단된 명령(기체로 나가지 않음)은 줄을 만들지 않는다. 출처(Role·운용자 결정) 꼬리표, 기체 system id, 줄 수 제한·필터는 넣지 않는다.

## 이유
- Frame에는 기체로 나간 명령이 없고, 엔진 상태에는 통과한 명령 기록이 이미 쌓인다(결정 0038). REST로 그 기록을 읽으면 틱 루프(`engine.py`)·`tick_log`·Frame 계약을 건드리지 않는다.
- 새 창은 전체 Frame이 필요 없어 WS 대신 1초 조회로 충분하다(로컬 시연).
- 대응표를 한 곳에 두어야 임무 파일과 로그가 같은 명령을 다르게 번역하지 않는다.

## 버린 대안
- 헤더 숫자 칸을 누르면 로그가 열림, 오른쪽 칸 아래 접기 칸: 사람이 새 버튼을 골랐다.
- Frame에 MAVLink 칸 추가 또는 `Frame.log`에 `[MAVLink]` 줄: 계약·남의 액션을 바꾸고 화면이 줄을 모으고 reset을 가려야 한다.
- 차단된 명령도 "전송 안 함" 줄로 보이기: 사람이 꼭 필요한 것만 원했다.

## 영향
- `modules/cop-ui/src/App.tsx`, `features/nav/tab.ts`, 새 `features/mavlink/`, `Screen.tsx` 헤더, `vite.config.ts` 프록시(+`viteProxy.test.ts`)
- `modules/gateway/app.py`(`GET /mavlink`), `contracts/API.md` 5절 표
- `modules/mavlink/`(새 `mav_cmd.py`, MAV-02, SPEC.md)
