<!-- 자동 생성 파일 (scripts/task.py). 직접 수정하지 마세요. -->

# 지금 작업판

마지막 기록 10/10 13:41 KST · 상세(입력·출력·완료 기준)는 docs/research/09 6절 · 기록은 `uv run python scripts/task.py`로만

## 진행중
- **Part1-19** 타격: 시나리오·플레이 JSON (fast1 동쪽 해안 우회, track_fast 수정·track_fast_sea·strike, 고속 보트 추적 전환 버튼) — 최동호, 10/10 12:21부터
- **Part2-19** 시나리오 튜닝 — 최동호, 10/10 12:02부터 · 하위 0/1 완료
- ⚠ 최동호 진행중 2개

## 막힘
- (없음)

## 예정

### kth9245
- **Part1-15** 3분 대본·BUILT_HERE·제출 설명

### 누구나
- **Part1-20** 타격: 화면 (무력화 표적 X·결과 카드·작전 성공·예시 장면 s7·s8)
- **Part1-21** 편집기 적 열 + GET /enemies (결정 0032, 읽기 전용)
- **Part2-19.1** 해상 기체는 육지를 지나지 않음: 섬 다각형(계약)·sim 우회·시나리오 바다 위치
- **Part3-12.2** 카드 편집: 지도에서 좌표 찍기(이동 지점·순찰 경로) — gio 세션

## 최근 결정
- 10/10 13:36 kth9245 · Part2-19.1 · 시나리오 좌표 수정(A: 수상정 대기 위치·적 배 경로·상륙 예상 지점)도 이 세션이 전부 한다. 최동호 Part1-19·Part2-19와 같은 파일(baengnyeong_night.json)이라 채팅으로 맞춘다. 리드 답 '이 세션이 A 전부'
- 10/10 13:36 kth9245 · Part3-14 · 보여 주기만: 편집기 작전 개요 위에 목적·시작 시각·작은 지도(작전 구역 + 기체 출발 위치)·기체 목록(종류·처음 플레이·예비 순서)·전환 버튼마다 기체→플레이. 편집 없음. 기체 정보는 GET /vehicles 추가. 리드 답 '보여 주기만 (추천)'
- 10/10 12:57 kth9245 · Part3-12.1 · 드롭다운 카드 편집을 전부 만든다: 오른쪽 편집 칸에서 이름, 행동 종류와 대상·거리(이동 지점·순찰 경로 좌표는 그대로), 연결 조건·값·다음 카드, 보고 문구·선택지·기체별 플레이, 카드 추가·삭제(첫 카드 제외). 리드 답 '일단 1번하고'(제안대로 전부). 통합 1에는 포함 안 됨(통합 2 항목)
- 10/10 12:41 kth9245 · Part1-21 · 빼는 후보로 두지 않고 유지(편집기 적 열 + GET /enemies). 리드 답 '이건 유지'
- 10/10 12:41 kth9245 · Part1-20 · 보류: 무력화 표시·작전 성공 표시는 성공 기준부터 정해야 해서 일단 하지 않음. 결과 카드(표적 무력화)는 Part1-18 이름표로 카드 열에 이미 뜸. 리드 답 '성공 기준까지 정해야되니깐 일단 ㄴㄴ'
- 10/10 12:41 kth9245 · Part2-19 · 완료 기준에 실제 baengnyeong_night.json으로 전환 승인→표적 선택→타격 승인 카드→함께 타격→fast1 무력화 엔진 테스트와 open_reports_max 타격 전·후 기록 추가(devil-advocate). 12:39 Part1-19 기록을 이쪽으로 옮김(11:57 결정: s7·s8은 Part2-19). 크게 오르면 수상정 표적 고정을 리드와 정함
- 10/10 12:39 kth9245 · Part1-15 · 타격 장면(약 20초)을 넣느라 줄일 장면은 3분 대본을 쓸 때 리허설로 재고 정한다. RUNBOOK.md의 옛 T1-3 문구(분류·위협도·대응 추천)도 이때 고친다. 리드 답 '대본 쓸 때 정함'
- 10/10 12:39 kth9245 · Part1-19 · 타격 화면에 '가상' 표시를 하지 않고 승인 카드 문구도 '타격 승인 요청' 그대로(devil-advocate 공격 3). 완료 기준에 실제 시나리오 끝까지(전환 승인→표적 선택→타격 승인→함께 타격→fast1 무력화) 테스트와 open_reports_max 타격 전후 기록 추가. 리드 답 '걍 이런건 필요 ㄴㄴ'
- 10/10 12:21 최동호 · Part1-19 · Part1-19는 최동호가 맡는다(누구나 항목, 리드 허락). 구조(enemies·적 플레이·track_fast·track_fast_sea·strike·전환 버튼)와 숫자 맞추기(Part2-19)를 한 사람이 같이 한다.
- 10/10 12:09 kth9245 · Part3-13.1 · 편집기 목록 위에는 '새로 만들기' 버튼만 두고, 누르면 'AI로 생성'(문장 입력·예시 문장·초안 만들기)과 '직접 생성'(이름·영역 → 시작 카드 하나짜리 새 플레이, 아직 저장 안 됨) 중 고른다. 리드 답 '새로 만들기 하고 ai로 생성, 직접 생성 이렇게 선택해서 추가되게 ㄲ'

