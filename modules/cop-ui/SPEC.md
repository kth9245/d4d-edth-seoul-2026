<!-- prefix: UI -->
# cop-ui SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| UI-01 | toGeoJSON | LegacyFrame | FeatureCollection | — | 리드 | 폐기(Part1-9, UI-07로 대체) |
| UI-02 | useFrames | ws url | {frame, connected} | 끊기면 1초 뒤 재연결, parseFrame을 통과한 Frame만 | 리드 | 완료 |
| UI-03 | MapView | frame, zone, tilesAvailable | 지도 | 위성 배경 위에 구역 다각형, 기체(상태 색)·표적(종류 색) HTML 마커와 이름표 | 리드 | 완료 |
| UI-04 | AlertList | LegacyFrame | 목록 | — | 리드 | 폐기(Part1-9, 카드 열은 Part1-10) |
| UI-05 | basemapStyle | tilesAvailable | Style | 타일 있으면 백령도 EOX raster z8~14(받은 범위만 요청, 출처 표기, 야간 밝기), 없으면 배경만 | 리드 | 완료 |
| UI-06 | zoneGeoJSON | Polygon \| null | FeatureCollection | 닫힌 [lon, lat] 고리 하나, 구역 없으면 빈 묶음 | 리드 | 완료 |
| UI-07 | frameMarkers | Frame | {vehicles, targets} | 기체마다 위치·상태, 표적마다 위치·종류·seen | 리드 | 완료 |
| UI-08 | parseFrame | ws 메시지 문자열 | Frame \| null | 깨진 메시지·옛 LegacyFrame은 null | 리드 | 완료 |
| UI-09 | fetchZone | — | Polygon \| null | GET /operation의 zone, 404·실패면 null(구역 없이 그림) | 리드 | 완료 |
| UI-10 | sceneFrames | contracts/examples/frames | SCENES s1~s6, SCENE_ZONE | 개발 서버 `?scene=s1`~`s6` 전용, 시연 빌드에 없음 | 리드 | 완료 |
| UI-11 | describeAction·describeCondition | Action / Condition | string | 행동·조건 한국어 한 줄, 라벨 표 Record로 빠짐 없음 | 리드 | 완료 |
| UI-12 | groupPlays | Play[] | PlayGroup[] | 드론·수상정·지상·공통 묶음, 영역 둘 이상·없음은 공통 | 리드 | 완료 |
| UI-13 | vehicleColumns | Operation, Play[] | Column[] | 기체별 시작 플레이 + 선택지로 이어지는 플레이, 순환 종료, 없는 플레이 null | 리드 | 완료 |
| UI-14 | playUsage | Operation, Play[] | Record<playId, Usage[]> | 작전 시작·선택지·전체 전환으로 쓰는 기체 | 리드 | 완료 |
| UI-15 | loadEditorData | fetch | EditorData | /operation·/plays 실패 시 예시 시나리오 + source=example(통합 2 전 제거) | 리드 | 완료 |
| UI-16 | EditorScreen | — | 편집기 화면 | 예시 작전이 왼쪽 바·작전 개요·플레이 카드로 그려짐(Part3-10), 탭 #editor·#live(tabFromHash) | 리드 | 완료 |
| UI-17 | kstTime | t_ms | "HH:MM:SS" | 기계 시간대와 무관하게 KST(결정 0012) | 리드 | 완료 |
| UI-18 | postDecision | report_id, choice_id | {ok, id} \| {ok: false, error} | POST /decisions, 실패해도 throw 없이 상태·detail 문구 | 리드 | 완료 |
| UI-19 | frameCards | Frame | Card[] | 보고(injection_pending·command_blocked 제외)+injections+blocks, 최신이 위, 처리된 것 done, 선택지마다 기체별 전환 줄 | 리드 | 완료 |
| UI-20 | pruneSent | 보낸 기록, 보고 id, 시각 역행 | 보낸 기록 | reset으로 사라진 보고·시각이 뒤로 가면 잊음(같은 id 카드가 잠기지 않게) | 리드 | 완료 |
| UI-21 | CardList | frame | 카드 열 | 선택지 버튼 → POST /decisions, 보낸 뒤 처리될 때까지 잠금, 실패 문구 | 리드 | 완료 |
| UI-22 | mmss | ms | "m:ss" | 1초 미만 버림, 60분 넘어도 분으로, 음수는 0:00 | 리드 | 완료 |
| UI-23 | nextStop | 작전 시작 후 ms, RUN_STOPS | RunStop \| null | 현재보다 뒤의 첫 정지 시각(정지 시각 위면 다음 것). 정지 시각은 스파이크 엔진 기준, Part1-14에서 engine.py로 재확인 | 리드 | 완료 |
| UI-24 | postRun·jumpPaused | 경로 / offset_ms | {ok, run} \| {ok: false, error} | POST /run/*, throw 없이 상태·detail 문구. 다음 사건은 speed=0 뒤 jump, 정지 실패면 jump 안 함 | 리드 | 완료 |
| UI-25 | metricView | Metrics | {operator, manual, rows} | 운용자 조작 대 수동 기준, 기체 공백 m:ss, 빠진 칸 0, 임무 판정 전·성공·실패 | 리드 | 완료 |
| UI-26 | fetchOperation | — | Partial<Operation> \| null | GET /operation 본문, 오류·JSON 아님·실패는 null(fetchZone·RunBar가 씀) | 리드 | 완료 |
| UI-27 | RunBar | frame | 지도 아래 재생 막대 | T+시계, 재생/일시정지(직전 배속으로 재개), ×1·5·10·30, 다음 사건(사건 직후 일시정지), 처음으로(확인창) | 리드 | 완료 |
| UI-28 | MetricsPanel | Metrics | 지표 패널 | 운용자 조작 대 기체별 직접 명령 수 나란히, 나머지 지표, 수동 기준 주석 | 리드 | 완료 |
| UI-29 | savePlay | Play | PlayCheck | POST /plays(검사 통과 시 서버 메모리에 저장·실행을 시작 전으로), 2xx 아니면·연결 실패면 오류 | 리드 | 완료 |
| UI-30 | issuesByStep·batteryText | PlayCheck, Play | {byStep, general} / string | step id 있는 오류는 그 카드에, 없거나 모르는 step은 플레이 머리에, 예상 귀환 배터리 한 줄 (편집기 저장 막대, Part3-11) | 리드 | 완료 |
| UI-31 | postJson | url, body? | {ok, id} \| {ok: false, error} | POST 공통: 실패해도 throw 없이 상태·detail, postDecision이 씀 | 리드 | 완료 |
| UI-32 | postSwitch·postSettle | SwitchIn / injection id, 승인 여부 | {ok, id} \| 오류 | POST /injections, /injections/{id}/approve·reject | 리드 | 완료 |
| UI-33 | fetchPlays | — | Play[] | GET /plays, 실패·목록 아님이면 [] | 리드 | 완료 |
| UI-34 | SwitchPanel | frame | 전환 요청 패널 | 작전 전체 전환 버튼 + 일부 전환(기체·플레이) → 승인 대기 생성 | 리드 | 완료 |
| UI-35 | postDirect | vehicle_id, GeoPoint | {ok, id} \| 오류 | POST /direct {vehicle_id, target} | 리드 | 완료 |
| UI-36 | useDirectControl | — | 선택·목표·안내 줄 | 기체 클릭 선택, 지도 클릭 → POST /direct 뒤 해제, Esc·같은 기체 다시 누르면 취소, 기체 클릭은 지도 클릭으로 안 샘 | 리드 | 완료 |
| UI-37 | insertReportStep | Play, 접근 step id | Play | 접근 앞에 hold + 선택지 하나 보고 step, 선택지의 operator_choice 탈출이 접근으로(결정 0031), 접근으로 가던 탈출은 보고로, 원본 안 바꿈 | 리드 | 완료 |
| UI-38 | saveErrorText | 저장 오류 문구 | 화면 문구 | 게이트웨이 응답 상태 코드 표시, 응답 없으면 서버 응답 없음 | 리드 | 완료 |
| UI-39 | postDraft·forSave | 문장 / Play | {ok, play} \| 오류 / Play | POST /plays/draft, AI 초안은 저장 때 approved=true(검사 통과 + 사람이 저장 = 승인) | 리드 | 완료 |
| UI-40 | DraftBox | — | AI 초안 칸 | 시연 문장 버튼(demo/draft_sentences.json) + 입력칸 → 초안이 미저장 플레이로 열림, 대기 템플릿 대체 알림 | 리드 | 완료 |
| UI-41 | layoutSteps·stepEdges·exitText | Play | 카드 위치 / 연결선 / 조건 문구 | 시작 step 왼쪽부터 탈출 깊이로 열 배치(겹침 없음, 닿지 않는 step은 다음 열), 탈출마다 연결선(운용자 선택·오류 step 구분), 없는 step은 선 없음 | 리드 | 완료 |
| UI-42 | PlayGraph·StepNode | Play, 검사 결과 | 그래프 화면 | React Flow 카드(행동·보고·연결 칸, 연결 줄마다 연결점, 변경 표시) + 점선 곡선 연결선과 조건 이름 | 리드 | 완료 |
