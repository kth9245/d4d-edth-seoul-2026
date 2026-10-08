# ROLECALL 구현 토대 — 데이터 형식(확정 수준), 모듈별 목표·방향, 통합 기준

정리일 2026-10-09. 결정 0003(아이디어 수정 방향)·0004(시나리오·장소)·0005(대본·계산·캐시의 선)를 구현으로 옮기는 기준 문서. 계획 문서 08의 6절(시스템 구조)·7절(역할 분담)을 대체한다. 액션 목록은 여기 없다. 액션은 10/10 사이클 시작 때 각자 `new_action.py`로 만든다.

**2026-10-09 밤 devil-advocate 검토 반영(10절).** 검토에서 2절 형식이 그대로는 시뮬레이션되지 않는 것이 확인돼(기체가 첫 틱 뒤 멈춤) 필드 3개를 고쳤고, 두 모드 재실행·미리 보기 경로·영역 제한 이어받기를 뺐다. 검증에 쓴 스파이크는 `knowledge/spikes/rolecall_engine_proto/`(대회 전 사전 준비분, 제출 설명에 밝힌다).

이 문서의 데이터 형식은 "v1 초안"이 아니다. 10/9 밤 리드가 `contracts/models/`에 옮기고, 10/10 12:00 형식 고정 때 검토만 한다. 바꿔야 하면 리드가 contracts 브랜치에서 바꾸고 팀에 알린다.

---

## 1. 한 장 구조

```
cop-ui (React)  ──REST/WS──  gateway (FastAPI)  ──호출──  engine.tick()
  editor / setup                                            │
  live (상황판)                                   ┌─────────┴──────────┐
                                                  sim → sensing → runtime → safety → frame
                                                  ↑                              │
                                                  └──── PassedCommand 만 받음 ────┘
play (검사·펼치기·AI 초안)  ── 저장된 Play JSON ──→ runtime
```

- **엔진 하나.** `engine.tick(state, inputs) -> (state, frame)`는 순수 함수. 실행 경로는 `/run/live` 하나이고 `speed`(배속)만 다르다. 1배속은 0.2초마다 틱 하나, 15배속은 0.2초마다 틱 15개를 돌리고 마지막 Frame만 보낸다. "미리 보기"는 같은 경로를 배속으로 돌리는 것이다(엔진이 결정적이므로 같은 seed면 같은 결과). 끝까지 돌려 Frame 목록을 돌려주는 경로는 없다(35분 작전 = Frame 10,500개 ≈ 35MB, 스파이크로 확인).
- **명령의 한 방향 흐름.** runtime이 `Command`를 만들고, safety만 `PassedCommand`를 만들며, sim은 `PassedCommand`만 받는다. 막힌 명령은 `Block`으로 frame에 실린다.
- **명령은 한 번, 수행은 계속.** runtime은 step에 *들어갈 때* 한 번만 `Command`를 낸다(결정 0006 단순형: step = 행동 하나 + 탈출 조건 목록). safety를 통과한 `PassedCommand`는 `VehicleState.active`에 보관되고, sim은 새 명령이 없는 틱에도 `active`를 계속 수행한다(순찰 경로 순회, 선회, 거리 유지). 이 필드가 없으면 기체가 첫 틱 뒤 멈춘다(검토에서 재현: 드론이 기지에서 3m 가고 35분 동안 정지). 명령을 틱마다 다시 내면 `commands_sent`·`manual_baseline_actions`가 초당 5씩 늘어 지표가 무너지므로 금지.
- **상태는 데이터.** 기체별 "지금 어느 플레이·step·줄에 있는가, 무슨 명령을 수행 중인가, 어느 보고의 결정을 기다리는가"를 `VehicleState`에 넣는다. 클래스 상속·콜백 없음. 액션 파일 하나가 틱의 한 단계를 맡는다.
- **파일 저장.** Play·Operation·Scenario는 JSON 파일(`demo/scenarios/`, `demo/plays/`). DB 없음.

---

## 2. 데이터 형식 (contracts/models.py, 확정 수준)

단위: 위경도 도(WGS84), 거리 m, 속도 m/s, 시간 UTC epoch ms(`t_ms`). 모든 모델은 pydantic v2. id는 문자열. `contracts.gen.ts`는 자동 생성.

### 2.1 열거형

| 이름 | 값 | 비고 |
|---|---|---|
| `Domain` | air, sea, ground | 기체 영역 |
| `VehicleStatus` | ready, active, returning, maintenance, lost | lost = 통신 두절 |
| `ActionKind` | move_to, patrol_route, search_area, return_home, watch_target, watch_point, approach_target, relay_comms, hold | 9개. step의 행동 하나. 분기·보고·승인은 step의 `on`·`report`로 표현(결정 0006 단순형). AI 초안 어휘이기도 함 |
| `ConditionKind` | target_found, arrived, time_elapsed, battery_below, operator_choice, signal_received | 6개 |
| `CommandKind` | move, orbit, keep_distance, hold, follow_route, zigzag, return_home, relay | 8개. 기체로 나가는 명령 |
| `CommandSource` | play_step, operator_decision, operator_direct, injected_plan, emergency | 출처(하한선 규칙 1) |
| `BlockReason` | no_provenance, outside_zone, battery_insufficient | 하한선 규칙 3개와 1:1 |
| `ReportKind` | target_detected, role_gap, vehicle_lost, battery_low, injection_pending, command_blocked | 상황판 카드 종류 |
| `TargetKind` | boat, fast_boat, person, unknown | 시연용 |
| `EmergencyKind` | link_lost, battery_low, operator_call | 위치 이상은 뺌(결정 0004, GPS 장면 없음) |

(`RunMode`는 검토에서 뺐다. 수동 기준선은 같은 실행 안에서 센다. 2.3 참고.)

### 2.2 모델 (필드 = 이름: 타입 [기본값])

