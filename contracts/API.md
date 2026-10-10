# contracts/API.md — 모듈 사이·화면과 서버 사이 규약 (정본)

데이터 형식의 정본은 `contracts/models/`(pydantic), 규약의 정본은 이 문서다(결정 0017). `docs/research/09` 2·3절과 다르면 이 문서가 맞다. 근거 결정: 0015(두 층), 0016(두 층 세부), 0017(API 규약), 0018(contracts 세부).
import는 `from contracts.models import X`만. 바꾸는 사람은 리드뿐이고, `contracts/models/`를 커밋하면 `check.sh`가 `contracts/schema/`와 `modules/cop-ui/src/contracts.gen.ts`를 다시 만든다.

## 1. 개념 (두 층)

| 이름 | 무엇 | 모델 |
|---|---|---|
| Role | 기체 **한 대**의 워크플로우. step 목록과 첫 step(`entry`). 쓸 수 있는 영역(`domains`) | `Role` |
| step | 행동 하나(`do`) + 탈출 조건(`on`, 앞에서부터 첫 참) + 들어갈 때 카드 한 장(`report`, 선택) | `Step` |
| 선택지 | 보고 카드의 버튼. 누르면 `role_by_vehicle`의 기체들이 각자 그 Role의 첫 step에서 시작 | `Choice` |
| 오퍼레이션(작전) | 임무 틀(`zone`·`vehicle_ids`·`started_ms`) + 시작 Role(`assign`) + 예비(`reserve`) + 전체 전환 버튼(`switches`) | `Operation`, `Switch` |
| 시나리오 | 시연 묶음: 작전 + 기체 제원 + Role 목록 + 사건 대본 + 적 + 섬(육지) 다각형 `land`(결정 0034) | `Scenario` |
| 적 | 대본에 적은 적 하나: 등장 시각(`appear_offset_ms`)·위치(`pos` 또는 `from_enemy`의 현재 위치)·속도 + 따르는 Role. 행동은 `move_to`·`patrol_route`·`hold`, 조건은 `arrived`·`time_elapsed`(`params.sec`)만. runtime·safety를 거치지 않고 sim이 움직인다(결정 0032) | `EnemySpec`, `Scenario.enemies` |
| 온톨로지 | 기체 종류의 is-a 계층(`kinds`, 상위 `is_a`)과 행동 묶음(`groups`). 종류가 더하는 능력(`provides`)을 하위 종류가 물려받는다. 기체는 `kind` 한 줄, `capabilities`·`kind_path`는 로더가 계산(결정 0038). 판정은 닫힌 세계(계층 어디에도 없으면 못 함) | `Ontology`, `Scenario.ontology`, `VehicleSpec.kind` |

Role은 다른 기체를 알지 못하지만, 선택지의 `role_by_vehicle`은 기체 id를 직접 적는다(결정 0016, 사람이 알고 고름).
선택지가 보고한 기체를 `role_by_vehicle`에 넣지 않으면, 그 기체는 같은 Role에서 지금 step의 탈출 `{cond: {kind: operator_choice, params: {choice: <선택지 id>}}, go_step}`으로 넘어간다. 그런 탈출이 없으면 보고 step에 머문다(결정 0031, 편집기 "보고 카드 끼워 넣기"가 이 모양을 넣는다).

**표적이 필요한 행동**(`watch_target`, `approach_target`, `strike_target`)의 `do.params.target`:
- `"nearest"`: step에 들어갈 때 그 기체에서 가장 가까운 표적. 아직 카드가 올라가지 않은 표적(`reported_by` 없음)을 먼저 고르고, 그런 표적이 없으면 전체에서 고른다(결정 0036)
- `"operator"`: 기체에 `target_id`가 있으면 그 표적(결정으로 옮겨진 기체는 카드의 표적, 예비 이어받기는 빠진 기체의 표적, 결정 0036). 없으면 step에 들어갈 때 명령 없이 `target_select` 카드만 낸다(선택지 id = 표적 id, `role_by_vehicle` 비움). 결정이 오면 `VehicleState.target_id`를 정하고 `entered_step=False`로 되돌려 다음 틱에 명령을 낸다
- 그 밖의 문자열: 고정 표적 id

