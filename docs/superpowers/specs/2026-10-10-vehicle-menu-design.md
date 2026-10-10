# 상황판 기체 메뉴 설계 (Part1-32.1, 결정 0058·0059·0060·0061)

## 목적
상황판에서 기체를 눌러도 선택만 되고 메뉴가 없었다. 표적 없는 Role 전환은 오른쪽 아래 접힌 '작전 전환' 칸에서 기체·Role을 고르고 승인 카드를 한 번 더 눌러야 했고, 타격은 타격 허락 카드로만 됐다(결정 0048). 사람: "기체 클릭하면 role을 바꾸거나 그 타격 이동 같은걸 바로 선택할 수 있게". 기체를 누르면 그 자리에서 이동·Role 전환·표적 지목(무장 기체는 타격까지)을 고르고, 누른 것이 곧 승인이 되게 한다.

## 범위
- 한다: 왼쪽 아군 목록에서 고른 기체 줄 아래로 메뉴를 펼침(지도에서 눌러도 같은 줄), 표적 없는 Role 바로 전환, 표적 Role(무장 기체는 '표적 타격')을 누르면 지금 포착된 적 목록에서 골라 바로 적용, 지도 지목 메뉴에도 '표적 타격', 지목 전환이 기체의 결정 id가 됨(runtime), '작전 전환' 칸 삭제와 '전 기체 귀환'을 아군 머리줄로, 고속 보트 추적·전 기체 순찰 버튼 데이터 삭제와 시연 추적 장면을 지목으로.
- 하지 않음: 연결 그래프(`GET /graph`)에 지목 기록(inj-n) 노드 추가, `track_fast` Role 안 타격 허락 카드 선택지가 d2·usv를 직접 적는 문제(d1을 고속 보트 추적에 지목해도 카드의 '이 기체로 타격'은 d2를 옮김. 시연은 d2·usv만 이 Role을 쓰고, 다른 기체는 메뉴의 '표적 타격'으로 직접 타격), 예시 장면 s4(`s4_switch_pending`)의 고속 보트 추적 전환 id(손으로 만든 예시라 대기 전환 카드 표시용으로 그대로 둠), 포착 목록에 놓친 적·전파(RF)만 잡힌 적 넣기(위치를 모르는 적을 치면 시뮬레이터의 실제 위치로 가게 됨), 타격 Role 이름 변경(데이터 이름 '표적 타격' 그대로, 사람이 말한 '지정 타격'은 이 Role), 표적 없는 Role 전환을 이미 카드를 기다리는 기체에 했을 때 그 카드 처리.

## 동작
1. **기체 고르기.** 지도 기체 마커 또는 왼쪽 아군 줄을 누르면 그 기체가 선택되고(지금 `useDirectControl.selected`), 왼쪽 목록의 그 기체 줄 아래가 펼쳐진다. 같은 기체를 다시 누르거나 Esc면 닫힌다. 다른 기체를 누르면 그 줄로 옮겨 간다.
2. **펼친 줄 내용.**
   - 이동: "지도를 누르면 그 지점으로 이동" 한 줄. 지도를 누르면 지금처럼 `POST /direct` 뒤 선택이 풀린다.
   - Role 바꾸기: 표적 없는 Role 버튼. 버튼 글은 Role 이름, 아래 작은 글씨 "지금 Role → 새 Role". 누르면 `POST /injections {role_by_vehicle: {기체: Role}, approve: true}`(결정 0059), 승인 카드 없이 다음 틱에 적용, 운용자 조작 1회. 보낸 뒤 선택이 풀리고 안내 줄에 "전환 inj-n · d2 → 귀환"(실패면 "보내기 실패: …").
   - 표적 Role: 표적이 필요한 Role도 버튼으로 나온다(감시·추적, 무장 기체면 `strike` Role '표적 타격'은 빨간 글씨, 결정 0058). 누르면 그 버튼 아래에 **지금 포착된 적** 목록이 펼쳐진다(사람: "role 중에 지정 타격이 있는거고 이걸 실행하면 현재 포착된 기체를 찾을 수 있는거지"). 목록은 상황판 표적 상태(`trackState`, 결정 0047)가 `seen`(우리 기체 센서에 지금 보임)인 적만, 위험도 높은 순, 줄마다 표적 id·종류·위험도·이 기체에서 거리. 적을 누르면 `postPoint`(approve: true)로 그 Role + 그 표적, 바로 적용. 다른 표적 Role 버튼을 누르면 목록이 그 아래로 옮겨 가고, 같은 버튼을 다시 누르면 접힌다. 포착된 적이 없으면 "지금 포착된 적이 없습니다" 한 줄.