**공간·기체**
- `GeoPoint` — lat: float, lon: float, alt_m: float = 0
- `Polygon` — points: list[GeoPoint] (3개 이상, 닫지 않음)
- `VehicleSpec` — id, name, domain: Domain, speed_mps: float, endurance_min: float, sensor_range_m: float, capabilities: list[ActionKind], home: GeoPoint
- `VehicleState` — id, t_ms, pos: GeoPoint, heading_deg: float, battery_pct: float, status: VehicleStatus, role_id: str|None, play_id: str|None, step_id: str|None, **entered_step: bool = False** (이 step의 `do`를 이미 명령으로 냈는가. 거짓이면 다음 틱에 명령·보고를 한 번 내고 참으로 바꾼다), waypoint_idx: int = 0 (-1 = 현재 명령의 목적지 도착), **active: PassedCommand|None** (sim이 계속 수행하는 현재 명령), **pending_report_id: str|None** (선택지 있는 보고에서 멈춰 Decision을 기다리는 중이면 그 Report id. 이 값이 있으면 runtime은 전이하지 않는다. 없으면 보고가 틱마다 다시 생겨 카드가 수천 장 쌓인다 — 검토에서 재현), emergency: EmergencyKind|None, **resume_play_id: str|None**, resume_step_id: str|None (복귀 지점은 플레이·step 쌍. 주입 뒤 직접 조종이 오면 step id만으로는 어느 플레이인지 모른다)

**작전·플레이**
- `Operation` — id, name, purpose, area: Polygon(표시용 작전 지역), zone: Polygon(작전 구역, 하한선 규칙 2, 상황판에서 수정 불가), vehicle_ids: list[str], started_ms: int|None
- `Role` — id, name, domains: list[Domain], required: list[ActionKind] (이 액션을 못 하는 기체는 검사에서 거부), vehicles: list[str] (주 기체 → 예비 순서. 결정 0005: 배정은 계획 담당이 고정)
- `Condition` — kind: ConditionKind, params: dict[str, float|str]
- `Action` — kind: ActionKind, params: dict[str, Any] (move_to의 target은 GeoPoint dict, patrol_route의 route는 GeoPoint dict 목록, watch_target의 target_id·distance_m. 타입을 `float|str|list`로 두면 목적지가 들어가지 않아 첫 액션부터 ValidationError)
- `Exit` — cond: Condition, go_step: str (조건이 참이 되면 옮겨 갈 step)
- `Choice` — id, label, step_by_role: dict[str, str] (역할 id → 시작할 step id. 결정 한 번이 여러 역할을 움직이는 자리)
- `ReportSpec` — text: str, choices: list[Choice] = [] (choices가 있으면 결정을 기다리는 승인 지점, 없으면 알림만)
- `Step` — id, role_id, name, **do: Action** (이 step의 행동 하나), **on: list[Exit] = []** (탈출 조건, 앞에서부터 첫 참인 것), **report: ReportSpec|None = None** (step에 들어갈 때 카드 한 장), ui: dict = {} (편집기 좌표, 엔진은 읽지 않음). 결정 0006: step 안에 줄 목록을 두지 않는다. 10/8 실행안 PDF의 `do`/`on`/`report`와 같은 꼴
- `EmergencyRules` — battery_low_pct: float = 30, link_lost_step: str|None, battery_low_step: str|None, operator_call_step: str|None
- `Play` — id, name, roles: list[Role], steps: list[Step], emergency: EmergencyRules, entry: dict[str, str] (역할 id → 첫 step id), origin: "human"|"ai_draft", approved: bool = False, template: bool = False
- `ValidationIssue` — code: str, step_id: str|None, message: str
- `PlayCheck` — ok: bool, issues: list[ValidationIssue], est_return_battery: dict[str, float] (역할 id → 예상 귀환 배터리 %)

**명령과 하한선**
- `Provenance` — source: CommandSource, play_id: str|None, step_id: str|None, decision_id: str|None, injection_id: str|None, operator_id: str|None, issued_ms: int
- `Command` — id, vehicle_id, kind: CommandKind, params: dict (target: GeoPoint | route: list[GeoPoint] | target_id | distance_m 등), provenance: Provenance|None
- `PassedCommand` — command: Command, checks: list[str] (통과한 규칙 이름 3개), passed_ms: int. **safety 모듈의 `check_command`만 만든다.** 다른 곳에서 생성하는 테스트를 두어 막는다(파이썬이라 타입으로 강제되지 않음, 테스트와 리뷰로 지킴)
- `Block` — command_id, vehicle_id, reason: BlockReason, detail: str, alternative: Command|None, t_ms

**감지·보고·결정**
- `Target` — id, kind: TargetKind, pos: GeoPoint, vel_east_mps: float, vel_north_mps: float, first_seen_ms, last_seen_ms, seen_by: list[str]
- `Report` — id, t_ms, kind: ReportKind, vehicle_id: str|None, target_id: str|None, role_id: str|None, text: str, choices: list[Choice] = [], resolved_ms: int|None, decision_id: str|None
- `Decision` — id, t_ms, report_id, choice_id, operator_id = "op1"
- `Assignment` — role_id, vehicle_id, since_ms, reason: str ("계획 담당 지정" 또는 "예비 n번 투입")
- `Injection` — id, play_id, anchor: dict (target_id 또는 zone Polygon), proposed: list[Assignment], status: "pending"|"approved"|"rejected", t_ms
- `DirectControl` — vehicle_id, target: GeoPoint, t_ms (운용자 직접 조종 입력)

**측정·프레임**
- `Metrics` — operator_actions: int, manual_baseline_actions: int, open_reports_max: int, role_gap_ms: int, blocked_commands: int, decisions: int, commands_sent: int, mission_success: bool|None
- `Frame` — t_ms, vehicles: list[VehicleState], targets: list[Target], reports: list[Report], assignments: list[Assignment], blocks: list[Block], injections: list[Injection], metrics: Metrics, log: list[str] (이 틱에 생긴 기록 줄). 시연 규모(기체 5·표적 2·카드 3)에서 JSON 3.4KB, 직렬화 0.013ms(측정)

**시나리오(sim 입력)**
- `ScenarioEvent` — t_ms, kind: "spawn_target"|"target_move"|"vehicle_link_lost"|"vehicle_battery_set"|"split_target", params: dict
- `Scenario` — id, operation: Operation, vehicles: list[VehicleSpec], plays: list[Play], events: list[ScenarioEvent], seed: int, tick_ms: int = 200, speed: float = 1.0

**엔진 입력(틱마다)**
- `TickInputs` — decisions: list[Decision], direct: list[DirectControl], injections: list[Injection](승인/거부 상태 변화)