정해진 표적은 `VehicleState.target_id`에 둔다. 명령으로 나갈 때는 `params.target_id`가 된다.

**타격(결정 0033).** 선택지가 기체를 다른 Role로 옮기면 그 기체에 `decision_id`(결정 id)와 `target_id`(카드의 표적)를 적는다. 표적을 지목한 전환(`target_by_vehicle`이 있는 Injection)은 그 기체에 `decision_id` = 그 Injection id(`inj-n`)를 적는다. 운용자가 기체·표적·Role을 골라 누른 것이 그 표적에 대한 결정이다(결정 0058). 전환 버튼·표적 없는 전환·예비 이어받기로 옮긴 기체는 `decision_id`가 없다. `strike_target` step의 명령(`strike`)은 출처 `decision_id`와 params `target`(표적의 현재 위치)을 싣고, safety 규칙 1은 `decision_id` 없는 `strike`를 `no_provenance`로 막는다(규칙 2·3은 `target`으로 그대로). 타격 중 기체가 표적 100 m 안이면 sim이 표적을 무력화(`neutralized_ms`, 속도 0)하고 `target_neutralized` 카드(알림만)를 낸다. 카드 선택지로 옮긴 기체가 기다리던 다른 카드는 같이 닫힌다(지목 전환은 카드를 닫지 않는다).

**발견한 기체가 붙는다(결정 0036).** `target_found` 조건은 지금 step의 행동이 표적 행동(`watch_target`·`approach_target`·`strike_target`, 추적)이면 그 기체의 `target_id` 표적이 센서에 보일 때 참이고, 아니면(순찰·이동·대기) 센서에 보이는 표적 가운데 아직 카드가 올라가지 않은 것(`Target.reported_by`가 없음)이 있을 때만 참이다. 그래서 감시를 넘기고 순찰로 돌아온 기체는 예전 표적을 다시 보고하지 않고 새 배를 찾는다. `target_detected` 카드가 생긴 틱에 gateway `engine.py`가 그 카드의 표적에 `reported_by`(카드를 올린 기체 id)를 적는다. 그래서 같은 구역에 여러 척이 오면 두 번째 기체는 이미 카드가 올라간 배가 아니라 새 배에 붙어 카드를 올린다. 예비 이어받기(`apply_reserves`)는 빠진 기체의 `target_id`를 예비 기체에 넘긴다.

**경로(결정 0044·0045).** `Scenario.routes`는 편집기가 "경로 비행" 카드에 내놓는 이름 붙은 경로다. `RouteDef`는 `points`(고정 좌표) 또는 `offsets`(카드에 들어가는 순간의 기체 위치에서 북·동 m) 중 하나를 가진다. 카드에는 고른 경로를 복사한다: `move_to`·`patrol_route`의 params `{route: GeoPoint[], route_name}` 또는 `{offsets: RouteOffset[], route_name}`. `patrol_route`는 반복, `move_to`는 한 번 따라가 마지막 점에서 `arrived`. 점 하나 `move_to {target}`는 그대로. runtime `route_command`가 진입 때 offsets를 실제 좌표 route로 바꾸고, 경로를 가진 `move_to`는 `follow_route`(`params.loop: false`)로 낸다. 조건 `at_time`(`params.offset_ms`)은 작전 시작 후 그 시간이 지나면 성립한다(`time_elapsed`는 적 대본의 "카드 시작 후 `sec`").

## 2. 시간·단위·id