## 완료
- **Part3-14** 작전 설정 패널 — kth9245, 10/10 13:41
- **Part1-14** smoke 전환 + 통합 주관 — kth9245, 10/10 13:18 · 하위 4/4 완료
- **Part3-12.1** 카드 편집 패널: 이름·행동(좌표 제외)·연결·보고·카드 추가/삭제 — kth9245, 10/10 13:08
- **Part1-14.4** 통합 2 전 스텁 제거: gateway stub_engine 대체 경로, 편집기 예시 데이터 — kth9245, 10/10 12:49
- **Part1-14.3** QA 수정: 직접 조종 십자를 서버 상태로(차단이면 없음, 대안이면 이동), 표적 이름표 위로 — kth9245, 10/10 12:43
- **Part1-14.2** 화면 QA 스크립트를 저장소에(scripts/qa.sh + 점검 목록) — kth9245, 10/10 12:36
- **Part1-14.1** 통합 1 확인: smoke 실제 엔진 전환 + 상황판·편집기 화면 QA — kth9245, 10/10 12:29
- **Part2-25** sim 적 진행(SIM-11, 결정 0032) + engine.py 호출 — kth9245, 10/10 12:15
- **Part2-24** 타격 engine.py: resolve_strikes 호출 + 타격 통과 기록 줄 — kth9245, 10/10 12:14
- **Part2-23** 타격 sim: advance 타격 분기·resolve_strikes 새 액션·update_metrics 작전 성공 — kth9245, 10/10 12:13
- **Part2-22** 타격 safety: 규칙 1에 타격 = 결정 id 필요 — kth9245, 10/10 12:12
- **Part2-21** 타격 runtime: enter_step·apply_decision·switch_play (결정 id·승인 표적·카드 닫기) — kth9245, 10/10 12:11
- **Part3-13.1** 새로 만들기 메뉴: AI로 생성 / 직접 생성 고르기 — kth9245, 10/10 12:11
- **Part1-18** 타격: 계약 추가 5개 + play 대응표 행 + TS·예시 (한 커밋) — kth9245, 10/10 12:10
- **Part3-10.1** 워크플로우 그래프 보기(step 카드 + 조건 연결선, React Flow) — kth9245, 10/10 12:09
- **Part3-13** 편집기: AI 초안 입력 칸 — kth9245, 10/10 11:59 · 하위 1/1 완료
- **Part3-12** 편집기: 카드 편집 — kth9245, 10/10 11:51 · 하위 1/2 완료
- **Part3-15** play `compile_mavlink` (결정 0011) — 황승주, 10/10 11:44 · 하위 1/1 완료 · PLY-10
- **Part3-15.1** mavlink compile_mavlink · MAV-01 (리드, 결정 0025, 통합 2 뒤) — 황승주, 10/10 11:44
- **Part1-11** 직접 조종 + 차단 카드 대안 버튼 — kth9245, 10/10 11:41
- **Part2-17** gateway `engine.py` 틱 루프 — 최동호, 10/10 11:38 · 하위 5/5 완료
- **Part2-18** gateway `build_frame` 재작성 — 최동호, 10/10 11:30
- **Part1-12** 주입 승인 카드 — kth9245, 10/10 11:28
- **Part2-17.1** gateway init_engine · GW-02 (묶음 A, engine_state.py 먼저) — 최동호, 10/10 11:23
- **Part3-9** play `draft_play` — 황승주, 10/10 11:22 · PLY-09
- **Part1-9.3** 디자인 v2: D4D 톤, Pretendard·Orbitron·JetBrains Mono 번들 — kth9245, 10/10 11:19
- **Part2-6** sensing `observe_targets`(공개 API 이름 `observe`) — 최동호, 10/10 11:16 · SNS-02
- **Part1-5** AI 초안 프롬프트·캐시 2개 — kth9245, 10/10 11:15 · 하위 1/1 완료
- **Part1-5.1** 프롬프트 틀 build_draft_prompt(PLY-12)·시연 문장 2개 — kth9245, 10/10 11:10
- **Part3-11** 편집기: 저장 → 검사 결과 표시 — kth9245, 10/10 11:09
- **Part2-17.3** gateway run_checks · GW-04 (황승주 SFT-03 뒤, 그 전엔 스텁) — 황승주, 10/10 11:09
- **Part2-17.2** gateway record_injections · GW-03 (묶음 A) — 황승주, 10/10 11:08
- **Part2-17.5** gateway tick_log · GW-07 (묶음 A) — 황승주, 10/10 11:08
- **Part2-17.4** gateway track_assignments · GW-05 (묶음 A) — 황승주, 10/10 11:08
- **Part1-9.2** 화면 스타일 정리(theme.css 토큰, 국방 톤) — kth9245, 10/10 11:07
- **Part2-5** sim `apply_events` — 최동호, 10/10 11:00 · SIM-09
- **Part1-13** 지표 패널 + 배속 + 다음 사건 — kth9245, 10/10 11:00
- **Part2-4** sim `advance_vehicles`(공개 API 이름 `advance`) — 최동호, 10/10 10:54 · SIM-08
- **Part1-10** 상황판 카드 열 + 결정 버튼 — kth9245, 10/10 10:52
- **Part2-3** sim `orbit_or_keep` — 최동호, 10/10 10:50 · SIM-07
- **Part3-10** 편집기: 카드 열(읽기 전용) — kth9245, 10/10 10:48 · 하위 1/1 완료
- **Part3-6** play `check_play` — 황승주, 10/10 10:44 · 하위 1/1 완료 · PLY-06
- **Part3-6.1** play check_operation · PLY-11 (통합 2, PLY-03~05 뒤) — 황승주, 10/10 10:44
- **Part1-7** gateway REST + WS — kth9245, 10/10 10:39
- **Part1-9.1** 드론 출발 위치 떼어 놓기(지도에서 겹침) — kth9245, 10/10 10:35
- **Part1-9** 지도: 위성 raster + 기체·표적·구역 — kth9245, 10/10 10:28 · 하위 3/3 완료
- **Part2-2** sim `follow_route` — 최동호, 10/10 10:28 · SIM-06
- **Part2-1** sim `move_straight` — 최동호, 10/10 10:25 · SIM-05
- **Part2-20** sim `load_scenario_json` — 최동호, 10/10 10:22 · SIM-04
- **Part3-5** play `check_zone` — 황승주, 10/10 10:20 · PLY-05
- **Part3-4** play `check_return_battery` — 황승주, 10/10 10:19 · PLY-04
- **Part3-3** play `check_report_points` — 황승주, 10/10 10:19 · PLY-03
- **Part3-8** play `list_templates` — 황승주, 10/10 10:16 · PLY-08
- **Part2-10** runtime `step_vehicle` — 황승주, 10/10 10:10 · 하위 1/1 완료 · RT-01
- **Part2-11** runtime `assign_roles` — 황승주, 10/10 10:10 · RT-02
- **Part2-14** runtime `apply_injection` — 황승주, 10/10 10:10 · RT-05
- **Part2-12** runtime `apply_decision` — 황승주, 10/10 10:09 · 하위 1/1 완료 · RT-03
- **Part2-10.1** runtime enter_step · RT-08 (PLY-07 뒤) — 황승주, 10/10 10:09
- **Part3-2** play `check_links` — 황승주, 10/10 10:07 · PLY-02
- **Part3-1** play `load_play` — 황승주, 10/10 10:06 · PLY-01
- **Part2-13** runtime `update_metrics` — 황승주, 10/10 10:05 · RT-04
- **Part2-16** runtime `apply_emergency` — 황승주, 10/10 10:05 · RT-07
- **Part2-15** runtime `apply_direct` — 황승주, 10/10 10:04 · RT-06
- **Part2-12.1** runtime switch_play · RT-09 (묶음 A, apply_decision·apply_injection·apply_reserves 전에) — 황승주, 10/10 10:04
- **Part3-7** play `expand_action` + 표 — 황승주, 10/10 10:02 · PLY-07
- **Part2-9** safety `check_command` — 황승주, 10/10 10:02 · SFT-03
- **Part2-8** safety `return_feasible` — 황승주, 10/10 10:00 · SFT-02
- **Part2-7** safety `point_in_polygon` — 황승주, 10/10 09:59 · SFT-01
- **Part1-17** 스파이크를 이식 모양으로 재배치(devil-advocate: SPEC 행마다 포맷된 파일, tick 계산 액션화, build_frame 새 이름, geo를 shared로, 모듈 AGENTS.md 정리) — kth9245, 10/10 00:22
- **Part1-16** 스파이크를 두 층 구조로 갱신(contracts 모델·시연 시나리오 사용, API.md 함수 이름, 35분 대본 테스트) — kth9245, 10/9 23:56
- **Part1-4** 시나리오 JSON + 템플릿 2개 — kth9245, 10/9 23:24
- **Part1-1** contracts 패키지 — kth9245, 10/9 23:19 · 하위 1/1 완료
- **Part1-1.1** contracts/API.md, contracts/README, AGENTS.md 읽을 목록, 09 문서 2·3절 정본 안내와 6절 수정 — kth9245, 10/9 23:18
- **Part1-2** 백령도 타일 커밋 — kth9245, 10/9 23:13
- **Part1-3** play·runtime·safety 뼈대 + SPEC 행 — kth9245, 10/9 02:28

## 뺌
- (없음)