### 2.3 지표 정의(발표에서 그대로 말할 문장)
- `operator_actions`: 운용자가 누른 횟수. 결정 + 직접 조종(차단 뒤 대안 지점을 눌러 다시 보낸 것 포함) + 주입 승인·거부.
- `manual_baseline_actions`: 같은 대본에서 기체별 직접 조종이었다면 사람이 내려야 했을 명령 수. 정의 = 엔진이 만든 `Command` 수(출처가 play_step·emergency인 것) + 보고 카드 수. **같은 실행 안에서 센다.** 두 번 돌리지 않으므로 결정 재생 형식이 필요 없다. 결정 0003의 "수동 모드(기체별 직접 명령 수를 엔진이 세기만 함)"를 이렇게 해석했다. 사람이 실제로 조작한 값이 아니라고 발표에서 말한다.
- `open_reports_max`: 미해결 보고 카드가 동시에 떠 있던 최대 개수.
- `role_gap_ms`: 역할에 배정된 기체가 없던 시간의 합. 기체 이탈 틱부터 **이어받은 기체가 그 step의 목적(감시: 표적이 센서 범위 안, 이동: 도착)에 닿은 틱**까지. 검토 전 정의("첫 PassedCommand 틱까지")로는 예비가 있으면 항상 1틱(200ms)이라 카드도 숫자도 생기지 않았다. 스파이크에서 드론 3이 기지에서 표적까지 가는 약 4분이 공백으로 잡힌다.
- `mission_success`: 시나리오가 정한 조건(선박 식별 보고가 처리됨)을 끝까지 만족했는가.

---

## 3. 모듈별 목표·방향·공개 API·완료 기준

형식: 목표(한 줄) / 방향(어떻게) / 공개 API(`from modules.<m> import ...`) / 완료 기준 / 하지 않는 것 / 담당.

### 3.1 contracts (리드, 10/9 밤)
- 목표: 2절을 `contracts/models/` 패키지로 옮기고 `contracts/examples/*.json`과 `contracts.gen.ts`를 만든다.
- 방향:
  - **파일 하나로는 못 넣는다.** 2절을 ruff 포맷으로 옮기면 353줄, 기존 78줄과 합쳐 431줄이라 guard·`check_specs.py`의 200줄 제한에 걸린다(측정). `contracts/models/` 패키지로 쪼갠다: `enums.py`, `world.py`(GeoPoint·Polygon·VehicleSpec·VehicleState·Operation), `play.py`, `command.py`(Provenance·Command·PassedCommand·Block), `events.py`(Target·Report·Decision·Assignment·Injection·DirectControl), `frame.py`(Metrics·Frame·Scenario·ScenarioEvent·TickInputs), `legacy.py`. `__init__.py`가 전부 re-export하고 `ALL_MODELS`를 든다. `from contracts.models import X`는 그대로 동작하므로 gen_contracts·모듈 코드는 안 바뀐다.
  - `scripts/check.sh` 31행의 `^contracts/models.py$`를 `^contracts/models/`로 바꾼다(안 바꾸면 TS가 조용히 옛 상태로 남는다).
  - 기존 Detection·Track·Assessment·Response·Frame은 `legacy.py`로 옮기고 **Frame은 `LegacyFrame`으로 이름을 바꾼다**(새 Frame이 그 이름을 쓴다). gateway `build_frame`·`smoke.py`·cop-ui 타입 참조를 같은 커밋에서 LegacyFrame으로 바꾼다. 안 그러면 ship의 smoke가 막혀 아무도 push하지 못한다.
  - `smoke.py`는 통합 1 전까지 레거시 엔진을 돌리고, runtime이 붙는 순간 백령도 시나리오로 바꾼다(리드).
- 완료 기준: 예시 JSON이 전 모델에 하나씩 있고 `gen_contracts.py`·`pytest`·`smoke.py`가 통과. **10/9 밤에 끝낸다.** 10/10 12:00은 검토만.
- 하지 않는 것: 모델 상속, Optional 남발. 필드 추가는 리드만.

### 3.2 play (팀원 3, 새 모듈)
- 목표: 플레이 파일을 읽고·검사하고·기체 명령으로 펼치고·AI 초안을 만든다.
- 방향:
  - 저장 전 검사 4종(step 단위): 로직 오류(`Exit.go_step`·`Choice.step_by_role`·`entry`가 없는 step을 가리킴, entry에서 닿을 수 없는 step), 보고·승인 지점 누락(target_found 탈출 뒤 choices 있는 report 없이 approach_target step에 닿는 경로), 귀환 배터리(각 역할의 경로 길이와 VehicleSpec 평균으로 추정), 작전 구역 밖 경로점.
  - 펼치기 표: `(ActionKind, Domain) -> CommandKind | None`. 표는 JSON 하나(`modules/play/expand_table.json`). None이면 그 기체는 그 역할 후보에서 빠진다. hold는 모든 영역에서 hold.
  - AI 초안: 문장 + 어휘(ActionKind·ConditionKind) + Play JSON 스키마를 LLM에 주고 구조화 출력만 받는다. 스키마 밖이면 버리고 한 번 재요청. `origin="ai_draft", approved=False`로 돌려준다. 응답은 `demo/plays/cache/<sha256(prompt)>.json`에 저장하고, 캐시가 있으면 호출하지 않는다. API 키는 `.env`.
  - 템플릿 2개를 손으로 쓴다: 해안 경계(**역할 4**: AIR 순찰(vehicles [드론1, 드론3])·SEA 확인·GROUND 상륙 감시·AIR 예비 순찰(vehicles [드론2], 결정 전에는 wait 줄에서 대기)), 고속 보트 추적(역할 1: AIR 추적). 역할 3개로는 사건 2의 "예비 드론이 빈 구역 순찰"이 나오지 않는다(검토에서 확인: 결정은 `Choice.step_by_role`로 역할을 움직이므로 넷째 역할이 있어야 넷째 기체가 움직인다).
- 공개 API: `load_play(path) -> Play`, `check_play(play, op: Operation, specs) -> PlayCheck`, `expand_action(action, domain) -> CommandKind|None`, `draft_play(text, op) -> Play`, `list_templates() -> list[Play]`
- 완료 기준: 템플릿 2개가 `check_play` 통과. 보고 지점을 뺀 플레이는 실패. AI 초안이 캐시로 재현. 전부 순수 함수, 예시 JSON으로 테스트.
- 하지 않는 것: 서명, 버전 관리, 플레이 간 참조.

