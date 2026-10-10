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
| UI-07 | frameMarkers | Frame | {vehicles, targets} | 기체마다 위치·상태, 표적마다 위치·종류·seen, 무력화 표적은 neutralized와 이름표 "<id> · 무력화"(지도에 회색 X, 기체 위, Part1-20) | 리드 | 완료 |
| UI-08 | parseFrame | ws 메시지 문자열 | Frame \| null | 깨진 메시지·옛 LegacyFrame은 null | 리드 | 완료 |
| UI-09 | fetchZone | — | Polygon \| null | GET /operation의 zone, 404·실패면 null(구역 없이 그림) | 리드 | 완료 |
| UI-10 | sceneFrames | contracts/examples/frames | SCENES s1~s8, SCENE_ZONE | 개발 서버 `?scene=s1`~`s8` 전용(타격 단계 순서 s1 s2 s3 s5 s6 s4 s7 s8), 시연 빌드에 없음 | 리드 | 완료 |
| UI-11 | describeAction·describeCondition | Action / Condition | string | 행동·조건 한국어 한 줄, 라벨 표 Record로 빠짐 없음 | 리드 | 완료 |
| UI-12 | groupPlays | Play[], 적 플레이 id | PlayGroup[] | 드론·수상정·지상·공통 묶음, 영역 둘 이상·없음은 공통, 적이 따르는 플레이는 맨 아래 '적' 묶음(Part1-21) | 리드 | 완료 |
| UI-13 | vehicleColumns | Operation, Play[] | Column[] | 기체별 시작 플레이 + 선택지로 이어지는 플레이, 순환 종료, 없는 플레이 null | 리드 | 완료 |
| UI-14 | playUsage | Operation, Play[], EnemySpec[] | Record<playId, Usage[]> | 작전 시작·선택지·전체 전환으로 쓰는 기체, 적 플레이는 그 적과 등장 시각(Part1-21) | 리드 | 완료 |
| UI-15 | loadEditorData | fetch | EditorData | /operation·/plays·/vehicles·/enemies를 읽음. 실패하면 오류(예시 데이터 대체는 통합 2 전에 제거, 편집기가 연결 실패를 표시) | 리드 | 완료 |
| UI-16 | EditorScreen | — | 편집기 화면 | 예시 작전이 왼쪽 바·작전 개요·플레이 카드로 그려짐(Part3-10), 탭 #editor·#live(tabFromHash) | 리드 | 완료 |
| UI-17 | kstTime | t_ms | "HH:MM:SS" | 기계 시간대와 무관하게 KST(결정 0012) | 리드 | 완료 |
| UI-18 | postDecision | report_id, choice_id | {ok, id} \| {ok: false, error} | POST /decisions, 실패해도 throw 없이 상태·detail 문구 | 리드 | 완료 |
| UI-19 | frameCards | Frame | Card[] | 보고(injection_pending·command_blocked 제외)+injections+blocks, 최신이 위, 처리된 것 done, 선택지마다 기체별 전환 줄, 무력화 카드에 근거 줄(운용자 결정 id·선택지 이름 → 타격 기체 · 통과한 검사, Part1-20) | 리드 | 완료 |
| UI-20 | pruneSent | 보낸 기록, 보고 id, 시각 역행 | 보낸 기록 | reset으로 사라진 보고·시각이 뒤로 가면 잊음(같은 id 카드가 잠기지 않게) | 리드 | 완료 |
| UI-21 | CardList | frame | 카드 열 | 선택지 버튼 → POST /decisions, 보낸 뒤 처리될 때까지 잠금, 실패 문구 | 리드 | 완료 |
| UI-22 | mmss | ms | "m:ss" | 1초 미만 버림, 60분 넘어도 분으로, 음수는 0:00 | 리드 | 완료 |
| UI-23 | nextStop | 작전 시작 후 ms, RUN_STOPS | RunStop \| null | 현재보다 뒤의 첫 정지 시각(정지 시각 위면 다음 것). 정지 시각은 실제 엔진의 타격 단계 순서 장면 시각(16:25 보고 카드, 19:05 드론1 귀환, 20:00 드론2 직접 조종, 23:05 고속정 등장), 타격 장면은 정지 없이 재생(Part1-13.1) | 리드 | 완료 |
| UI-24 | postRun·jumpPaused | 경로 / offset_ms | {ok, run} \| {ok: false, error} | POST /run/*, throw 없이 상태·detail 문구. 다음 사건은 speed=0 뒤 jump, 정지 실패면 jump 안 함 | 리드 | 완료 |
| UI-25 | metricView | Metrics | {operator, manual, rows} | 운용자 조작 대 수동 기준, 기체 공백 m:ss, 빠진 칸 0. 임무 판정 행은 없음(타격 결과는 결과 카드, Part1-20) | 리드 | 완료 |
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
| UI-43 | blankPlay·NewPlayMenu | 이름, 영역 | Play / 새로 만들기 메뉴 | '새로 만들기' → 'AI로 생성'(초안 칸) 또는 '직접 생성'(시작 카드 하나, 겹치지 않는 id, 사람 작성이라 승인됨), 둘 다 미저장으로 열림 | 리드 | 완료 |
| UI-44 | openView·backFrom | 보던 화면, 다음 화면 | 화면 기록 | 연 순서를 기억해 '← 뒤로'가 같은 길로 돌아감(목록·카드 안 플레이 링크), 기록 없으면 작전 개요 | 리드 | 폐기(Part1-33: 플레이 화면 버튼은 언제나 "← 작전 개요", 화면 순서 기록 없음) |
| UI-45 | directAims | Frame, 방금 보낸 명령 | 십자 목록 | 직접 조종 십자는 프레임 기준(operator_direct move 실행 중이고 step 밖인 기체의 목표). 차단된 명령은 십자 없음, 대안 지점이면 그쪽, 도착하면 없어짐. 방금 보낸 명령은 다음 프레임 전까지만 | 리드 | 완료 |
| UI-46 | updateStep·setActionKind·addStepAfter·removeStep·addChoice·removeChoice·defaultCondition·zoneCentre | Play, 카드 id | 새 Play | 카드 편집(Part3-12.1, StepEditor 패널): 이름·행동(대상·거리, 이동·경로 좌표는 플레이의 점 또는 구역 중심)·연결(조건·값·다음 카드)·보고(문구·선택지·기체별 플레이)·카드 추가(도착 연결)·삭제(들어오는 연결·비상 연결도 정리, 시작 카드 제외). 선택지를 지우면 그 선택 연결도 지움 | 리드 | 완료 |
| UI-47 | vehicleRows·switchRows·startText | Operation, VehicleSpec[] | 패널 줄 | 작전 설정 패널(Part3-14, 보여 주기만): 기체별 종류·처음 플레이·예비 순서, 전환 버튼별 기체→플레이, 시작 시각 KST. OperationPanel이 편집기 작전 개요 위에, MiniMap(작전 구역 + 출발 위치, 조작 없음, 영상 출처는 지도 아래) | 리드 | 완료 |
| UI-48 | enemyRows·appearText | EnemySpec[], 작전 시작 시각, Play[] | 적 열 머리 | 편집기 작전 개요 아군 열 아래 '적' 구역(Part1-21, 결정 0032, 읽기 전용): 적마다 종류·등장 시각 KST(+분)·위치 좌표 또는 'boat1 위치에서'·속도, 그 아래 플레이 카드(StepCard). 플레이가 없으면 없는 플레이로 표시. 데이터는 GET /enemies | 리드 | 완료 |
| UI-49 | fetchScenarios | — | ScenarioInfo[] | GET /scenarios(결정 0042), 오류·연결 실패·목록 아님이면 빈 목록 | 리드 | 완료 |
| UI-50 | activateScenario | 작전 id | RunState | POST /scenarios/{id}/activate(그 작전을 실행 작전으로, 시작 전 멈춤), 2xx 아니면·연결 실패면 오류 | 리드 | 완료 |
| UI-51 | stopsFor | 실행 작전 id | RunStop[] | 야간 시연(baengnyeong_night)이면 RUN_STOPS, 그 밖은 없음(다음 사건 없음, 결정 0042) | 리드 | 완료 |
| UI-52 | applyRoute·setLoop·routeChoice·ROUTE_KINDS | Play, 카드 id, RouteDef/반복 | 새 Play / 경로 id | 경로 비행(결정 0044·0045): 고른 경로를 카드에 복사(고정=route, 상대=offsets, route_name), 반복=patrol_route·한 번=move_to(점 하나 이동은 반복 시 한 점 route), 행동을 바꾸면 경로 값 지움, 목록에 없는 경로는 "" | 리드 | 완료 |
| UI-53 | describeAction·describeCondition(경로·T+) | Action/Condition | 카드 문구 | "경로 비행 · 이름|경로 N곳 · 한 번|반복 · 기체 위치 기준", at_time은 T+m:ss | 리드 | 완료 |
| UI-54 | deletePlay | 플레이 id | 서버에 있었나(bool) | DELETE /plays/{id}(결정 0050, 실행 작전에서 지우고 시작 전으로), 404는 저장 전 새 플레이라 false, 그 밖의 실패는 오류. 플레이 화면 "삭제"는 두 번 누르기, 지운 뒤 작전 개요 | 리드 | 완료 |
| UI-55 | fetchOntology | — | OntologyView | GET /ontology(결정 0038), 실패하면 서버 detail("이 시나리오에는 온톨로지가 없습니다")을 담은 오류, 온톨로지 화면이 그 문구를 보임(결정 0051) | 리드 | 완료 |
| UI-80 | decisionQueue | Card[], t_ms | {action, alerts, history} | 선택지 있는 미처리 보고·대기 전환·대안 있는 차단(그 기체에 차단 뒤 새 명령이 나갈 때까지, 최대 2분)이 대기열, 같은 전환의 표적 선택 여러 장은 한 항목, 순서 타격 허락 > 차단 > 전환 > 위험도(표적 선택은 0.55, 같으면 최신), 2분 안의 무력화·공백·배터리·차단은 알림, 나머지 최신 위(Part1-32) | 리드 | 완료 |
| UI-81 | choiceGroups | CardChoice[] | {planned, requests} | 정해진 선택지 먼저 엔진 순서(결정 0046), "X → 무엇" 한 기체 선택지는 무엇별 묶음(발생 지역 순찰 → "… 이어받기", 함께 감시 → "Y와 함께 T 감시") | 리드 | 완료 |
| UI-82 | trackState | Target, t_ms, 기준점 | {k, pos, est?, agoMs?, dir?, speed?} | seen·rf·lost·never·gone, lost는 마지막으로 본 위치(없으면 실제 위치), 0.3 m/s 미만 정지, 기준점 쪽 접근·반대 이탈(기준점 없으면 접근), 추정 위치 = 마지막 위치 + 속도 × 지난 시간(결정 0047) | 리드 | 완료 |
| UI-83 | targetStage | Frame, Target, Track | {key, label, detail, away} | 무력화 > 타격 중 > 허락 대기 > 놓침(경과·방향·속도, 이탈이면 away) > RF 탐지 > 미탐 > 추적(임무 중 기체만) > 발견 | 리드 | 완료 |
| UI-84 | situationCounts | Stage[], Queue | {targets, stages, decisions} | 단계별 개수 급한 순, 0개 뺌, 결정 수는 합친 표적 선택의 기체 수만큼 | 리드 | 완료 |
| UI-85 | vehicleRows | Frame, 플레이 이름, VehicleSpec[] | VehicleRow[] | 하는 일(귀환 중·기지 정비·플레이 이름·대기), 종류 한글, 표적·타격은 임무 중일 때만, 배터리(35% 미만 low), 결정 대기(Part1-32) | 리드 | 완료 |
| UI-86 | targetPlays | Play[], 도메인 | Play[] | 첫 step이 watch_target·approach_target이고 그 도메인을 쓰는 플레이, strike_target 없음(결정 0048) | 리드 | 완료 |
| UI-88 | postPoint | 기체, 플레이, 표적 | Sent | POST /injections {play_by_vehicle, target_by_vehicle, approve: true}(결정 0049), throw 없음 | 리드 | 완료 |
| UI-87 | cameraPoints | Frame, Track 묶음, Queue | GeoPoint[] | 표적 표시 위치·추정 위치(2분 넘은 무력화 제외), 임무 중 표적 맡은 기체, 열린 카드가 부르는 기체(보고·선택지 미리 보기), 차단 대안 지점, 없으면 빈 목록(Part1-32) | 리드 | 완료 |
| UI-89 | fetchBoardData | — | {plays, vehicles, watch} | GET /plays·/vehicles·/watch_points, 실패·목록 아님·연결 실패는 빈 목록 | 리드 | 완료 |
| UI-91 | linkLines | Frame, Track 묶음, Queue | FeatureCollection | 임무 중 기체→표적(감시·타격, 무력화 표적엔 타격만), 놓친 표적 추정선, 차단 기체→대안 지점 | 리드 | 완료 |
| UI-92 | watchCircles | WatchPoint[] | FeatureCollection | 기준점 반경 고리(64칸, 닫힘) | 리드 | 완료 |
