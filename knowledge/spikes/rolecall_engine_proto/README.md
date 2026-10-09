# ROLECALL 엔진 스파이크 (대회 전 사전 준비분)

**대회 전 사전 준비분이므로 제출 설명에 밝힌다.** 모듈 코드가 아니다. 10/10에 `new_action.py`로 만든 액션에 함수 단위로 옮겨 쓴다(아래 표).

2026-10-09 밤 두 층 구조(결정 0015·0016: 플레이 = 기체 하나의 워크플로우, 작전 = 기체들의 플레이 묶음)로 다시 썼다(Part1-16). 데이터는 실제 계약 `contracts.models`와 시연 시나리오 `demo/scenarios/baengnyeong_night.json`을 그대로 쓰고, 함수 이름·서명은 `contracts/API.md` 3절을 따른다. 옛 역할 기반 판(`models09.py`)은 git 이력에만 있다.

| 파일·함수 | 옮길 곳 |
|---|---|
| `step_vehicle.py` `step_vehicle` | runtime Part2-10 (RT-01) |
| `step_vehicle.py` `expand_action`(표) | play Part3-7 (PLY-07) |
| `engine_proto.py` `apply_events` | sim Part2-5 (SIM-09) |
| `engine_proto.py` `observe` | sensing Part2-6 (SNS-02) |
| `engine_proto.py` `advance` | sim Part2-1~2-4 (SIM-05~08) |
| `engine_proto.py` `apply_decision`·`apply_injection`·`apply_direct`·`apply_emergency`·`apply_reserves`·`update_metrics` | runtime Part2-12·2-14·2-15·2-16·2-11·2-13 |
| `engine_proto.py` `return_feasible`·`check_command`, `geo.py` `point_in_polygon` | safety Part2-8·2-9·2-7 |
| `engine_proto.py` `EngineState`·`init_state`·`tick` | gateway `engine.py` Part2-17 |
| `engine_proto.py` `Operator` | 옮기지 않음(화면 대신 누르는 대본). gateway REST가 같은 입력을 만든다 |

실행: `uv run python knowledge/spikes/rolecall_engine_proto/engine_proto.py`. 검사: `uv run pytest tests/test_spike_script.py`(35분 대본의 사건 1·2·3·4·6).

결과(2026-10-10 0시): 10,500틱(200ms × 35분) 0.5초. 21:11 보트 출현 → 센서 계산으로 21:16 보고 카드 → 결정 한 번에 기체 4대 플레이 전환 → 21:19 드론 1 배터리 귀환, 예비 드론 3이 감시 플레이를 처음부터(결정 0022) → 기체 공백 약 2분 44초 → 21:23 보트 분리, 전환 요청·승인, 운용자가 fast1 선택 → 21:31 직접 조종 구역 밖 차단, 대안 통과, 먼 지점 배터리 차단. 차단은 직접 조종 2건뿐이다.

옛 판에서 고친 것: 선회(orbit) 명령을 받으면 표적이 멀어도 원 위로 순간 이동해 이어받기 공백이 생기지 않던 것(이제 먼저 날아간다), 기지에서 대기하는 기체의 배터리가 줄던 것(이제 줄지 않고 `ready` 유지), 감시 플레이의 귀환 step을 예비가 그대로 이어받던 것(결정 0022).