### 3.3 runtime (팀원 2, 새 모듈)
- 목표: 틱마다 기체별 현재 (플레이, step)을 진행해 `Command`를 만들고, 보고·결정·이어받기·주입·직접 조종·비상을 처리하며 지표를 센다.
- 방향(결정 0006 단순형):
  - 상태 기계는 `VehicleState`의 play_id/step_id/entered_step이다. **step에 들어간 첫 틱에 `do`를 `Command` 하나로 내고(있으면 `report` 카드도 한 장), 그 뒤 매 틱 `on`을 앞에서부터 평가해 첫 참인 `Exit.go_step`으로 옮긴다.** 줄 해석기·line_idx·if_cond가 없다. 수행은 sim이 `VehicleState.active`로 계속한다(1절). 순찰 step의 전형: `do=patrol_route(route), on=[target_found → 보고 step]`.
  - 행동 9개 중 시연에 필요한 것부터: patrol_route, watch_target, approach_target, move_to, return_home, hold(대기 step). 조건은 target_found·arrived·battery_below. 나머지 행동(search_area, relay_comms, watch_point)과 조건(time_elapsed, signal_received)은 빼는 순서 뒤쪽.
  - 보고 → 결정: `report`에 choices가 있으면 `pending_report_id`를 적고 그 값이 있는 동안 전이하지 않는다(`do`는 보통 hold 또는 watch_target). `Decision`이 오면 `pending_report_id`를 지우고 `Choice.step_by_role`대로 각 역할의 기체를 해당 step으로 옮기며 `entered_step=False`로 둔다(주인공 장면). choices 없는 report는 알림 카드만 만들고 멈추지 않는다(사건 3의 "알림만").
  - 배정(결정 0005, 고정): `Role.vehicles` 순서에서 status가 ready·active이고 **다른 역할에 배정돼 있지 않은** 첫 기체. 점수 계산 없음.
  - 이어받기: 기체가 returning·lost·maintenance가 되면(또는 귀환 step에 들어가면) `Role.vehicles`의 다음 예비 기체가 이탈한 기체의 step을 `entered_step=False`로 시작한다. 예비가 없으면 `role_gap` 보고 카드와 `role_gap_ms` 누적. **영역 제한은 두지 않는다.** `Role.vehicles`에 다른 영역 기체를 적으면 그대로 이어받고, 명령은 그 기체의 영역으로 펼쳐진다(`expand_line(line, domain)`). runtime 코드는 영역을 보지 않으므로 비용이 없다.
  - 주입: `Injection`은 pending으로 들어오고 승인될 때까지 명령을 만들지 않는다(출처 없음). 승인되면 proposed대로 배정하고 원래 (play, step)은 resume_play_id/resume_step_id에 보관.
  - 직접 조종: `DirectControl`은 `Command(kind=move, provenance.source=operator_direct)`. 도착하면 resume (play, step)으로 복귀. 차단된 명령의 대안 지점은 화면이 `/direct`로 다시 보낸다(별도 엔드포인트 없음, 운용자 조작 1회로 센다).
  - 비상: battery_below(EmergencyRules.battery_low_pct)·link_lost·operator_call → 지정 step으로, 끝나면 resume.
  - 수동 기준선: 같은 실행에서 `manual_baseline_actions`를 2.3 정의대로 센다. 두 번 돌리지 않는다.
- 공개 API: `step_vehicles(state, plays, targets, t_ms) -> (state, list[Command], list[Report])`, `assign_roles(play, states) -> list[Assignment]`(배정과 이어받기 같은 함수), `apply_decision(state, play, decision) -> state`, `apply_injection(...)`, `update_metrics(metrics, frame_parts) -> Metrics`
- 완료 기준: 통합 1 슬라이스(4절). 결정 한 번에 역할 4개가 함께 step을 바꾸는 테스트. 역할 공백 시간이 세어지는 테스트. step 진입 때 명령·카드가 한 번만 나오는 테스트.
- 뼈대: `knowledge/spikes/rolecall_engine_proto/step_vehicle.py`가 단순형 step 진행 액션의 출발점(80줄 안, 결정 0006 반영 뒤 재실행 확인).
- 하지 않는 것: 경로 계획(직선만), 충돌 회피.

### 3.4 safety (팀원 2, 새 모듈)
- 목표: 모든 `Command`에 규칙 3개를 적용해 `PassedCommand` 또는 `Block`을 돌려준다. 예외 허가 없음(결정 0003).
- 방향:
  - 규칙 1 `no_provenance`: provenance가 None이거나, source가 injected_plan인데 injection이 approved가 아니거나, source가 play_step인데 play.approved가 False면 막는다. 대안 없음(승인 대기 카드).
  - 규칙 2 `outside_zone`: 명령의 목적지(또는 경로점 전부)가 `Operation.zone` 밖이면 막는다. 대안 = 목적지와 현재 위치를 잇는 선이 구역 경계와 만나는 점에서 안쪽으로 50m 들어온 지점으로 같은 kind의 명령.
  - 규칙 3 `battery_insufficient`: 목적지까지 + 목적지에서 home까지 거리를 speed_mps로 나눈 시간이 남은 배터리(endurance_min × battery_pct)의 80%를 넘으면 막는다. 대안 = 갈 수 있는 최대 거리 지점.
  - 규칙 순서 1→2→3. 첫 실패에서 멈춘다.
- 공개 API: `check_command(cmd, state, spec, op, plays, injections) -> PassedCommand | Block`, `point_in_polygon(p, poly) -> bool`, `return_feasible(...) -> (bool, GeoPoint|None)`
- 완료 기준: 규칙마다 통과·차단·대안 테스트. `PassedCommand`를 safety 밖에서 만드는 코드가 없음을 grep 테스트로 확인.
- 하지 않는 것: 서명 검증, 이상 명령 탐지, 지휘관 예외.