- 모든 `t_ms`는 UTC epoch 밀리초다. 예외는 `ScenarioEvent.offset_ms` 하나로, 작전 시작 후 밀리초다. 사건 시각은 `operation.started_ms + offset_ms`다. 시나리오의 `started_ms`가 비면 `load_scenario_json`이 ValueError를 낸다(결정 0018).
- 사람이 보는 시각은 KST로 표시한다(결정 0012). 좌표는 WGS84 도, 거리는 m, 속도는 m/s다.
- id는 무작위 uuid를 쓰지 않는다. 엔진이 만드는 것은 `cmd-<기체>-<t_ms>`, `rep-<기체>-<t_ms>`이고, 같은 틱 둘째부터 `-2`를 붙인다. 서버가 받는 입력은 `dec-1`, `dir-1`, `inj-1` 순번이다. 같은 seed면 같은 Frame 열이 나와야 한다.
- 지표 정의는 09 문서 2.3을 따른다. 단 09 문서의 옛 역할(role) 개념이 없어져서(지금의 Role과 다름) `role_gap_ms`는 `vehicle_gap_ms`가 되었다. 기체가 빠진 틱부터, 예비 기체가 그 step의 목적에 닿은 틱까지 잰다. 목적은 행동 종류마다 다음과 같다.
  - `watch_target`·`approach_target`: 그 기체가 어느 표적의 `seen_by`에 든 틱
  - `move_to`·`patrol_route`: `waypoint_idx`가 -1 또는 1 이상이 된 틱
  - 그 밖의 행동: 첫 PassedCommand가 나온 틱
- `mission_success`: 표적 하나라도 무력화되면 참(결정 0033).

## 3. 틱 한 번 (gateway `engine.py`, 호출 순서만)

`tick(state: EngineState, inputs: TickInputs) -> (EngineState, Frame)`. `EngineState`는 `modules/gateway/engine_state.py`의 dataclass로 계약이 아니다. 운용자 입력 기록·하한선 검사 묶음·배정 갱신·기록 줄·Frame 만들기는 gateway 액션 GW-02~07이 하고 `tick`은 호출 순서만 둔다. 동작하는 원본은 `knowledge/spikes/rolecall_engine_proto/port/modules/`. 칸은 t_ms, scenario, specs, roles, states, targets, reports, assignments, blocks, injections, metrics, run이고, `GET /graph`용 기록 decisions·commands(통과·차단 모두)·passed가 틱마다 쌓인다(결정 0038).

| 순서 | 모듈 | 함수 |
|---|---|---|
| 1 | sim | `apply_events(scenario, states, targets, t_ms, dt_ms) -> (states, targets)` |
| 1.5 | sim | 적(결정 0032): `spawn_enemies(scenario, targets, t_ms, dt_ms) -> targets`, `steer_enemies(enemies, roles, targets, t_ms, dt_ms, land) -> targets`(배는 섬을 돌아감, 결정 0034) |
| 1.6 | sim | `update_emission(scenario, targets, t_ms) -> targets`: 적이 `appear_offset_ms + emit_start_offset_ms`부터 `emitting`(결정 0039) |
| 2 | sensing | `observe(states, specs, targets, t_ms) -> targets`. 본 틱에 `last_seen_pos`·`last_seen_vel_east_mps`·`last_seen_vel_north_mps`도 그때 값으로(놓친 표적은 화면이 마지막 위치와 그때 움직임으로 그림, 결정 0047) |
| 2.5 | gateway | `score_targets(states, specs, targets, watch_points, tick_ms) -> targets`: sensing `score_target`으로 `threat`·`threat_reasons`·`rf_detected`·`threat_accum`을 씀. 종류는 `seen_by`가 비면 unknown(결정 0039·0040) |
| 3 | runtime | 입력 적용: `apply_decision(states, roles, decision, reports) -> (states, reports)`, 승인된 것만 `apply_injection(states, roles, injection) -> states`, `apply_direct(states, direct, t_ms) -> (states, Command)` |
| 4 | runtime | `apply_emergency(states, roles) -> states` |
| 5 | runtime | 기체마다 `step_vehicle(state, specs[id], roles[state.role_id], targets, t_ms, started_ms=op.started_ms) -> (state, Command \| None, Report \| None)` |
| 5.1 | gateway | 그 기체가 카드를 냈으면 바로 `mark_reported(targets, [report]) -> targets`: `target_detected` 카드의 표적에 `reported_by`(결정 0036). 다음 기체는 같은 틱에도 그 배를 새 접촉으로 보지 않는다 |
| 5.15 | runtime | 순찰 보고 흐름 밖 기체가 본 새 적: `spot_reports(states, targets, roles, op, specs, land, t_ms) -> list[Report]`로 그 기체 이름의 발견 카드("새 적 탐지"), 그 기체는 하던 일 계속, 선택지는 표적용 전환 → 기지 대기 드론 감시(결정 0057). 그 카드도 `mark_reported`. |
| 5.2 | runtime | 새로 나온 `target_detected` 카드의 선택지를 `fleet_choices(report, states, op, roles) -> Report`로 만든다: 카드에 정해진 선택지가 있으면 그것을 앞에 두고 "발생 지역 순찰"·"함께 감시"를 덧붙인다(결정 0046, RT-11) |
| 5.3 | runtime | 열려 있는(`resolved_ms` 없음) `target_detected` 카드의 선택지를 매 틱 `fleet_choices`로 다시 만든다. 자기 카드가 열린 드론은 후보에서 빠진다(결정 0046) |
| 6 | runtime | `apply_reserves(states, op, roles, assignments, t_ms) -> (states, assignments, Report \| None)` |
| 7 | safety | 명령마다 `check_command(cmd, state, spec, op, roles, injections) -> PassedCommand \| Block` |
| 8 | sim | `advance(states, specs, passed, dt_ms, targets, land) -> states`(해상 기체는 섬을 돌아감, 결정 0034) |
| 8.5 | sim | `resolve_strikes(states, targets, t_ms) -> (targets, list[Report])`(결정 0033) |
| 9 | runtime | `update_metrics(metrics, outcome: TickOutcome) -> Metrics` |
| 10 | gateway | `build_frame(state, log) -> Frame` |

