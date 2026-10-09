# contracts/API.md — 모듈 사이·화면과 서버 사이 규약 (정본)

데이터 형식의 정본은 `contracts/models/`(pydantic), 규약의 정본은 이 문서다(결정 0017). `docs/research/09` 2·3절과 다르면 이 문서가 맞다. 근거 결정: 0015(두 층), 0016(두 층 세부), 0017(API 규약), 0018(contracts 세부).
import는 `from contracts.models import X`만. 바꾸는 사람은 리드뿐이고, `contracts/models/`를 커밋하면 `check.sh`가 `contracts/schema/`와 `modules/cop-ui/src/contracts.gen.ts`를 다시 만든다.

## 1. 개념 (두 층)

| 이름 | 무엇 | 모델 |
|---|---|---|
| 플레이 | 기체 **한 대**의 워크플로우. step 목록과 첫 step(`entry`). 쓸 수 있는 영역(`domains`) | `Play` |
| step | 행동 하나(`do`) + 탈출 조건(`on`, 앞에서부터 첫 참) + 들어갈 때 카드 한 장(`report`, 선택) | `Step` |
| 선택지 | 보고 카드의 버튼. 누르면 `play_by_vehicle`의 기체들이 각자 그 플레이의 첫 step에서 시작 | `Choice` |
| 오퍼레이션(작전) | 임무 틀(`zone`·`vehicle_ids`·`started_ms`) + 시작 플레이(`assign`) + 예비(`reserve`) + 전체 전환 버튼(`switches`) | `Operation`, `Switch` |
| 시나리오 | 시연 묶음: 작전 + 기체 제원 + 플레이 목록 + 사건 대본 | `Scenario` |

플레이는 다른 기체를 알지 못하지만, 선택지의 `play_by_vehicle`은 기체 id를 직접 적는다(결정 0016, 사람이 알고 고름).

**표적이 필요한 행동**(`watch_target`, `approach_target`)의 `do.params.target`:
- `"nearest"`: step에 들어갈 때 그 기체에서 가장 가까운 표적
- `"operator"`: step에 들어갈 때 명령 없이 `target_select` 카드만 낸다(선택지 id = 표적 id, `play_by_vehicle` 비움). 결정이 오면 `VehicleState.target_id`를 정하고 `entered_step=False`로 되돌려 다음 틱에 명령을 낸다
- 그 밖의 문자열: 고정 표적 id

정해진 표적은 `VehicleState.target_id`에 둔다. 명령으로 나갈 때는 `params.target_id`가 된다.

## 2. 시간·단위·id

- 모든 `t_ms`는 UTC epoch 밀리초다. 예외는 `ScenarioEvent.offset_ms` 하나로, 작전 시작 후 밀리초다. 사건 시각은 `operation.started_ms + offset_ms`다. 시나리오의 `started_ms`가 비면 `load_scenario_json`이 ValueError를 낸다(결정 0018).
- 사람이 보는 시각은 KST로 표시한다(결정 0012). 좌표는 WGS84 도, 거리는 m, 속도는 m/s다.
- id는 무작위 uuid를 쓰지 않는다. 엔진이 만드는 것은 `cmd-<기체>-<t_ms>`, `rep-<기체>-<t_ms>`이고, 같은 틱 둘째부터 `-2`를 붙인다. 서버가 받는 입력은 `dec-1`, `dir-1`, `inj-1` 순번이다. 같은 seed면 같은 Frame 열이 나와야 한다.
- 지표 정의는 09 문서 2.3을 따른다. 단 역할이 없어져서 `role_gap_ms`는 `vehicle_gap_ms`가 되었다. 기체가 빠진 틱부터, 예비 기체가 그 step의 목적에 닿은 틱까지 잰다. 목적은 행동 종류마다 다음과 같다.
  - `watch_target`·`approach_target`: 그 기체가 어느 표적의 `seen_by`에 든 틱
  - `move_to`·`patrol_route`: `waypoint_idx`가 -1 또는 1 이상이 된 틱
  - 그 밖의 행동: 첫 PassedCommand가 나온 틱

## 3. 틱 한 번 (gateway `engine.py`, 호출 순서만)

`tick(state: EngineState, inputs: TickInputs) -> (EngineState, Frame)`. `EngineState`는 engine.py 안의 dataclass로 계약이 아니다. 칸은 t_ms, scenario, specs, plays, states, targets, reports, assignments, blocks, injections, metrics, run이다.

| 순서 | 모듈 | 함수 |
|---|---|---|
| 1 | sim | `apply_events(scenario, states, targets, t_ms, dt_ms) -> (states, targets)` |
| 2 | sensing | `observe(states, specs, targets, t_ms) -> targets` |
| 3 | runtime | 입력 적용: `apply_decision(states, plays, decision, reports) -> (states, reports)`, 승인된 것만 `apply_injection(states, plays, injection) -> states`, `apply_direct(states, direct, t_ms) -> (states, Command)` |
| 4 | runtime | `apply_emergency(states, plays) -> states` |
| 5 | runtime | 기체마다 `step_vehicle(state, specs[id], plays[state.play_id], targets, t_ms) -> (state, Command \| None, Report \| None)` |
| 6 | runtime | `apply_reserves(states, op, assignments, t_ms) -> (states, assignments, Report \| None)` |
| 7 | safety | 명령마다 `check_command(cmd, state, spec, op, plays, injections) -> PassedCommand \| Block` |
| 8 | sim | `advance(states, specs, passed, dt_ms, targets) -> states` |
| 9 | runtime | `update_metrics(metrics, outcome: TickOutcome) -> Metrics` |
| 10 | gateway | `build_frame(state, log) -> Frame` |