### 3.5 sim (팀원 2, 고쳐 씀)
- 목표: `PassedCommand`대로 기체를 움직이고 배터리를 줄이며 사건 대본을 재생한다.
- 방향: 2D 등속 직선 이동, 배터리는 `100 / endurance_min` %/분 선형. orbit은 반지름 고정 원운동, keep_distance는 표적과 거리 유지, follow_route는 경로점 순회(`waypoint_idx`를 돌린다). **이번 틱 `PassedCommand`가 있으면 `VehicleState.active`를 그것으로 바꾸고, 없으면 `active`를 계속 수행한다.** orbit·keep_distance는 표적 위치가 필요하므로 `advance`가 targets를 받는다. 사건 대본의 `ScenarioEvent`를 t_ms에 적용(표적 출현·이동·분리, 기체 link_lost, 배터리 강제 설정).
- 공개 API: `load_scenario(path) -> Scenario`(기존 YAML 로더를 JSON·새 모델로 교체. `modules/sim/types.Scenario`는 레거시로 이름 변경), `advance(states, specs, passed: list[PassedCommand], dt_ms, targets) -> states`, `apply_events(scenario, states, targets, t_ms, dt_ms) -> (states, targets)`
- 완료 기준: 명령 8종 각각 1틱 이동 테스트. 명령 없는 틱에 active가 계속 수행되는 테스트. 사건 5개 대본이 끝까지 돈다.
- 뼈대: `knowledge/spikes/rolecall_engine_proto/engine_proto.py`의 `advance`·`apply_events`(합쳐 약 60줄). 35분 작전 10,500틱이 0.5초에 돈다(측정, 틱당 0.05ms). 1배속 0.2초 틱과 15배속 모두 여유.
- 하지 않는 것: SITL, 물리, 바람·해류, 3D.

### 3.6 sensing (팀원 2, 고쳐 씀)
- 목표: 기체 센서 범위 안 표적을 "본 것"으로 표시하고 `target_found` 조건의 근거를 만든다.
- 방향: 거리 ≤ sensor_range_m이면 `Target.seen_by`에 기체 id 추가, last_seen_ms 갱신. 야간이라 범위를 줄인 값을 VehicleSpec에 직접 넣는다. 탐지 잡음은 없앤다(시연 재현성).
- 공개 API: `observe(states, specs, targets, t_ms) -> targets`
- 완료 기준: 범위 안·밖 테스트. 기존 Detection 기반 액션은 삭제하지 않고 파이프라인에서만 뺀다.

### 3.7 gateway (리드, 고쳐 씀)
- 목표: 엔진을 돌리고 화면과 주고받는다.
- 방향: `engine.tick`를 gateway의 `engine.py`에 두고 모듈 순서대로 부른다(로직 없음). 실행 경로는 `/run/live?speed=` 하나: 0.2초마다 `speed`개 틱을 돌리고 마지막 Frame을 WS로 보낸다. 상태는 프로세스 메모리 하나(작전 1개). 틱 순서(스파이크와 같다): apply_events → observe → 입력 적용(decisions·direct·injections) → step_vehicles → assign_roles(이어받기) → check_command(전부) → advance → update_metrics → Frame.
- REST(확정): `GET/POST /plays`, `POST /plays/check`, `POST /plays/draft`, `GET/POST /operation`, `POST /run/live`, `POST /run/reset`, `POST /decisions`, `POST /direct`, `POST /injections`, `POST /injections/{id}/approve|reject`, `POST /run/jump?t_ms=` (발표용 "다음 사건으로": 그 시각까지 틱을 돌린다). WS `/ws`: Frame. (`/run/preview`·`/mode`는 검토에서 뺐다.)
- 완료 기준: smoke가 사건 5개 대본을 끝까지 돌려 Metrics를 낸다. 리셋 뒤 같은 seed로 같은 결과.
- 하지 않는 것: 인증, 다중 작전, 영속 저장.

### 3.8 cop-ui (map·live·replay 리드, editor·setup 팀원 3)
- 목표: 화면 2개. 편집기(설정 포함)와 상황판.
- 방향:
  - 편집기: React Flow를 쓰지 않는다. 역할별 세로 열에 step 카드. 카드 하나 = 행동 드롭다운 1개 + 탈출 조건 목록(조건·갈 step 드롭다운) + 보고 칸(문구·선택지). 줄 목록 UI 없음(결정 0006). 상단에 AI 초안 입력 칸. 저장 버튼이 `/plays/check` 결과를 카드 옆에 표시. 작전 설정(이름·작전 구역 그리기·기체 선택)은 편집기 왼쪽 패널.
  - 상황판: MapLibre + 백령도 위성 타일(로컬 캐시, 결정 0004·0001), 기체·표적·작전 구역·경로, 오른쪽에 카드 열(보고·역할 공백·승인 대기·차단), 카드의 선택지 버튼이 `/decisions`. 직접 조종은 기체 클릭 후 지도 클릭. 차단 카드의 "대안 지점으로" 버튼은 `/direct`를 대안 좌표로 다시 보낸다. 아래에 지표 패널: 운용자 조작 수 대 수동 기준 명령 수 나란히(한 실행의 Metrics). 발표용 배속과 "다음 사건으로".
  - 타일: EOX Sentinel-2 cloudless(CC BY-NC-SA 4.0, 출처 표기) z8~14, `scripts/fetch_tiles_baengnyeong.sh`로 199장 1.2MB(실행 확인, 23초). 10m 해상도라 군사시설이 식별되지 않아 정책 2번에도 맞다. Esri World Imagery는 z16까지 선명하지만 오프라인 캐시가 약관상 제한되고 시설이 보이므로 쓰지 않는다. MapLibre raster source `tiles: ["/tiles/baengnyeong/{z}/{x}/{y}.jpg"]`, maxzoom 14(그 위는 확대 표시). 타일 없으면 현재처럼 배경색만.
  - 미리 보기(시뮬레이션 화면)는 별도 화면이 아니라 상황판을 배속으로 돌리는 것.
- 완료 기준: 통합 2 슬라이스(4절)를 화면 조작만으로 통과.
- 하지 않는 것: 드래그 연결선, 되돌리기, 다중 작전, 로그인.
- 대회 전 수정: `modules/cop-ui/AGENTS.md`의 "외부 네트워크 금지"를 "로컬 타일 우선, 온라인 타일 허용(결정 0001)"으로, 담당 "팀원 4"를 실제 배정으로.

### 3.9 tracking · assess · respond
- 휴면. 코드와 테스트는 남기고 파이프라인에서만 뺀다. SPEC.md에 "T1-3용, 휴면" 표기.

### 3.10 demo (리드)
- 백령도 시나리오 데이터: `demo/scenarios/baengnyeong_night.json`(Operation + VehicleSpec 5 + 사건 5), 플레이 2개, AI 초안 캐시 2개, 위성 타일 캐시, `BUILT_HERE.md` 갱신, 3분 대본.

---

## 4. 통합 슬라이스(검사 가능한 끝에서 끝 경로)