공통 형식: `specs: dict[기체 id, VehicleSpec]`, `roles: dict[Role id, Role]`, `states: list[VehicleState]`.
작전 시작(`/run/reset`) 상태: 모든 기체는 home 위치, `ready` 상태, `role_id = op.assign.get(id)`, `step_id`는 그 Role의 `entry`, `entered_step=False`, `t_ms = op.started_ms`이고, 배정 사유는 "작전 배정"이다.

**그 밖의 공개 API**
- sim: `load_scenario_json(path) -> Scenario`. 레거시 `load_scenario`·`simulate`는 통합 1까지 그대로 둔다. `sea_aim(pos, goal, land) -> GeoPoint`(결정 0034): 해상 기체(domain sea)와 적 배(boat·fast_boat)는 직선이 `Scenario.land`를 지나면 섬 모서리(바다 쪽 100 m)를 돌아가고, 목표가 육지 안이면 해안에서 50 m 바다 점까지 간다. 시나리오에 `ontology`가 있으면 `kind`가 있는 기체의 `capabilities`·`kind_path`를 계층에서 채운다(결정 0038).
- safety: `point_in_polygon(p, poly) -> bool`, `return_feasible(state, spec, dest) -> (bool, GeoPoint | None)`
- role: `load_role(path) -> Role`, `check_role(role, op, specs) -> RoleCheck`(Role 하나만 본다: step 연결, 보고 지점, 작전 구역, 이 Role을 assign·switches·reserve로 받는 기체의 영역·능력, 귀환 배터리. 다른 Role을 받지 않으므로 선택지가 가리키는 Role의 존재는 보지 않는다), `check_operation(op, roles, specs) -> RoleCheck`(작전 전체: assign·reserve·switches·보고 선택지가 만드는 (기체, Role) 쌍마다 check_role, 없는 Role을 가리키면 `missing_role`. issue 메시지 앞에 `[Role id] `가 붙는다. 결정 0030), `expand_action(action, domain) -> CommandKind | None`, `list_templates() -> list[Role]`, `draft_role(text, op) -> Role`
- mavlink(리드, 결정 0025): `compile_mavlink(role, op, specs) -> dict[기체 id, (plan dict, script str)]`. role 모듈은 `expand_action`만 공개 API로 쓴다. `mavlink_lines(passed, specs) -> list[str]`(통과한 명령 → MAVLink 메시지 줄, `GET /mavlink`, 결정 0064)
- ontology(리드, 결정 0038): `kind_chain(kind, onto) -> list[VehicleKind]`, `explain_capability(kind, action, onto) -> CapabilityReason`, `infer_capabilities(kind, onto) -> list[ActionKind]`, `fill_vehicle_kinds(scenario) -> Scenario`, `ontology_view(scenario) -> OntologyView`
- `PassedCommand`는 `safety.check_command`만 만든다.

