# 해커톤 중 새로 만든 부분

심사에서 "해커톤에서 새로 만든 부분"을 구분해 발표해야 한다. 기능을 완성할 때마다 한 줄씩 추가한다.

## 대회 전에 준비한 것 (새로 만든 것 아님)
- 저장소 골격, 규칙 문서, 검사 스크립트, 가짜 로직 walking skeleton, 로컬 지도 타일

## 해커톤 중 만든 것
| 시각 | 모듈 | 내용 | 담당 |
|---|---|---|---|
| 10/10 10:40 | cop-ui | Part1-9 지도: 백령도 EOX 위성 raster, 작전 구역(GET /operation), 기체·표적 HTML 마커(상태·종류 색), 개발용 `?scene=s1`~`s6`, MapLibre worker 경로 수정 | kth9245 |
| 10/10 10:45 | gateway | REST(플레이·작전·실행·결정·직접 조종·전환 요청/승인) + WS Frame 송출, 배속·일시정지·다음 사건 점프, engine.py 전 스텁 (Part1-7) | kth9245 |
| 10/10 10:40 | cop-ui | Part3-10 편집기 탭: 플레이 목록(영역별), 플레이 하나의 읽기 전용 step 카드, 작전 개요(기체별 시작 + 선택지로 이어지는 플레이), 서버 없으면 예시 데이터 표시 | kth9245 |
| 10/10 11:20 | play | Part1-5.1 AI 초안 프롬프트 `build_draft_prompt`(PLY-12, change_cot식 절 구조, JSON 출력, 결정 0028 Grok) + 시연 문장 2개 `demo/draft_sentences.json`. grok-4.7로 두 문장 확인: no_report는 `missing_report_point` 하나만, usv_patrol은 검사 통과 | kth9245 |
| 10/10 11:15 | demo | Part1-5 AI 초안 캐시 2개 `demo/plays/cache/<sha256(prompt)>.json`(grok-4.7 응답, `scripts/make_draft_cache.py`로 재생성), `tests/test_draft_cache.py`가 프롬프트·작전이 바뀌어 캐시가 안 맞으면 실패 | kth9245 |
| 10/10 10:55 | cop-ui | Part1-10 상황판 카드 열: 보고·승인 대기·차단 카드(KST 시각, 처리됨 표시), 선택지 버튼 → POST /decisions와 기체별 전환 미리 보기 | kth9245 |
| 10/10 11:00 | cop-ui | Part1-13 상황판 재생 막대(지도 아래: T+시계, 재생/일시정지, 배속 ×1·5·10·30, 다음 사건 → 사건 직후 일시정지, 처음으로)와 지표 패널(운용자 조작 대 기체별 직접 명령 수, 같은 실행에서 센 수동 기준) | kth9245 |
| 10/10 11:10 | cop-ui | 화면 스타일 정리(theme.css 토큰): 군 표준 소속 색 기호(아군 시안·미식별 노랑·적대 빨강, 상태는 모양), 각진 패널, DIN 계열 숫자 글꼴, 지도 출처 한 줄 | kth9245 |
| 10/10 11:08 | gateway, cop-ui | Part3-11 편집기 저장: 플레이 머리 저장 버튼 → POST /plays(GW-08 check_saved_play로 플레이 검사 + 그 저장으로 새로 생긴 작전 오류, 통과하면 메모리에 저장하고 실행을 시작 전으로), 오류는 해당 step 카드 옆에 빨갛게, 예상 귀환 배터리 표시. POST /plays/check(검사만) | kth9245 |
| 10/10 11:30 | cop-ui | 디자인 v2(D4D 톤): 검정·격자 바탕, 초록 상태색, 흰 주 버튼, Pretendard·Orbitron·JetBrains Mono 번들(오프라인), 카드 상태 코드 | kth9245 |
| 10/10 11:35 | cop-ui | Part1-12 전환 요청 패널(전체 전환 버튼·일부 전환) + 승인 대기 카드의 승인·거부 버튼과 바뀌는 내용 미리 보기 | kth9245 |
| 10/10 11:45 | cop-ui | Part1-11 직접 조종(기체 클릭 → 지도 클릭 → POST /direct, 선택 링·목표 십자·안내 줄) + 차단 카드 "대안 지점으로" 버튼 | kth9245 |
