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