## 4. 전환 경로 (결정 0015·0016)

| 경로 | 시작 | 적용 |
|---|---|---|
| 보고 카드 선택지 | `POST /decisions` | 바로 적용한다. 누른 것이 운용자 결정이다(사건 2: 한 번에 기체 4대) |
| 전체 전환 버튼 | `POST /injections {switch_id}` | `Injection(pending)`과 `injection_pending` 카드를 만들고, 승인 뒤 `apply_injection`으로 적용 |
| 일부 전환 | `POST /injections {role_by_vehicle}` | 위와 같다(사건 4: 드론 2를 고속 보트 추적으로) |
| 기체 메뉴 Role 전환 | `POST /injections {role_by_vehicle, approve: true}` | 상황판에서 기체를 누르고 표적 없는 Role을 누른 것. 버튼의 "지금 Role → 새 Role"이 미리 보기이고 누른 것이 승인이라 `Injection(approved)`로 기록하고 대기 카드 없이 다음 틱에 적용한다. 운용자 조작 1(결정 0059) |
| 표적 지목 | `POST /injections {role_by_vehicle, target_by_vehicle, approve: true}` | 상황판에서 기체 → 표적 Role → 포착된 적(또는 기체 → 지도 표적 → Role)을 누른 것. 메뉴가 미리 보기이고 누른 것이 승인이라 `Injection(approved)`로 기록하고 다음 틱에 `apply_injection`이 Role·`target_id`·`decision_id`(= Injection id)를 바꾼다. 그래서 무장 기체의 타격 Role('표적 타격')도 출처 검사를 통과한다. 운용자 조작 1(결정 0048·0049·0058) |

어느 경로든 원래 Role은 끝나고 자동 복귀는 없다. `resume_role_id`·`resume_step_id`는 직접 조종(`/direct`) 뒤 복귀에만 쓴다. 이어받기는 기체가 returning·lost·maintenance가 되면 `op.reserve[id]`의 첫 가용 기체가 그 기체의 Role을 **첫 step(entry)부터** `entered_step=False`로 시작하는 것이다(결정 0022: 빠진 기체는 이미 귀환 step에 있으므로 현재 step을 이어받으면 예비도 귀환한다). 이때 배정 사유는 "예비 투입: <id> 대신"이고 `vehicle_gap` 카드가 생긴다.

## 5. 화면과 서버 (REST, WS)

화면은 엔진 시각을 모르므로 `id`와 `t_ms`는 서버가 붙이고, 입력은 다음 틱의 `TickInputs`에 들어간다.

