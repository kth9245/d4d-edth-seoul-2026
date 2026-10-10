<!-- 자동 생성 파일 (scripts/task.py). 직접 수정하지 마세요. -->

# 지금 작업판

마지막 기록 10/10 12:04 KST · 상세(입력·출력·완료 기준)는 docs/research/09 6절 · 기록은 `uv run python scripts/task.py`로만

## 진행중
- **Part2-19** 시나리오 튜닝 — 최동호, 10/10 12:02부터

## 막힘
- (없음)

## 예정

### kth9245
- **Part1-14** smoke 전환 + 통합 주관
- **Part1-15** 3분 대본·BUILT_HERE·제출 설명
- **Part3-14** 작전 설정 패널

### 황승주
- **Part2-21** 타격 runtime: enter_step·apply_decision·switch_play (결정 id·승인 표적·카드 닫기)
- **Part2-22** 타격 safety: 규칙 1에 타격 = 결정 id 필요
- **Part2-23** 타격 sim: advance 타격 분기·resolve_strikes 새 액션·update_metrics 작전 성공

### 최동호
- **Part2-24** 타격 engine.py: resolve_strikes 호출 + 타격 통과 기록 줄
- **Part2-25** sim 적 진행(SIM-11, 결정 0032) + engine.py 호출

### 누구나
- **Part1-18** 타격: 계약 추가 5개 + play 대응표 행 + TS·예시 (한 커밋)
- **Part1-19** 타격: 시나리오·플레이 JSON (fast1 동쪽 해안 우회, track_fast 수정·track_fast_sea·strike, 고속 보트 추적 전환 버튼)
- **Part1-20** 타격: 화면 (무력화 표적 X·결과 카드·작전 성공·예시 장면 s7·s8)
- **Part1-21** 편집기 적 열 + GET /enemies (결정 0032, 읽기 전용)
- **Part3-10.1** 워크플로우 그래프 보기(step 카드 + 조건 연결선, React Flow)