3. **지도에서 지목(지금 기능 유지).** 기체를 고른 채 지도 표적 또는 왼쪽 적 줄을 누르면 지금의 지목 메뉴(`PointMenu`)가 뜬다. 목록은 아래 '표적 Role'(무장 기체면 '표적 타격' 포함)이고 누르면 같은 `postPoint`. 메뉴 아래 안내는 "누르면 바로 바뀝니다"만(타격 금지 문구 삭제). 기체 메뉴의 목록과 같은 요청이라 둘 중 아무 길로 해도 된다.
4. **메뉴에 넣는 Role** (`vehicleMenuRoles`): 다음을 모두 만족하는 Role.
   - 적이 쓰는 Role이 아님(`GET /enemies`의 `role_id`).
   - 기체 영역(`VehicleSpec.domain`)이 `Role.domains`에 있음.
   - 기체 `capabilities`가 있으면 Role의 모든 step 행동(`do.kind`)이 그 안에 있음(정찰 드론 d1·d3·d4에는 '표적 타격'이 없음). `capabilities`가 비면(온톨로지 없는 작전) 이 조건은 건너뜀.
   - 나눔: 첫 step(`entry`)의 행동이 `watch_target`·`approach_target`·`strike_target`이고 `params.target`이 `"operator"`이면 표적 Role(runtime `spot_reports`와 같은 기준에 타격 추가), 아니면 표적 없는 Role.
   - 표적 없는 Role에서는 지금 하는 Role을 뺀다. 표적 Role은 지금 Role도 남긴다(같은 추적을 다른 표적으로 돌리기).
5. **지목 타격의 출처(runtime, 결정 0058).** `apply_injection`이 `target_by_vehicle`에 있는 기체에 Role·표적과 함께 `decision_id = injection.id`를 적는다. 그 기체의 `strike` 명령은 출처 `decision_id = inj-n`을 싣고 안전 규칙 1을 통과한다. 표적 없이 옮긴 기체(전 기체 버튼, 표적 없는 메뉴 전환, 예비 이어받기)는 지금처럼 `decision_id`가 없어 타격이 막힌다. `check_command`는 바꾸지 않는다. 타격 결과 카드 근거 줄은 "운용자 결정 inj-n → d2 타격 · 출처·구역·배터리 검사 통과"가 된다(지금 코드 그대로).
6. **전 기체 버튼.** 왼쪽 '아군 n' 머리줄 오른쪽에 `Operation.switches` 버튼(두 작전 모두 '전 기체 귀환' 하나). 누르면 지금처럼 `POST /injections {switch_id}` → 오른쪽 결정 대기에 승인 카드. 보낸 결과는 머리줄 아래 한 줄("요청됨 inj-n · 결정 대기에서 승인" 또는 실패).
7. **오른쪽 열.** '작전 전환' 접힘 칸을 지우고 '지난 기록' 접힘만 남는다.
8. **데이터와 시연 대본(결정 0060·0061).** 두 작전 `operation.switches`에서 `track_fast`·`patrol_all`을 지운다(24시간은 `scripts/make_coast_routes.py`에서 지우고 재생성). 그래서 새 적 발견 카드(결정 0057)의 맨 앞 '표적용 전환' 선택지가 비고, fast1 카드에는 기지 대기 드론 감시 또는 '전 기체 현 임무 유지'만 남는다. 시연의 고속정 추적은 fast1 카드가 뜬 뒤 기체 메뉴에서 두 번: d2 → '고속 보트 추적' → 포착 목록의 fast1, usv → '고속 보트 추적(해상)' → fast1(지도에서 fast1을 눌러 지목해도 같은 요청). 그 뒤 타격 허락 카드·'함께 타격'·무력화는 그대로.

