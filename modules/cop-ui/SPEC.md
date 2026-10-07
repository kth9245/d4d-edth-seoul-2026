<!-- prefix: UI -->
# cop-ui SPEC

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| UI-01 | toGeoJSON | Frame | FeatureCollection | 표적마다 점 1개, 분류·위협도·대응 속성 | 리드 | 완료 |
| UI-02 | useFrames | ws url | {frame, connected} | 끊기면 1초 뒤 재연결 | 리드 | 완료 |
| UI-03 | MapView | frame, center | 지도 | 분류별 색, 위협도별 크기 | 리드 | 완료 |
| UI-04 | AlertList | frame | 목록 | 위협도 내림차순, 대응 추천 표시 | 리드 | 완료 |
| UI-05 | basemapStyle | tilesAvailable | Style | 타일 있으면 로컬 pmtiles(라벨 없음), 없으면 배경만 | 리드 | 완료 |