## 최근 결정
- 10/10 11:57 kth9245 · Part1-19 · 구조만 쓴다(enemies·적 플레이·track_fast·track_fast_sea·strike·전환 버튼·capabilities). 숫자는 대략값, 맞추기는 Part2-19. 완료 기준을 check_operation 통과 + 틱 루프가 오류 없이 돌고 fast1이 나타나 움직임으로 낮춤(s7·s8 도달은 Part2-19). fast1은 spec 5절의 split_target(ve·vn)이 아니라 10.1의 enemy_fast1로 쓴다. 리드 답 'ㅇㅇ 이렇게 ㄱㄱ'
- 10/10 11:56 kth9245 · Part2-19 · fast1(사건 4, 적 enemies) 등장 시각·경로점·속도와 타격 시점까지 baengnyeong_night.json의 숫자는 전부 Part2-19가 한 타임라인으로 맞춘다. s5·s6이 s4 앞으로 옮겨져 드론2 배터리가 타격 명령의 귀환 배터리 검사에 걸리므로 숫자를 한 사람이 맡는다. 완료 기준: 틱 루프로 s1·s2·s3·s5·s6·s4·s7·s8이 이 순서로 남. fast1 부분은 Part1-19·Part2-21~25 뒤. 09 6절 행 수정(b2dd55a). 리드 답 'ㅇㅇ 이렇게 ㄱㄱ'
- 10/10 11:55 kth9245 · Part3-13 · POST /plays/draft는 draft_play를 별도 스레드에서 돌려 WS를 멈추지 않는다. 편집기 AI 초안 칸은 demo/draft_sentences.json 문장 버튼(캐시와 같은 출처)과 입력칸. 초안은 목록에 '아직 저장 안 됨'으로, 'AI 초안 · 승인 전' 표시. 저장 시 approved=true로 보낸다(검사 통과 + 사람이 저장 = 승인, safety가 approved=false 플레이 명령을 막음). origin이 ai_draft가 아니면 대기 템플릿 대체를 알림. 리드 답 'ㄱㄱ'
- 10/10 11:46 kth9245 · Part3-12 · 결정 0031 참조(보고 선택지가 보고한 기체를 다른 플레이로 안 보내면 같은 플레이의 operator_choice 탈출로 이어짐, runtime apply_decision 수정은 이 세션이 하고 황승주에게 알림)
- 10/10 11:45 황승주 · Part3-15.1 · compile_mavlink(play, op, specs: dict[id, VehicleSpec]): op.assign에서 이 플레이를 받는 기체마다 (plan, script). .plan = entry step 미션(QGC Plan, ArduPilot, MAV_TYPE 2/11/10, 드론 고도 50 m), 스크립트 = step 그래프 전체(pymavlink, 틀 modules/mavlink/vehicle_script.py.txt). 대응: move/follow_route/zigzag→WAYPOINT 16, return_home→RTL 20, keep_distance→DO_SET_MODE 176 FOLLOW(Copter 23·Rover 6), 지상 hold→DO_SET_MODE HOLD 4, orbit/hold/relay→LOITER_UNLIM 17(좌표 없으면 0,0=현재 위치), expand_action None→빈 미션. 지상 신호는 STATUSTEXT target_found/signal/choice:<id>
- 10/10 11:37 kth9245 · Part1-11 · 직접 조종은 기체 클릭(선택, 초록 링·안내 줄·십자 커서) → 지도 클릭 → POST /direct, 보낸 뒤 선택 해제, Esc나 같은 기체 다시 누르면 취소. 차단 카드에 대안 지점이 있으면 '대안 지점으로' → 같은 기체로 대안 좌표 POST /direct. 막힘 판단은 서버(safety)만. 리드 답 'ㄱㄱ'
- 10/10 11:36 kth9245 · Part3-15.1 · 황승주에게 넘김(결정 0019, 황승주 세션이 일손 남는다고 제안). 리드 답 'Part3-15.1 compile_mavlink'. 상위 Part3-15(누구나)는 그대로 두고 3-15.1이 끝나면 같이 done
- 10/10 11:19 kth9245 · Part1-12 · 사건 4를 화면만으로 끝내려고 Part1-12에 전환 요청 패널(작전 전체 전환 버튼 + 일부 전환: 기체·플레이 고르고 요청 → POST /injections)을 넣는다. 승인 대기 카드에 승인(주)·거부(보조) 버튼과 바뀌는 내용(d2→track_fast)을 붙인다. 리드 답 'ㄱㄱ'
- 10/10 11:13 kth9245 · Part1-9.3 · D4D 홈페이지 톤: 검정 바탕, 초록 #4ade80은 시스템 상태(연결·선택·성공), 흰 주 버튼, 각진 1px 선, Orbitron 화면 이름·큰 숫자, JetBrains Mono 대문자 코드, Pretendard 본문. 글꼴은 npm(OFL)으로 번들해 오프라인 동작. 지도 기호는 군 표준 소속 색(아군 시안) 유지. 리드 답 'd4d 홈페이지 느낌', 'ㄱㄱ 디자인 좀 간지나게'
- 10/10 11:02 kth9245 · Part1-9.2 · 색·글꼴은 src/theme.css 토큰 한 곳에서 정하고 기존 CSS는 배치만 맡는다. 지도 출처는 EOX 문구만 작고 흐린 한 줄(MapLibre 표시·흰 상자 제거, 라이선스상 완전 삭제 불가). 기호는 소속 색(아군 시안·미식별 노랑·적대 빨강), 기체 상태는 모양으로. 훈련 표시 띠는 넣지 않음. 리드 답 '작고 흐린 한 줄', '소속 색 + 상태는 모양', '빼기'

## 완료
- **Part3-13** 편집기: AI 초안 입력 칸 — kth9245, 10/10 11:59
- **Part3-12** 편집기: 카드 편집 — kth9245, 10/10 11:51
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
- **Part3-10** 편집기: 카드 열(읽기 전용) — kth9245, 10/10 10:48 · 하위 0/1 완료
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
