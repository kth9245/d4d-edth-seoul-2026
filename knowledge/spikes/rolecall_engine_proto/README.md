# ROLECALL 엔진 스파이크 (대회 전 사전 준비분)

**대회 전 사전 준비분이므로 제출 설명에 밝힌다.** 2026-10-10 0시 devil-advocate 검토 뒤, 내일 그대로 복사할 수 있는 모양으로 다시 나눴다(Part1-17).

## 무엇이 있나

- `port/modules/<모듈>/...` — 저장소 `modules/`와 **같은 경로·같은 import**. 액션 파일 하나 = SPEC.md 행 하나, ruff 포맷 끝(줄 길이 100), 액션마다 80줄 이하(가장 긴 것 65줄). `engine.py`는 호출 순서만.
- `run_script.py` — 이식 파일로 시연 시나리오(`demo/scenarios/baengnyeong_night.json`)의 35분 대본을 돌린다. `Operator`는 화면 대신 버튼을 누르는 대본이라 옮기지 않는다.
- 검사: `uv run pytest tests/test_spike_script.py` — 사건 1·2·3·4·6이 대본대로 나오는지, 그리고 이식 파일이 액션 규칙(80줄·공개 함수 이름·SPEC 행)·포맷·모듈 경계를 지키는지.

실행: `PYTHONPATH=knowledge/spikes/rolecall_engine_proto/port:. uv run python knowledge/spikes/rolecall_engine_proto/run_script.py`

## 옮기는 법 (내일)

1. `uv run python scripts/new_action.py <모듈> <액션>`으로 `예정` 행을 가져간다(파일·실패 테스트가 생김).
2. 생긴 액션 파일 내용을 `port/modules/<모듈>/actions/<액션>.py`로 바꾼다. 경로·import가 같아 그대로 동작한다.
3. 실패 테스트를 진짜 테스트로 바꾼다(TDD는 테스트부터, 결정 0014). happy path만(결정 0024).
4. `__init__.py`는 `port`의 것을 보고 새 이름만 **추가**한다(sim·sensing·gateway의 레거시 이름은 통합 1까지 그대로).

| 모듈 | 파일 (SPEC 행) | 담당 |
|---|---|---|
| sim | load_scenario_json(SIM-04), move_straight(05), follow_route(06), orbit_or_keep(07), advance_vehicles(08), apply_events(09) | 최동호 |
| sensing | observe_targets(SNS-02) | 최동호 |
| gateway | engine.py, engine_state.py, init_engine(GW-02), record_injections(03), run_checks(04), track_assignments(05), build_frame_v2(06), tick_log(07) | 최동호 |
| safety | point_in_polygon(SFT-01), return_feasible(02), check_command(03) | 황승주 |
| runtime | step_vehicle(RT-01), apply_reserves(02), apply_decision(03), update_metrics(04), apply_injection(05), apply_direct(06), apply_emergency(07), enter_step(08), switch_role(09) | 황승주 |
| role | expand_action(PLY-07) | 황승주 |

거리·좌표 계산은 `shared/geo.py`(`dist_m`, `lerp`, `move_toward`, `offset_latlon`)를 쓴다.

## 결과 (2026-10-10 0시)

10,500틱(200ms × 35분) 0.7초. 21:11 보트 출현 → 센서 계산으로 21:16 보고 카드 → 결정 한 번에 기체 4대 Role 전환 → 21:19 드론 1 배터리 귀환, 예비 드론 3이 감시 Role을 처음부터(결정 0022), 기체 공백 약 2분 43초 → 21:23 보트 분리, 전환 요청·승인, 운용자가 fast1 선택 → 21:31 직접 조종 구역 밖 차단, 대안 통과, 먼 지점 배터리 차단. 차단은 직접 조종 2건뿐.

옛 판에서 고친 것: 선회 명령에서 원 위로 순간 이동하던 것(이제 먼저 날아감), 기지 대기 중 배터리가 줄던 것, 예비가 귀환 step을 이어받던 것(결정 0022), step_vehicle 한 함수가 포맷 뒤 114줄이던 것(enter_step으로 나눔), 틱 루프 안의 계산(gateway 액션으로 뺌).