**통합 1 (10/10 18:00)** — 편집기 없이.
손으로 쓴 플레이 JSON → `check_play` 통과 → `/run/live` → 드론이 순찰 → 표적 출현(사건 1) → `target_found` 탈출 → 보고 step 진입 → Report 카드가 WS Frame에 실림 → `/decisions`로 선택 → 역할 4개의 기체가 각자 step으로 이동 → `check_command`가 전부 통과 → 지도에 네 기체가 움직임. Metrics에 operator_actions=1이 찍힘.

통합 1에 필요한 액션 수(검토에서 셈): 팀원 2 — sim 2(advance·apply_events), sensing 1(observe), safety 3(check_command·point_in_polygon·return_feasible), runtime 5(step_vehicles·assign_roles·apply_decision·apply_injection은 뒤로·update_metrics) = **11개, 12:00~18:00 6시간에 시간당 약 2개**. 스파이크 코드를 옮기면 가능하고, 백지에서 쓰면 안 된다. 팀원 3 — play 2(load_play·check_links)만 18:00 전, 나머지 검사 3개·expand_line·list_templates는 00:00까지. 리드 — contracts(밤), gateway engine.py·app.py 재작성, build_frame 1개, 시나리오 JSON, 타일.

**통합 2 (10/11 00:00)** — 화면 조작만으로.
편집기에서 AI 초안 입력 → 검사 실패 카드(보고 지점 없음) → 카드 추가 → 저장 통과 → 상황판에서 실행 → 사건 1·2·3(귀환·이어받기·역할 공백 카드)·4(주입 승인 대기 → 승인)·6(구역 밖 차단·배터리 차단) → 지표 패널에 두 모드 나란히 → 3분 안에 리허설 1회.

**동결 (10/11 06:00)** — `KDTH_FREEZE=1`. 이후 데이터·문구·대본만.

---

## 4.5 어디까지 대본이고 어디부터 계산인가

심사에서 "그거 계산된 겁니까?"에 답할 선. 세 층으로 나누고, 발표와 `demo/BUILT_HERE.md`에 같은 말로 적는다.

| 층 | 내용 | 시연에서 | 왜 |
|---|---|---|---|
| **대본(입력)** | 사건 5개의 시각·위치(표적 출현·분리, 드론 1 배터리 강제 설정), 기체 제원 5개, 작전 구역 폴리곤, 템플릿 플레이 2개, **역할별 기체 배정과 예비 순서(결정 0005)** | `Scenario` JSON 파일. 화면 기록 줄에 `[대본]` 표시 | 공개·가상 데이터 정책. 환경은 우리가 정하는 것이 맞다 |
| **계산(엔진)** | 기체 이동·배터리, 센서 범위 탐지, step 진행, 보고 카드 생성, 이어받기(예비 순서대로), 역할 공백, 주입 승인 대기, 직접 조종, 하한선 규칙 3개와 대안 지점, 지표 전부(두 모드) | 틱마다 실제로 계산. 같은 seed면 같은 결과 | 이것이 "계산·측정·보장"이다. 여기에 고정값을 넣는 순간 SUPPORTY와 같아진다 |
| **캐시(외부 응답)** | AI 초안의 LLM 응답 2개, 백령도 위성 타일 | 파일에서 읽음. 캐시 미스면 라이브 호출, 실패하면 템플릿으로 대체하고 화면에 표시 | 결정 0001의 "끊겨도 이어감" |

**하지 않는 것(연출 금지 목록).** 아래가 하나라도 들어가면 심사 질의에서 무너진다.
- 보고 카드를 시각으로 띄우기(예: T+11분에 카드 생성). 카드는 `target_found` 조건이 센서 범위 계산으로 참이 될 때만 생긴다. 대본은 표적을 그 시각에 그 위치에 놓을 뿐이다. 따라서 08 5.4의 "T+11분 보고"는 표적 출현 시각이고 보고 시각은 엔진이 정한다(스파이크에서 11분 출현 → 16분 보고). 대본의 출현 위치·순찰 경로를 엔진을 돌려 가며 맞춘다. 3분 대본의 시각은 그 결과로 적는다.
- (배정은 결정 0005로 대본 층. 질의에서 물으면 "해커톤이라 배정은 고정으로 하고 진행했다"고 그대로 답한다. 이어받기와 역할 공백은 계산 층.)
- 지표를 손으로 적기. 두 모드의 숫자는 같은 seed로 돌린 Metrics에서만 나온다.
- 차단 카드를 직접 조종 입력에 붙여 두기. 차단은 safety가 실제로 규칙을 평가한 결과여야 한다. 시연 대본은 운용자가 어디를 찍을지만 정한다.
- 사건 2의 "결정 한 번에 세 기체 이동"을 기체별 이동 명령 3개로 미리 적어 두기. 이동은 `Choice.step_by_role`과 runtime의 step 전이에서 나와야 한다.

**발표에서 말할 문장.** "사건의 시각과 위치, 역할별 기체 배정은 작전 전에 정한 대본입니다. 그 뒤의 탐지·보고·이어받기·차단·숫자는 전부 엔진이 틱마다 계산한 것이고, 같은 시드로 다시 돌리면 같은 결과가 나옵니다. AI 초안 응답과 지도 타일은 행사장 인터넷 때문에 미리 받아 둔 캐시입니다."

**개발 중 스텁(시연의 대본과 다름).** 통합 1(18:00)에서 늦은 파트는 예시 JSON으로 대체한다. 편집기가 늦으면 플레이는 손으로 쓴 JSON, runtime이 늦으면 gateway가 예시 Frame을 그대로 보낸다. 스텁은 `contracts/examples/`의 파일만 쓰고, 통합 2(00:00) 전에 전부 걷어낸다. 통합 2 뒤에 남아 있는 스텁은 "계산" 층을 "대본" 층으로 떨어뜨리는 것이므로 `BUILT_HERE.md`에 적고 발표에서 말한다.

---

## 5. 구현 원칙(모듈 공통)

