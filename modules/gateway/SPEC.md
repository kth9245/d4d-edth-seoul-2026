<!-- prefix: GW -->
# gateway SPEC

통합 1 구간(결정 0009): 틱 루프 `engine.py`(`tick`, 호출 순서만)·`engine_state.py`(`EngineState`)와 GW-02~07 액션은 최동호(09 6절 Part2-17·2-18). 원본은 `knowledge/spikes/rolecall_engine_proto/port/modules/gateway/`를 그대로 복사. GW-01 `build_frame`은 레거시 smoke가 쓰므로 통합 1까지 그대로 두고 새 Frame은 GW-06 `build_frame_v2`. REST·WS(`app.py`, Part1-7)는 리드. `engine.py`·`engine_state.py`와 Part1-7의 `live.py`(실행 상태·입력 대기열)·`stub_engine.py`(engine.py 전 임시, 통합 2 전 삭제)는 액션 파일이 아니라 이 표에 행이 없다.

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| GW-01 | build_frame | t_ms, tracks, assessments, responses | Frame | 계약 Frame 생성 | 리드 | 완료 |
| GW-02 | init_engine | Scenario | EngineState | 기체 home·ready, play_id=op.assign, step=entry, t_ms=started_ms, 배정 작전 배정. 원본: 스파이크 port | 최동호 | 예정 |
| GW-03 | record_injections | injections, reports, requests, t_ms | (injections, reports, new_reports, approved) | pending이면 injection_pending 카드, 승인·거부면 카드 닫고 승인 목록 반환. 원본: 스파이크 port | 황승주 | 완료 |
| GW-04 | run_checks | cmds, before_direct, states, specs, op, plays, injections, t_ms | (states, passed, blocks, new_reports) | 통과·차단 분리, 차단마다 command_blocked 카드, 막힌 직접 조종 기체 상태 복원. 원본: 스파이크 port | 황승주 | 완료 |
| GW-05 | track_assignments | assignments, before, states, t_ms, reason | list[Assignment] | 바뀐 기체만 새 배정(플레이·시각·사유). 원본: 스파이크 port | 황승주 | 완료 |
| GW-06 | build_frame_v2 | EngineState, log | Frame | 예시 frame.json과 같은 모양, 직렬화 테스트. 원본: 스파이크 port | 최동호 | 예정 |
| GW-07 | tick_log | Scenario, t_ms, dt_ms, TickInputs, blocks | list[str] | 사건·결정·전환·직접 조종·차단 줄 각 1테스트. 원본: 스파이크 port | 황승주 | 완료 |
| GW-08 | check_saved_play | Play, Scenario | PlayCheck | 없는 플레이를 가리키는 선택지, 선택지로 받는 기체의 영역 불일치를 잡음, 데모 플레이는 통과, 같은 오류 중복 없음 | kth9245 | 완료 |
