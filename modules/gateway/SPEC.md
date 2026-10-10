<!-- prefix: GW -->
# gateway SPEC

통합 1 구간(결정 0009): 틱 루프 `engine.py`(`tick`, 호출 순서만)·`engine_state.py`(`EngineState`)와 GW-02~07 액션은 최동호(09 6절 Part2-17·2-18). 원본은 `knowledge/spikes/rolecall_engine_proto/port/modules/gateway/`를 그대로 복사. GW-01 `build_frame`은 레거시 smoke가 쓰므로 통합 1까지 그대로 두고 새 Frame은 GW-06 `build_frame_v2`. REST·WS(`app.py`, Part1-7)는 리드. `engine.py`·`engine_state.py`와 Part1-7의 `live.py`(실행 상태·입력 대기열)는 액션 파일이 아니라 이 표에 행이 없다.

| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| GW-01 | build_frame | t_ms, tracks, assessments, responses | Frame | 계약 Frame 생성 | 리드 | 완료 |
| GW-02 | init_engine | Scenario | EngineState | 기체 home·ready, role_id=op.assign, step=entry, t_ms=started_ms, 배정 작전 배정. 원본: 스파이크 port | 최동호 | 완료 |
| GW-03 | record_injections | injections, reports, requests, t_ms | (injections, reports, new_reports, approved) | pending이면 injection_pending 카드, 승인·거부면 카드 닫고 승인 목록 반환. 원본: 스파이크 port | 황승주 | 완료 |
| GW-04 | run_checks | cmds, before_direct, states, specs, op, roles, injections, t_ms | (states, passed, blocks, new_reports) | 통과·차단 분리, 차단마다 command_blocked 카드, 막힌 직접 조종 기체 상태 복원. 원본: 스파이크 port | 황승주 | 완료 |
| GW-05 | track_assignments | assignments, before, states, t_ms, reason | list[Assignment] | 바뀐 기체만 새 배정(Role·시각·사유). 원본: 스파이크 port | 황승주 | 완료 |
| GW-06 | build_frame_v2 | EngineState, log | Frame | 예시 frame.json과 같은 모양, 직렬화 테스트. 원본: 스파이크 port | 최동호 | 완료 |
| GW-07 | tick_log | Scenario, t_ms, dt_ms, TickInputs, blocks, passed, hits | list[str] | 사건·결정·전환·직접 조종·차단 줄 각 1테스트. 원본: 스파이크 port · 타격 통과·무력화 줄(결정 0033), 적 등장 줄(결정 0032) | 황승주 | 완료 |
| GW-08 | check_saved_role | Role, Scenario | RoleCheck | 없는 Role을 가리키는 선택지, 선택지로 받는 기체의 영역 불일치를 잡음, 데모 Role은 통과, 같은 오류 중복 없음 | kth9245 | 완료 |
| GW-09 | mark_reported | targets, new_reports | list[Target] | target_detected 카드의 표적에 reported_by = 카드 기체, 이미 적힌 표적·다른 카드 종류는 그대로 (결정 0036) | kth9245 | 완료 |
| GW-10 | score_targets | states, specs, targets, watch_points, tick_ms | targets | threat·threat_reasons·rf_detected·threat_accum을 채움. seen_by가 비면 종류 unknown, 무력화된 표적은 그대로 (결정 0039·0040) | 최동호 | 완료 |
| GW-11 | build_object_graph | EngineState, focus | ObjectGraph | fast1에서 카드→결정→타격 명령→기체, 다른 표적을 겨눈 명령은 안 나옴, 차단은 명령에 붙음, 없는 focus는 ValueError (결정 0038) | kth9245 | 완료 |
| GW-12 | identify_targets | targets, t_ms, tick_ms | targets | unknown 종류·미무력화 표적마다 sensing identify_target을 불러 ident_state·ident_confidence·ident_reasons·ident_observed_ms를 쓴다(결정 0056). 다른 표적은 그대로 | 최동호 | 진행중 |
| GW-13 | refresh_strike_cards | reports, states, specs, targets, roles | reports | 열린 unknown 표적 발견 카드의 문구 끝에 식별 줄(상태·신뢰도·이유)을 붙이고, 식별됨이면 타격 가능 기체마다 타격 승인 선택지를 더한다(strike_<id>, 둘 이상이면 strike_all). 식별 전이면 타격 선택지를 모두 뺀다(결정 0056) | 최동호 | 진행중 |