1. 액션 파일 1개 = 공개 함수 1개 = 80줄 이하 = 테스트 1개. 틱의 한 단계가 한 액션이 되도록 쪼갠다.
2. 엔진 쪽 함수는 전부 순수 함수. 입력을 바꾸지 않고 새 객체를 돌려준다. 시간은 인자 `t_ms`로만 받는다(`time.time()` 금지).
3. 난수는 `Scenario.seed`에서 나온 `random.Random` 하나만. 같은 seed = 같은 Frame 열.
4. `PassedCommand`는 safety만 만든다. 다른 모듈에서 생성자를 호출하면 테스트가 실패하도록 grep 테스트를 둔다.
5. 다른 모듈은 공개 API만 import. `modules.<m>.actions...` import 금지(guard가 막음).
6. 외부 호출은 play의 `draft_play` 하나뿐이고 캐시를 먼저 본다. 시연 경로에서 캐시 미스가 나면 템플릿으로 대체하고 화면에 "캐시 없음" 표시.
7. 좌표는 contracts의 GeoPoint만. 편집기 화면 좌표는 `Step.ui`에만.

---

## 6. 사람별 영역(방향만, 액션은 사이클 시작 때)

팀(결정 0007): 리드 kth9245, 팀원 황승주·최동호. 파트 2·3을 누가 맡는지는 다음 세션의 devil-advocate 검토(11절) 뒤 정한다.

| 파트 | 담당 | 모듈 | 첫 사이클에서 끝낼 것 |
|---|---|---|---|
| 1 | 리드 kth9245 | contracts, gateway, cop-ui map/live, demo | contracts 확정(10/9 밤), gateway 틱 루프와 WS, 백령도 타일, 시나리오 데이터 |
| 2 | 황승주 또는 최동호 | sim, sensing, runtime, safety | sim 이동·배터리, safety 규칙 3, runtime step 진행과 report→decision (통합 1 액션 11개) |
| 3 | 황승주 또는 최동호 | play, cop-ui editor/setup | 플레이 형식 로드·검사, 템플릿 2개, 편집기 카드 열 (통합 1 액션 2개, 나머지 00:00까지) |

도움 가능(순수 함수): play 검사 4종, safety 규칙 3개, Metrics 집계, 펼치기 표. 막히면 5분 안에 "막힘: 모듈, 함수, 증상"을 채팅에.

---

## 7. 빼는 순서(늦어질 때, 앞에서부터)

1. 작전 설정 패널(기체 선택은 시나리오 파일 고정값으로)
2. 행동 뒤쪽 3종(search_area, relay_comms, watch_point)과 조건 2종(time_elapsed, signal_received)
3. 비상 규칙 link_lost·operator_call(battery_low만 남김)
4. 주입(사건 4). 승인 대기 카드만 남기고 승인 뒤 배정 전이는 뺀다
5. AI 초안 라이브 호출(캐시 응답만, 입력 칸은 유지)
6. 편집기 카드 편집(읽기 전용 카드 + 저장 검사만)
(배정 점수는 결정 0005로 처음부터 없음. 미리 보기 경로와 두 모드 재실행은 검토에서 설계 자체를 뺐으므로 여기 없음)

끝까지 남기는 것: 결정 한 번에 세 역할 이동, 보고 카드, 이어받기와 역할 공백 카드, 주입 승인 대기, 구역 밖·배터리 차단, 지표 두 모드 나란히.

---

## 8. 대회 전(10/9 밤) 할 일 — 검토 결과로 갱신

1. **contracts 패키지**(리드, 약 1.5시간): `knowledge/spikes/rolecall_engine_proto/models09.py`를 `contracts/models/` 6개 파일로 나눠 넣고(3.1), 레거시 모델을 `legacy.py`·`LegacyFrame`으로 옮기고 gateway·smoke·cop-ui 참조를 고친다. `check.sh` 31행 수정. 예시 JSON 29개·TS 생성. `pytest`·`smoke.py` 통과 확인.
2. **타일**: `scripts/fetch_tiles_baengnyeong.sh 14`를 실행해 `modules/cop-ui/public/tiles/baengnyeong/`에 199장을 넣고 커밋(1.2MB). 약관 확인 끝(EOX CC BY-NC-SA, ATTRIBUTION.txt 생성됨). `basemap.ts`에 raster source 추가는 10/10 리드 첫 사이클.
3. `modules/cop-ui/AGENTS.md`(담당 팀원 4 → 리드 map/live·팀원 3 editor, "외부 네트워크 금지" → "로컬 타일 우선, 온라인 허용(결정 0001)"). 루트 AGENTS.md 모듈 담당 표에 play·runtime·safety 추가.
4. `new_module.py`로 play(PLY)·runtime(RT)·safety(SFT) 뼈대 생성. 각 SPEC.md에 4절의 통합 1 액션 이름을 미리 행으로 적어 두면 10/10 아침에 `new_action.py`만 돌리면 된다.
5. **시나리오 JSON**(리드): `demo/scenarios/baengnyeong_night.json`을 스파이크의 `engine_proto.py` 하단 데이터(작전 구역·기체 5·플레이 역할 4·사건)에서 옮기고, 사건 시각·위치를 스파이크로 돌려 보고 시각이 3분 대본에 맞게 조정. 템플릿 플레이 2개도 같은 파일에서.
6. AI 초안 프롬프트와 캐시 2개 생성(인터넷 되는 곳에서). 08 5.4 사건 3 문구를 "예비 드론 3이 이어받음, 닿을 때까지 역할 공백"으로 고친다(이 커밋에서 반영).

---

## 9. 알려진 구현 위험(2026-10-09 검토 뒤)

해결됨(검토에서 확인·반영): report 대기 전이(`pending_report_id`), 결정 재생(두 모드 재실행 폐지), 80줄 제한(한 줄 진행 58줄), 타일 약관·용량(EOX 199장 1.2MB).

남은 것:
- safety 규칙 3(배터리)의 추정식이 orbit·keep_distance처럼 목적지가 없는 명령에 애매하다. 스파이크는 목적지 없는 명령에 규칙 3을 건너뛴다. 시연 사건 6은 move 명령이라 영향 없음. 발표에서 묻히면 "목적지 있는 명령에 적용"이라고 답한다.
- 수동 기준선 정의(2.3)가 심사위원에게 "지어낸 숫자"로 보일 수 있다. 정의를 화면에 그대로 적는다.
- 사건 4(주입)와 사건 6(직접 조종)이 같은 드론 2에 연달아 오므로 resume 쌍이 덮인다. 주입 승인 뒤의 플레이가 그 기체의 현재 플레이이므로 덮여도 복귀 대상은 맞다. 빼는 순서 4번.
- 3명 중 React 경험자가 없으면 파트 3이 막힌다. 편집기는 처음부터 읽기 전용 카드 + "보고 카드 끼워 넣기" 버튼 하나로 시작하고, 남으면 편집을 넣는다(빼는 순서 6번을 기본값으로).
- 리드의 10/9 밤 작업(8절 1·5번)이 안 끝나면 10/10 12:00 형식 고정이 밀리고 팀원 2의 11개 액션이 같이 밀린다. 이것이 지금의 하중 가정이다.