## 파일
| 층 | 파일 | 변경 | 담당 |
|---|---|---|---|
| runtime | `modules/runtime/actions/apply_injection.py`(RT-05), `tests/test_apply_injection.py` | `target_by_vehicle` 기체에 `decision_id = injection.id` | 이 작업(황승주 영역, 알림) |
| contracts | `contracts/API.md` 1절 타격 문단·4절 표 | 지목 전환의 결정 id, '기체 메뉴 Role 전환'(일부 전환 + approve) 행, 지목 타격 | 이 작업 |
| cop-ui | `features/board/vehicleMenuRoles.ts`(새 액션) | 위 4항. `{plain, target}`, 각 `{id, name, strike}` | 이 작업 |
| cop-ui | `features/board/seenTargets.ts`(새 액션) | Frame 표적, Track 묶음, 기체 위치 → `seen`인 적 `{id, kind, threat, distM}[]` 위험도 순 | 이 작업 |
| cop-ui | `features/board/postRole.ts`(새 액션) | `POST /injections {role_by_vehicle, approve: true}`, throw 없음 | 이 작업 |
| cop-ui | `features/board/fetchBoardData.ts`(UI-89) | `GET /enemies`·`GET /operation`도 읽어 `{…, enemyRoles: string[], switches: Switch[]}`, 실패는 빈 목록 | 이 작업 |
| cop-ui | `features/board/VehicleMenu.tsx`(새), `RosterPanel.tsx`(UI-94) | 고른 줄 아래 펼침(이동 안내, 표적 없는 Role 버튼, 표적 Role 버튼과 그 아래 포착 목록), 머리줄 전 기체 버튼과 결과 줄 | 이 작업 |
| cop-ui | `features/board/PointMenu.tsx`, `features/map/useDirectControl.ts`(UI-96·UI-36) | 지목 목록을 `vehicleMenuRoles().target`으로, 타격 빨간 글씨, 안내 문구, `onRole`·결과 줄, `onPointFromMenu(role, target)`(지도 지목 없이 메뉴 목록에서), 안내 줄 "d2 선택 · 왼쪽 메뉴에서 Role · 지도를 누르면 이동 · Esc 취소" | 이 작업 |
| cop-ui | `Screen.tsx`, `board.css` | SwitchPanel 접힘 삭제, RosterPanel에 메뉴·버튼 연결, 펼친 줄 모양 | 이 작업 |
| cop-ui | 삭제: `features/cards/SwitchPanel.tsx`(UI-34), `features/cards/switchRoleOptions.ts`+테스트(UI-65), `features/board/targetRoles.ts`+테스트(UI-86) | SPEC 행은 `폐기(Part1-32.1, …)` | 이 작업 |
| scripts | `scripts/qa/live.json` L7, `scripts/qa/draft_to_live.json` I4~I6, L15 지목 메뉴 문구 | '전환 요청' 고르기 → 기체 줄 메뉴 버튼(승인 카드 없음, 조작 1회), 지목 메뉴 타격 확인 | 이 작업 |
| demo | `demo/scenarios/baengnyeong_night.json`, `scripts/make_coast_routes.py` → `baengnyeong_24h.json` | switches에서 `track_fast`·`patrol_all` 삭제 | track 세션 제안(답 대기, 안 맡으면 이 작업) |
| tests | `modules/gateway/tests/test_demo_timeline.py`, `tests/test_demo_scenario.py`, spot_reports 테스트 | fast1 카드 처리 + 지목 두 번, `test_track_fast_switch_sends_d2_and_usv`·`test_patrol_all_switch_rotates_the_three_drones`를 같은 배정 직접 넣기로 | track 세션 제안 |
| scripts | `scripts/qa/script.json` P6, `contracts/examples/operation.json` 등(`gen_examples.py` 재생성) | P6 카드 선택지 → 지목 두 번 | track 세션 제안 |

## 순서
1. runtime `apply_injection` 결정 id(테스트 먼저) → ship. 이게 먼저 있어야 화면에서 지목 타격을 눌렀을 때 출처 검사에 막히지 않는다.
2. `contracts/API.md` → ship.
3. cop-ui 액션 `vehicleMenuRoles`·`postRole`·`fetchBoardData`(테스트 먼저) → 화면 연결(VehicleMenu·RosterPanel·PointMenu·useDirectControl·Screen) → 지울 파일 삭제 → ship.
4. 화면 점검 목록(live·draft_to_live) 고치고 실제 화면 확인 → ship.
5. 데이터·대본(track 세션 답에 따라).

## 테스트
- runtime `apply_injection`: `target_by_vehicle`에 있는 기체는 `decision_id == injection.id`·`target_id == 표적`, 표적 없이 옮긴 기체는 `decision_id is None`. 지목으로 `strike` Role에 든 기체가 `step_vehicle`을 거쳐 낸 `strike` 명령의 `provenance.decision_id == inj-n`이고 `check_command`가 통과(출처 규칙만 본다, 구역·배터리는 시나리오 위치로).
- cop-ui `vehicleMenuRoles`: 야간 시나리오 Role로 d2(무장 드론)는 표적 Role에 감시·고속 보트 추적·표적 타격, d1(정찰 드론)은 타격 없음, usv는 해상 Role만, 적 Role(`enemy_*`) 없음, 표적 없는 Role에 지금 Role 없음, `capabilities` 없는 기체는 능력 조건 건너뜀.
- cop-ui `seenTargets`: 손으로 만든 표적·표적 상태로 보이는 적만(놓침·RF만·미탐·무력화 제외), 위험도 순, 기체에서 거리(m, 정수).
- cop-ui `postRole`: 경로·본문(`approve: true`, `target_by_vehicle` 없음), 실패 시 `{ok: false}`.
- cop-ui `fetchBoardData`: 적 Role id와 switches, 하나가 실패해도 나머지.
- 화면(dev 서버, 야간 작전): d2 줄 누름 → 펼친 줄에 이동 안내·'귀환' 등 버튼·표적 Role 버튼 '표적 감시'·'고속 보트 추적'·'표적 타격'(빨강) → '귀환' 누름 → 승인 카드 없이 d2가 귀환, 운용자 조작 +1. d2 다시 고름 → 펼친 줄의 '표적 타격'(빨강) 누름 → 그 아래 포착 목록에 fast1(보일 때) → 누름 → d2가 fast1로 가 무력화, 결과 카드 근거 줄 "운용자 결정 inj-n". d1 고름 → 펼친 줄에 '표적 타격' 없음, 지도에서 fast1을 눌러도 지목 메뉴에 타격 없음. 오른쪽 열에 '작전 전환' 없음, 아군 머리줄 '전 기체 귀환' → 승인 카드. 스크린샷은 CDP로 실제 대기 뒤 촬영(가상 시간 스크린샷은 지도 구역 레이어를 놓침).
- 시연 대본 테스트·`scripts/qa/script.json`은 5단계(track 세션) 뒤 끝까지 통과.
