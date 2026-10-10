<!-- 자동 생성 파일 (scripts/task.py). 직접 수정하지 마세요. -->

# 지금 작업판

마지막 기록 10/10 10:10 KST · 상세(입력·출력·완료 기준)는 docs/research/09 6절 · 기록은 `uv run python scripts/task.py`로만

## 진행중
- (없음)

## 막힘
- (없음)

## 예정

### kth9245
- **Part1-5** AI 초안 프롬프트·캐시 2개
- **Part1-7** gateway REST + WS
- **Part1-9** 지도: 위성 raster + 기체·표적·구역
- **Part1-10** 상황판 카드 열 + 결정 버튼
- **Part1-11** 직접 조종 + 차단 카드 대안 버튼
- **Part1-12** 주입 승인 카드
- **Part1-13** 지표 패널 + 배속 + 다음 사건
- **Part1-14** smoke 전환 + 통합 주관
- **Part1-15** 3분 대본·BUILT_HERE·제출 설명
- **Part3-10** 편집기: 카드 열(읽기 전용)
- **Part3-11** 편집기: 저장 → 검사 결과 표시
- **Part3-12** 편집기: 카드 편집
- **Part3-13** 편집기: AI 초안 입력 칸
- **Part3-14** 작전 설정 패널
- **Part3-15.1** mavlink compile_mavlink · MAV-01 (리드, 결정 0025, 통합 2 뒤)

### 황승주
- **Part2-10** runtime `step_vehicle` · 하위 1/1 완료 · RT-01
- **Part2-11** runtime `assign_roles` · RT-02
- **Part3-3** play `check_report_points` · PLY-03
- **Part3-4** play `check_return_battery` · PLY-04
- **Part3-5** play `check_zone` · PLY-05
- **Part3-6** play `check_play` · 하위 0/1 완료 · PLY-06
- **Part3-6.1** play check_operation · PLY-11 (통합 2, PLY-03~05 뒤)
- **Part3-8** play `list_templates` · PLY-08
- **Part3-9** play `draft_play` · PLY-09

### 최동호
- **Part2-1** sim `move_straight` · SIM-05
- **Part2-2** sim `follow_route` · SIM-06
- **Part2-3** sim `orbit_or_keep` · SIM-07
- **Part2-4** sim `advance_vehicles`(공개 API 이름 `advance`) · SIM-08
- **Part2-5** sim `apply_events` · SIM-09
- **Part2-6** sensing `observe_targets`(공개 API 이름 `observe`) · SNS-02
- **Part2-17** gateway `engine.py` 틱 루프 · 하위 0/5 완료
- **Part2-17.1** gateway init_engine · GW-02 (묶음 A, engine_state.py 먼저)
- **Part2-17.2** gateway record_injections · GW-03 (묶음 A)
- **Part2-17.3** gateway run_checks · GW-04 (황승주 SFT-03 뒤, 그 전엔 스텁)
- **Part2-17.4** gateway track_assignments · GW-05 (묶음 A)
- **Part2-17.5** gateway tick_log · GW-07 (묶음 A)
- **Part2-18** gateway `build_frame` 재작성
- **Part2-19** 시나리오 튜닝
- **Part2-20** sim `load_scenario_json` · SIM-04

### 누구나
- **Part3-15** play `compile_mavlink` (결정 0011) · 하위 0/1 완료 · PLY-10

## 최근 결정
- 10/9 23:20 kth9245 · Part1-4 · 사건 4 고속 보트 추적 플레이의 표적은 운용자가 고름(target: operator → 승인 뒤 target_select 카드). 리드 답 '운용자가 고름'
- 10/9 23:14 kth9245 · Part1-1 · 결정 0015·0016·0017·0018 참조(두 층 구조, contracts 세부, API 규약)

## 완료
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