---

## 10. devil-advocate 검토 결과(2026-10-09 밤)

주장: "이 문서의 모듈 경계·데이터 형식·통합 슬라이스대로 가면 3명이 통합 1·2를 넘기고 3분 시연이 재현된다." 하중 가정으로 적었던 것은 "runtime을 팀원 한 명이 15:00~21:00에 만든다"였다.

| 항목 | 판정 | 근거·변경 |
|---|---|---|
| 급소: `VehicleState`에 현재 명령이 없어 한 번 낸 명령으로는 기체가 다음 틱에 멈춘다. 진짜 하중 가정은 "12:00 뒤 계약을 안 바꾼다"다 | **CONCEDE** | 스파이크 `--no-active`로 재현(드론 3m 이동 뒤 정지, 표적 미탐지). `active`·`pending_report_id`·`resume_play_id` 추가, `Line.params` 타입 수정. 계약 변경을 10/9 밤으로 당겨 흡수 |
| 공격 1: resume 한 칸, 대안 적용 엔드포인트 없음, 결정 재생 형식 없음 | **CONCEDE** | resume을 (play, step) 쌍으로. 대안은 화면이 `/direct` 재전송. 두 모드 재실행을 없애 재생 형식 불필요 |
| 공격 2: 08 사건 3(수상정 이어받기)과 09 "영역 넘는 이어받기 안 함"이 모순, 역할 3개로는 예비 드론이 안 움직임 | **CONCEDE** | 영역 제한 삭제(runtime은 영역을 안 봄). 템플릿 역할 4개. 08 사건 3 문구 수정 |
| 공격 3: models.py 431줄로 200줄 guard에 걸림, check.sh 31행, smoke·build_frame·cop-ui가 새 Frame에 깨져 ship 불가 | **CONCEDE** | 측정 431줄. `contracts/models/` 패키지, `LegacyFrame` 개명, check.sh 수정, 같은 커밋에서 smoke 유지 |
| 하중 가정(runtime 6시간) | **REBUT 일부** | 한 줄 진행 58줄, sim+sensing+safety+runtime 뼈대 합계 약 250줄이 스파이크에 있음. 11개 액션을 6시간에 옮기는 일로 바뀜. 단 스파이크 없이 백지에서는 성립하지 않음 |
| 틱 성능 | **REBUT** | Frame 직렬화 0.013ms, 35분 10,500틱 0.5초 |
| 타일 | **REBUT** | 스크립트 실행 확인(199장 23초), 약관 EOX CC BY-NC-SA |

반대자의 P(MISTAKE) 70% → 수정 뒤 내 추정 40%. 남은 위험은 9절.

더 싼 대안(반대자 제안): step을 "행동 하나 + 탈출 조건 목록"으로 단순화해 줄 해석기를 없애는 것. 10/8 실행안 PDF의 step 형식(`do` + `on`)과 같다. **결정 0006으로 처음부터 이 형태를 쓴다.** 편집기 카드와 AI 초안 어휘는 step 단위(ActionKind 9개 + ConditionKind)로 맞췄다. 스파이크를 단순형으로 바꿔 다시 돌려 같은 사건 대본이 끝까지 도는 것을 확인했다.

같은 검토에서 사람이 답한 것(결정 0006): 스파이크 코드를 대회에서 쓰고 사전 준비분으로 밝힌다. 수동 기준선은 한 실행에서 센다. 타일은 EOX Sentinel-2 z8~14.

---

## 11. 다음 세션 devil-advocate 주장 블록(역할 분담과 저장소 구조)

결정 0007 뒤 사람이 지정한 검토 대상: "이 역할 분담의 당위성과 이거에 맞게 레포 구조가 잘 짜여져 있는지". 반대자에게 줄 것은 이 블록과 파일 경로뿐이다.

```
CLAIM: 6절의 3파트 분담(리드: contracts·gateway·지도·demo / 파트 2: sim·sensing·runtime·safety /
  파트 3: play·편집기)과 지금 저장소 구조(모듈별 디렉터리, 1 액션 = 1 파일 = 80줄, SPEC.md 등록,
  공개 API만 import, 로컬 브랜치 → main 직접 push)는 황승주·최동호가 서로 기다리지 않고
  10/10 12:00~18:00에 통합 1 경로를 만들게 한다.
EVIDENCE FOR: (1) 모듈 경계가 데이터 형식(contracts)으로만 이어져 파트 2·3이 같은 파일을 만지지 않는다.
  (2) 통합 1 액션 수를 세어 파트 2는 11개, 파트 3은 2개로 양이 비대칭이지만 파트 3에는 편집기(React)가
  뒤따른다. (3) 스파이크가 파트 2 액션 11개의 원본을 제공한다. (4) guard·SPEC·new_action이 구조를 강제한다.
COST IF WRONG: 한 사람이 병목이 되거나 두 사람이 같은 파일에서 충돌해 통합 1이 늦는다. 18:00을 놓치면
  통합 2(00:00)와 3분 시연이 연쇄로 밀린다.
LOAD-BEARING ASSUMPTION: 파트 2의 11개 액션(엔진 전부)을 한 사람이 6시간에 옮기고, 그동안 파트 3은
  play 2개 액션 뒤 React 편집기를 혼자 시작할 수 있다. 두 사람의 Python·React 경험은 아직 문서에 없다.
```

반대자가 보면 좋은 것: AGENTS.md 소유 표, 이 문서 3·4·6절, `modules/*/SPEC.md`, `tools/guard/check_edit.py`(브랜치 제한은 2026-10-09 제거됨), `scripts/ship.sh`(rebase → 검사 → main push), `knowledge/spikes/rolecall_engine_proto/`.
미리 알아 둘 약점: 리드가 contracts·gateway·지도·시나리오·타일·통합을 전부 쥐고 있어 리드가 병목일 가능성이 파트 2보다 클 수 있다. 세 사람이 main에 직접 push하므로 rebase 충돌이 잦으면 ship.sh가 막는다.