| 엔드포인트 | 요청 | 응답 |
|---|---|---|
| `GET /roles` · `POST /roles` | — · `Role` | `Role[]` · `RoleCheck` |
| `DELETE /roles/{id}` | — | `Role[]`(남은 Role. 실행 작전에서 지우고 작전 시작 직전 `paused`, 그 Role로 시작하던 기체는 배정 없이 시작, 다른 쓰임은 검사하지 않음, 결정 0050). 없는 id 404 |
| `GET /enemies` | — | `EnemySpec[]`(시나리오의 적, Part1-21) |
| `GET /watch_points` | — | `WatchPoint[]`(시나리오의 기준점, 상황판이 놓친 표적의 접근·이탈을 가름, 결정 0047) |
| `GET /routes` | — | `RouteDef[]`(실행 작전의 경로 목록, 결정 0044) |
| `POST /routes` | `RouteDef`(고정이면 `points`, 상대면 `offsets`) | `RouteDef[]`(실행 작전 경로 목록 끝에 더함, 같은 id는 바꿈. 카드는 고를 때 경로를 복사하므로 실행을 되돌리지 않음. gateway 메모리에만, 결정 0054) |
| `GET /ontology` | — | `OntologyView`(계층 + 기체마다 행동 10개의 판정과 경로, 결정 0038). 시나리오에 온톨로지가 없으면 404 |
| `GET /graph?focus=` | — | `ObjectGraph`(그 객체에서 링크를 따라 모은 객체. 기체와 focus가 아닌 표적은 더 펼치지 않음, 결정 0038). 없는 id는 404 |
| `GET /mavlink` | — | `string[]`(이번 실행에 안전 검사를 통과한 명령을 시간순 MAVLink 메시지 줄로: `HH:MM:SS(KST) 기체 메시지 MAV_CMD이름(번호) p1 … p7`. NAV는 `MISSION_ITEM_INT seq<n>` 줄들 + `MISSION_START`, 그 밖은 `COMMAND_LONG`, 대응 명령이 없는 타격은 줄 없음. 헤더 MAVLink 버튼의 새 창이 1초마다 읽음, 결정 0064) |
| `POST /roles/check` | `Role` | `RoleCheck` |
| `POST /roles/draft` | `DraftIn{text}` | `Role`(origin=ai_draft, approved=false) |
| `GET /operation` · `POST /operation` | — · `Operation` | `Operation` |
| `GET /vehicles` | — | `VehicleSpec[]`(시나리오의 기체 제원·출발 위치, Part3-14 작전 패널) |
| `GET /scenarios` | — | `ScenarioInfo[]`(gateway가 켤 때 읽은 시연 작전, 실행 작전은 `active`, 결정 0042) |
| `POST /scenarios/{id}/activate` | — | `RunState`(그 작전을 실행 작전으로, 작전 시작 직전 `paused`). 없는 id 404 |
| `POST /scenarios` | `NewOperationIn{name, purpose}` | `ScenarioInfo[]`(실행 작전과 같은 지도·기체·Role 목록·경로·온톨로지로 빈 작전 `new_op_<n>`을 만들어 실행 작전으로, 작전 시작 직전 `paused`. 시작 배정·예비·전환 버튼·교대·적·대본 사건은 비우고 적의 Role은 빼며, gateway 메모리에만 있음, 결정 0053). 시작 Role은 `POST /operation`으로 바꾼다 |
| `POST /run/live?speed=` · `POST /run/reset` · `POST /run/jump?offset_ms=` | — | `RunState` |
| `POST /decisions` | `DecisionIn{report_id, choice_id}` | `Accepted{id, t_ms}` |
| `POST /direct` | `DirectIn{vehicle_id, target}` | `Accepted` |
| `POST /injections` | `SwitchIn{switch_id}` 또는 `SwitchIn{role_by_vehicle, target_by_vehicle?, approve?}` | `Injection`(pending, `approve`면 approved). 라벨은 "<Role>: <기체>"이고 표적이 있으면 " → <표적>" |
| `POST /injections/{id}/approve` · `.../reject` | — | `Injection` |
| WS `/ws` | — | 0.2초마다 `Frame` 하나. 배속 n이면 틱 n개를 돌리고 마지막 Frame만 보낸다. 실행 상태는 `Frame.run{status, speed}` |

`POST /roles/check`와 `POST /roles`의 검사는 `check_role`에 "이 Role로 바꾸면 `check_operation`에 새로 생기는 오류"를 더한 것이다(gateway GW-08 `check_saved_role`). `POST /roles`는 검사를 통과할 때만 gateway 메모리의 Role 목록에 저장하고(같은 id는 제자리 교체, 새 id는 뒤에 추가) 실행을 작전 시작 직전(`paused`)으로 되돌린다. 저장한 Role은 그다음 작전 시작에 쓰인다. 파일에는 쓰지 않아 gateway를 다시 켜면 시나리오 원본으로 돌아간다. 실패면 아무것도 바꾸지 않는다. 둘 다 응답은 항상 `RoleCheck`다(결정 0030).

`GET /scenarios`는 gateway가 켤 때 읽은 시연 작전 목록이다(`baengnyeong_night`, `baengnyeong_24h`. 처음 실행 작전은 `KDTH_SCENARIO`, 목록에 없는 파일이면 맨 앞에 붙는다). `POST /scenarios/{id}/activate`는 지금 실행 작전(저장한 Role·작전 수정 포함)을 메모리 목록에 남겨 두고 그 작전으로 바꾼 뒤 `/run/reset`처럼 작전 시작 직전(`paused`)으로 되돌린다. 나머지 엔드포인트와 `/ws`는 바뀐 실행 작전을 쓴다(결정 0042).