공통 형식: `specs: dict[기체 id, VehicleSpec]`, `plays: dict[플레이 id, Play]`, `states: list[VehicleState]`.
작전 시작(`/run/reset`) 상태: 모든 기체는 home 위치, `ready` 상태, `play_id = op.assign.get(id)`, `step_id`는 그 플레이의 `entry`, `entered_step=False`, `t_ms = op.started_ms`이고, 배정 사유는 "작전 배정"이다.

**그 밖의 공개 API**
- sim: `load_scenario_json(path) -> Scenario`. 레거시 `load_scenario`·`simulate`는 통합 1까지 그대로 둔다.
- safety: `point_in_polygon(p, poly) -> bool`, `return_feasible(state, spec, dest) -> (bool, GeoPoint | None)`
- play: `load_play(path) -> Play`, `check_play(play, op, specs) -> PlayCheck`(step 연결, `play_by_vehicle`의 플레이 존재), `check_operation(op, plays, specs) -> PlayCheck`(보고·승인 지점, 귀환 배터리, 작전 구역), `expand_action(action, domain) -> CommandKind | None`, `list_templates() -> list[Play]`, `draft_play(text, op) -> Play`, `compile_mavlink(play, op, specs) -> dict[기체 id, (plan dict, script str)]`
- `PassedCommand`는 `safety.check_command`만 만든다.

## 4. 전환 세 경로 (결정 0015·0016)

| 경로 | 시작 | 적용 |
|---|---|---|
| 보고 카드 선택지 | `POST /decisions` | 바로 적용한다. 누른 것이 운용자 결정이다(사건 2: 한 번에 기체 4대) |
| 전체 전환 버튼 | `POST /injections {switch_id}` | `Injection(pending)`과 `injection_pending` 카드를 만들고, 승인 뒤 `apply_injection`으로 적용 |
| 일부 전환 | `POST /injections {play_by_vehicle}` | 위와 같다(사건 4: 드론 2를 고속 보트 추적으로) |

어느 경로든 원래 플레이는 끝나고 자동 복귀는 없다. `resume_play_id`·`resume_step_id`는 직접 조종(`/direct`) 뒤 복귀에만 쓴다. 이어받기는 기체가 returning·lost·maintenance가 되면 `op.reserve[id]`의 첫 가용 기체가 그 기체의 플레이와 현재 step을 `entered_step=False`로 이어받는 것이다. 이때 배정 사유는 "예비 투입: <id> 대신"이고 `vehicle_gap` 카드가 생긴다.

## 5. 화면과 서버 (REST, WS)

화면은 엔진 시각을 모르므로 `id`와 `t_ms`는 서버가 붙이고, 입력은 다음 틱의 `TickInputs`에 들어간다.

| 엔드포인트 | 요청 | 응답 |
|---|---|---|
| `GET /plays` · `POST /plays` | — · `Play` | `Play[]` · `PlayCheck` |
| `POST /plays/check` | `Play` | `PlayCheck` |
| `POST /plays/draft` | `DraftIn{text}` | `Play`(origin=ai_draft, approved=false) |
| `GET /operation` · `POST /operation` | — · `Operation` | `Operation` |
| `POST /run/live?speed=` · `POST /run/reset` · `POST /run/jump?offset_ms=` | — | `RunState` |
| `POST /decisions` | `DecisionIn{report_id, choice_id}` | `Accepted{id, t_ms}` |
| `POST /direct` | `DirectIn{vehicle_id, target}` | `Accepted` |
| `POST /injections` | `SwitchIn{switch_id}` 또는 `SwitchIn{play_by_vehicle}` | `Injection`(pending) |
| `POST /injections/{id}/approve` · `.../reject` | — | `Injection` |
| WS `/ws` | — | 0.2초마다 `Frame` 하나. 배속 n이면 틱 n개를 돌리고 마지막 Frame만 보낸다. 실행 상태는 `Frame.run{status, speed}` |

오류 응답은 다음과 같다. 형식이 틀리면 400, 없는 id는 404, 상태 충돌(이미 처리된 보고, pending이 아닌 주입)은 409이고, 본문은 FastAPI 기본 `{"detail": "..."}`다.

## 6. 예시와 스텁

- `contracts/examples/<모델 snake_case>.json`: 모델마다 하나씩 있다. `contracts/examples/frames/`에는 3분 대본의 6장면이 있다(`s1_report_wait`, `s2_after_decision`, `s3_takeover`, `s4_switch_pending`, `s5_zone_block`, `s6_battery_block`). `frame.json`은 s1과 같다. 모두 한 세계(기체 d1·d2·d3·usv·ugv, 작전 op1, 표적 boat1·fast1)에서 나왔다.
- 다시 만드는 명령은 `uv run python scripts/gen_examples.py`이다. 세계 데이터는 `scripts/example_world.py`, 장면은 `scripts/example_scenes.py`에 있다. 위치는 손으로 계산한 근사값이다.
- 아직 없는 함수의 스텁은 이 예시를 돌려준다(09 4.5). 통합 2(00:00) 전에 걷어낸다.
- 레거시 T1-3 모델(`Detection`·`Track`·`Assessment`·`Response`·`LegacyFrame`)은 지금 gateway·smoke가 쓰고 있다. 통합 1 뒤 smoke를 새 엔진으로 바꿀 때 뺀다(Part1-14).
