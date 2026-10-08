<!-- prefix: GW -->
# gateway SPEC

통합 1 구간(결정 0009): 틱 루프 `engine.py`(`tick`, `EngineState`, `TickOutcome`; 09 6절 Part2-17)와 GW-01 `build_frame` 재작성(Part2-18)은 최동호. REST·WS(`app.py`, Part1-7)는 리드. `engine.py`는 액션 파일이 아니라 모듈 파일(200줄 제한)이라 이 표에 행이 없다.

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| GW-01 | build_frame | t_ms, tracks, assessments, responses | Frame | 계약 Frame 생성 | 리드 | 완료 |