`/run/live?speed=0`은 일시정지다. `status`는 `paused`가 되고 `speed`는 멈추기 전 배속을 그대로 둔다(결정 0026). `/run/reset` 뒤에는 `paused`이고, 빈 입력으로 틱 하나를 돌려 첫 Frame을 만든다. WS Frame의 `log`는 그 연결에 아직 보내지 않은 기록 줄 전부다(배속으로 돈 틱들의 줄을 모두 담고, 일시정지 중에는 빈 목록, 새 연결의 첫 Frame은 reset 뒤 전부). 전환 요청이 아직 틱에 들어가기 전에 승인·거부가 오면 서버가 그 판정을 한 틱 뒤에 넣는다. 서버는 `gateway`를 `uvicorn modules.gateway.app:create_app --factory`로 띄운다.

오류 응답은 다음과 같다. 형식이 틀리면 400, 없는 id는 404, 상태 충돌(이미 처리된 보고, pending이 아닌 주입)은 409이고, 본문은 FastAPI 기본 `{"detail": "..."}`다.

## 6. 예시와 스텁

- `contracts/examples/<모델 snake_case>.json`: 모델마다 하나씩 있다. `contracts/examples/frames/`에는 3분 대본의 8장면이 있다(`s1_report_wait`, `s2_after_decision`, `s3_takeover`, `s4_switch_pending`, `s5_zone_block`, `s6_battery_block`, `s7_strike_approval`, `s8_neutralized`; 시각 순서는 s1 s2 s3 s5 s6 s4 s7 s8, 결정 0033). `frame.json`은 s1과 같다. 모두 한 세계(기체 d1·d2·d3·usv·ugv, 작전 op1, 표적 boat1·fast1)에서 나왔다.
- 다시 만드는 명령은 `uv run python scripts/gen_examples.py`이다. 세계는 시연 시나리오 `demo/scenarios/baengnyeong_night.json`을 `scripts/example_world.py`가 읽은 것이고(결정 0035, 시나리오는 JSON을 손으로 고친다), 장면은 `scripts/example_scenes.py`에 있다. 위치는 손으로 계산한 근사값이다. `gen_examples.py`는 `demo/`를 쓰지 않는다.
- 아직 없는 함수의 스텁은 이 예시를 돌려준다(09 4.5). 통합 2(00:00) 전에 걷어낸다.
- 레거시 T1-3 모델(`Detection`·`Track`·`Assessment`·`Response`·`LegacyFrame`)은 지금 gateway·smoke가 쓰고 있다. 통합 1 뒤 smoke를 새 엔진으로 바꿀 때 뺀다(Part1-14).

## 해안 순찰 교대(결정 0037)
- `VehicleSpec.recharge_min`(0 = 충전 없음): 기지에서 `maintenance`인 동안 배터리가 `100/recharge_min`%/분씩 차고 100%면 `ready`.
- `Operation.rotation`(교대 기체)·`rotation_roles`(늘 지키는 순찰 Role): 비면 교대 없음.
- `Operation.rotation_pools`(순찰 Role → 그 해안을 서로 교대하는 드론들, 예: 북 d1·d3 / 남 d2·d4): 있으면 교대·빈 해안 채우기는 그 짝 안에서만. 비면 `rotation` 전체에서.
- `ReportSpec.auto_choices`: 해안 순찰 발견 카드는 runtime `fleet_choices`가 그때 함대로 선택지를 만든다(다른 드론마다 발생 지역 순찰·감시 드론과 함께 감시, 그리고 유지). `Choice.target_by_vehicle`: 그 선택으로 옮긴 기체가 감시할 표적.
- 틱 순서 4.6: `rotate_patrols` 다음 `relieve_hover`(감시 드론 교대). 5.2: `step_vehicle`이 만든 카드에 `fleet_choices`.
- 틱 순서 4.5: `apply_emergency`(4) 다음, `step_vehicle`(5) 전에 runtime `rotate_patrols`.
