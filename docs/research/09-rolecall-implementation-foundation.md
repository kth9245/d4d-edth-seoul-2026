# ROLECALL 구현 토대 — 데이터 형식(확정 수준), 모듈별 목표·방향, 통합 기준

정리일 2026-10-09. 결정 0003(아이디어 수정 방향)·0004(시나리오·장소)를 구현으로 옮기는 기준 문서. 계획 문서 08의 6절(시스템 구조)·7절(역할 분담)을 대체한다. 액션 목록은 여기 없다. 액션은 10/10 사이클 시작 때 각자 `new_action.py`로 만든다.

이 문서의 데이터 형식은 "v1 초안"이 아니다. 10/10 12:00 형식 고정 때 검토만 하고 그대로 `contracts/models.py`에 옮긴다. 바꿔야 하면 리드가 contracts 브랜치에서 바꾸고 팀에 알린다.

다음 세션 devil-advocate 주장 블록 초안은 10절.

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

- **엔진 하나.** `engine.tick(state, inputs) -> (state, frame)`는 순수 함수. 실시간 실행은 0.2초마다 한 번 부르고, 시뮬레이션(미리 보기)은 끝까지 돌려 frame 목록을 만든 뒤 배속으로 재생한다. 두 경로의 코드가 같다.
- **명령의 한 방향 흐름.** runtime이 `Command`를 만들고, safety만 `PassedCommand`를 만들며, sim은 `PassedCommand`만 받는다. 막힌 명령은 `Block`으로 frame에 실린다.
- **상태는 데이터.** 기체별 "지금 어느 플레이·step·줄에 있는가"를 `VehicleState`에 넣는다. 클래스 상속·콜백 없음. 액션 파일 하나가 틱의 한 단계를 맡는다.
- **파일 저장.** Play·Operation·Scenario는 JSON 파일(`demo/scenarios/`, `demo/plays/`). DB 없음.

---

## 2. 데이터 형식 (contracts/models.py, 확정 수준)

단위: 위경도 도(WGS84), 거리 m, 속도 m/s, 시간 UTC epoch ms(`t_ms`). 모든 모델은 pydantic v2. id는 문자열. `contracts.gen.ts`는 자동 생성.

### 2.1 열거형

| 이름 | 값 | 비고 |
|---|---|---|
| `Domain` | air, sea, ground | 기체 영역 |
| `VehicleStatus` | ready, active, returning, maintenance, lost | lost = 통신 두절 |
| `ActionKind` | move_to, patrol_route, search_area, return_home, watch_target, watch_point, approach_target, relay_comms, if_cond, loop, wait, send_signal, wait_signal, report, require_approval | 15개. AI 초안 어휘이기도 함 |
| `ConditionKind` | target_found, arrived, time_elapsed, battery_below, operator_choice, signal_received | 6개 |
| `CommandKind` | move, orbit, keep_distance, hold, follow_route, zigzag, return_home, relay | 8개. 기체로 나가는 명령 |
| `CommandSource` | play_step, operator_decision, operator_direct, injected_plan, emergency | 출처(하한선 규칙 1) |
| `BlockReason` | no_provenance, outside_zone, battery_insufficient | 하한선 규칙 3개와 1:1 |
| `ReportKind` | target_detected, role_gap, vehicle_lost, battery_low, injection_pending, command_blocked | 상황판 카드 종류 |
| `TargetKind` | boat, fast_boat, person, unknown | 시연용 |
| `EmergencyKind` | link_lost, battery_low, operator_call | 위치 이상은 뺌(결정 0004, GPS 장면 없음) |
| `RunMode` | role, manual_baseline | 인지부하 비교(결정 0003) |

### 2.2 모델 (필드 = 이름: 타입 [기본값])

**공간·기체**
- `GeoPoint` — lat: float, lon: float, alt_m: float = 0
- `Polygon` — points: list[GeoPoint] (3개 이상, 닫지 않음)
- `VehicleSpec` — id, name, domain: Domain, speed_mps: float, endurance_min: float, sensor_range_m: float, capabilities: list[ActionKind], home: GeoPoint
- `VehicleState` — id, t_ms, pos: GeoPoint, heading_deg: float, battery_pct: float, status: VehicleStatus, role_id: str|None, play_id: str|None, step_id: str|None, line_idx: int = 0, waypoint_idx: int = 0, emergency: EmergencyKind|None, resume_step_id: str|None

**작전·플레이**
- `Operation` — id, name, purpose, area: Polygon(표시용 작전 지역), zone: Polygon(작전 구역, 하한선 규칙 2, 상황판에서 수정 불가), vehicle_ids: list[str], started_ms: int|None
- `Role` — id, name, domains: list[Domain], required: list[ActionKind] (이 액션을 못 하는 기체는 후보에서 제외)
- `Condition` — kind: ConditionKind, params: dict[str, float|str]
- `Line` — kind: ActionKind, params: dict[str, float|str|list], cond: Condition|None = None, then_step: str|None = None (if_cond·wait_signal·report 분기 대상)
- `Choice` — id, label, step_by_role: dict[str, str] (역할 id → 시작할 step id. 결정 한 번이 여러 역할을 움직이는 자리)
- `Step` — id, role_id, name, lines: list[Line], choices: list[Choice] = [] (lines에 report/require_approval이 있을 때), next_step: str|None, ui: dict = {} (편집기 좌표, 엔진은 읽지 않음)
- `EmergencyRules` — battery_low_pct: float = 30, link_lost_step: str|None, battery_low_step: str|None, operator_call_step: str|None
- `Play` — id, name, roles: list[Role], steps: list[Step], emergency: EmergencyRules, entry: dict[str, str] (역할 id → 첫 step id), origin: "human"|"ai_draft", approved: bool = False, template: bool = False
- `ValidationIssue` — code: str, step_id: str|None, line_idx: int|None, message: str
- `PlayCheck` — ok: bool, issues: list[ValidationIssue], est_return_battery: dict[str, float] (역할 id → 예상 귀환 배터리 %)

**명령과 하한선**
- `Provenance` — source: CommandSource, play_id: str|None, step_id: str|None, line_idx: int|None, decision_id: str|None, injection_id: str|None, operator_id: str|None, issued_ms: int
- `Command` — id, vehicle_id, kind: CommandKind, params: dict (target: GeoPoint | route: list[GeoPoint] | target_id | distance_m 등), provenance: Provenance|None
- `PassedCommand` — command: Command, checks: list[str] (통과한 규칙 이름 3개), passed_ms: int. **safety 모듈의 `check_command`만 만든다.** 다른 곳에서 생성하는 테스트를 두어 막는다(파이썬이라 타입으로 강제되지 않음, 테스트와 리뷰로 지킴)
- `Block` — command_id, vehicle_id, reason: BlockReason, detail: str, alternative: Command|None, t_ms

**감지·보고·결정**
- `Target` — id, kind: TargetKind, pos: GeoPoint, vel_east_mps: float, vel_north_mps: float, first_seen_ms, last_seen_ms, seen_by: list[str]
- `Report` — id, t_ms, kind: ReportKind, vehicle_id: str|None, target_id: str|None, role_id: str|None, text: str, choices: list[Choice] = [], resolved_ms: int|None, decision_id: str|None
- `Decision` — id, t_ms, report_id, choice_id, operator_id = "op1"
- `Assignment` — role_id, vehicle_id, since_ms, reason: str (거리·배터리 점수 설명 한 줄)
- `Injection` — id, play_id, anchor: dict (target_id 또는 zone Polygon), proposed: list[Assignment], status: "pending"|"approved"|"rejected", t_ms
- `DirectControl` — vehicle_id, target: GeoPoint, t_ms (운용자 직접 조종 입력)

**측정·프레임**
- `Metrics` — operator_actions: int, manual_baseline_actions: int, open_reports_max: int, role_gap_ms: int, blocked_commands: int, decisions: int, commands_sent: int, mission_success: bool|None
- `Frame` — t_ms, mode: RunMode, vehicles: list[VehicleState], targets: list[Target], reports: list[Report], assignments: list[Assignment], blocks: list[Block], injections: list[Injection], metrics: Metrics, log: list[str] (이 틱에 생긴 기록 줄)

**시나리오(sim 입력)**
- `ScenarioEvent` — t_ms, kind: "spawn_target"|"target_move"|"vehicle_link_lost"|"vehicle_battery_set"|"split_target", params: dict
- `Scenario` — id, operation: Operation, vehicles: list[VehicleSpec], plays: list[Play], events: list[ScenarioEvent], seed: int, tick_ms: int = 200, speed: float = 1.0

**엔진 입력(틱마다)**
- `TickInputs` — decisions: list[Decision], direct: list[DirectControl], injections: list[Injection](승인/거부 상태 변화), mode: RunMode

### 2.3 지표 정의(발표에서 그대로 말할 문장)
- `operator_actions`: 운용자가 누른 횟수. 결정 + 직접 조종 + 주입 승인·거부.
- `manual_baseline_actions`: 같은 대본에서 기체별 직접 조종이었다면 사람이 내려야 했을 명령 수. 정의 = 엔진이 만든 `Command` 수(출처가 play_step·emergency인 것) + 보고 카드 수. 사람이 실제로 조작한 값이 아니라고 발표에서 말한다.
- `open_reports_max`: 미해결 보고 카드가 동시에 떠 있던 최대 개수.
- `role_gap_ms`: 역할에 배정된 기체가 없던 시간의 합. 기체 이탈 틱부터 이어받은 기체의 첫 `PassedCommand` 틱까지.
- `mission_success`: 시나리오가 정한 조건(선박 식별 보고가 처리됨)을 끝까지 만족했는가.

---

## 3. 모듈별 목표·방향·공개 API·완료 기준

형식: 목표(한 줄) / 방향(어떻게) / 공개 API(`from modules.<m> import ...`) / 완료 기준 / 하지 않는 것 / 담당.

### 3.1 contracts (리드)
- 목표: 2절을 그대로 `contracts/models.py`에 옮기고 `contracts/examples/*.json`과 `contracts.gen.ts`를 만든다.
- 방향: 기존 Detection·Track·Assessment·Response는 지우지 않고 남긴다(tracking·assess·respond 휴면용). 새 모델을 추가하고 `ALL_MODELS`에 등록.
- 완료 기준: 예시 JSON이 전 모델에 하나씩 있고 `gen_contracts.py`가 통과. 12:00 전에 끝낸다(10/9 밤 작성 권장).
- 하지 않는 것: 모델 상속, Optional 남발. 필드 추가는 리드만.

### 3.2 play (팀원 3, 새 모듈)
- 목표: 플레이 파일을 읽고·검사하고·기체 명령으로 펼치고·AI 초안을 만든다.
- 방향:
  - 저장 전 검사 4종: 로직 오류(끊긴 next_step, 닿을 수 없는 step, 끝나지 않는 loop, 송신 없는 wait_signal), 보고·승인 지점 누락(target_found 뒤에 report 없이 approach_target로 가는 경로), 귀환 배터리(각 역할의 경로 길이와 VehicleSpec 평균으로 추정), 작전 구역 밖 경로점.
  - 펼치기 표: `(ActionKind, Domain) -> CommandKind | None`. 표는 JSON 하나(`modules/play/expand_table.json`). None이면 그 기체는 그 역할 후보에서 빠진다.
  - AI 초안: 문장 + 어휘(ActionKind·ConditionKind) + Play JSON 스키마를 LLM에 주고 구조화 출력만 받는다. 스키마 밖이면 버리고 한 번 재요청. `origin="ai_draft", approved=False`로 돌려준다. 응답은 `demo/plays/cache/<sha256(prompt)>.json`에 저장하고, 캐시가 있으면 호출하지 않는다. API 키는 `.env`.
  - 템플릿 2개를 손으로 쓴다: 해안 경계(역할 3: AIR 순찰·SEA 확인·GROUND 상륙 감시), 고속 보트 추적(역할 1: AIR 추적).
- 공개 API: `load_play(path) -> Play`, `check_play(play, op: Operation, specs) -> PlayCheck`, `expand_line(line, domain) -> CommandKind|None`, `draft_play(text, op) -> Play`, `list_templates() -> list[Play]`
- 완료 기준: 템플릿 2개가 `check_play` 통과. 보고 지점을 뺀 플레이는 실패. AI 초안이 캐시로 재현. 전부 순수 함수, 예시 JSON으로 테스트.
- 하지 않는 것: 서명, 버전 관리, 플레이 간 참조.

### 3.3 runtime (팀원 2, 새 모듈)
- 목표: 틱마다 기체별 현재 (플레이, step, 줄)을 한 줄 진행해 `Command`를 만들고, 보고·결정·이어받기·주입·직접 조종·비상을 처리하며 지표를 센다.
- 방향:
  - 상태 기계는 `VehicleState`의 play_id/step_id/line_idx다. 한 틱에 한 줄. 줄의 cond가 거짓이면 그 줄에 머문다.
  - 액션 15개 중 시연에 필요한 것부터: move_to, patrol_route, watch_target, approach_target, report, require_approval, return_home, if_cond(target_found·arrived·battery_below). 나머지(search_area, relay_comms, loop, wait, send_signal, wait_signal, watch_point)는 빼는 순서 뒤쪽.
  - 보고 → 결정: `report` 줄은 `Report`를 만들고 그 기체는 멈춘다. `Decision`이 오면 `Choice.step_by_role`대로 각 역할의 기체를 해당 step으로 옮긴다(주인공 장면).
  - 배정: 역할마다 후보(domains ∩ capabilities 충족) 중 거리·배터리 점수 최고. `Assignment.reason`에 한 줄 설명.
  - 이어받기: 기체가 returning·lost·maintenance가 되면 같은 역할 후보 중 다시 배정. 없으면 `role_gap` 보고 카드와 `role_gap_ms` 누적. 영역을 넘는 이어받기는 하지 않는다.
  - 주입: `Injection`은 pending으로 들어오고 승인될 때까지 명령을 만들지 않는다(출처 없음). 승인되면 proposed대로 배정하고 원래 step은 resume_step_id에 보관.
  - 직접 조종: `DirectControl`은 `Command(kind=move, provenance.source=operator_direct)`. 도착하면 resume_step_id로 복귀.
  - 비상: battery_below(EmergencyRules.battery_low_pct)·link_lost·operator_call → 지정 step으로, 끝나면 resume.
  - 수동 기준선: `mode=manual_baseline`일 때도 같은 틱을 돌리되 `manual_baseline_actions`를 2.3 정의대로 센다. 두 모드를 같은 seed로 돌려 Metrics를 나란히 둔다.
- 공개 API: `step_vehicles(state, plays, inputs, t_ms) -> (state, list[Command], list[Report])`, `assign_roles(play, specs, states, op) -> list[Assignment]`, `apply_decision(state, play, decision) -> state`, `apply_injection(...)`, `update_metrics(metrics, frame_parts) -> Metrics`
- 완료 기준: 통합 1 슬라이스(4절). 결정 한 번에 역할 3개가 함께 step을 바꾸는 테스트. 역할 공백 시간이 세어지는 테스트.
- 하지 않는 것: 경로 계획(직선만), 충돌 회피, 영역 넘는 이어받기.

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
- 방향: 2D 등속 직선 이동, 배터리는 `100 / endurance_min` %/분 선형. orbit은 반지름 고정 원운동, keep_distance는 표적과 거리 유지, follow_route는 경로점 순회. 사건 대본의 `ScenarioEvent`를 t_ms에 적용(표적 출현·이동·분리, 기체 link_lost, 배터리 강제 설정).
- 공개 API: `load_scenario(path) -> Scenario`(기존 유지, 모델 교체), `advance(states, specs, passed: list[PassedCommand], dt_ms) -> states`, `apply_events(scenario, states, targets, t_ms) -> (states, targets)`
- 완료 기준: 명령 8종 각각 1틱 이동 테스트. 사건 5개 대본이 끝까지 돈다.
- 하지 않는 것: SITL, 물리, 바람·해류, 3D.

### 3.6 sensing (팀원 2, 고쳐 씀)
- 목표: 기체 센서 범위 안 표적을 "본 것"으로 표시하고 `target_found` 조건의 근거를 만든다.
- 방향: 거리 ≤ sensor_range_m이면 `Target.seen_by`에 기체 id 추가, last_seen_ms 갱신. 야간이라 범위를 줄인 값을 VehicleSpec에 직접 넣는다. 탐지 잡음은 없앤다(시연 재현성).
- 공개 API: `observe(states, specs, targets, t_ms) -> targets`
- 완료 기준: 범위 안·밖 테스트. 기존 Detection 기반 액션은 삭제하지 않고 파이프라인에서만 뺀다.

### 3.7 gateway (리드, 고쳐 씀)
- 목표: 엔진을 돌리고 화면과 주고받는다.
- 방향: `engine.tick`를 gateway의 `engine.py`에 두고 모듈 순서대로 부른다(로직 없음). 두 실행 경로: `/run/live`(0.2초 틱, WS로 Frame 전송), `/run/preview`(끝까지 돌려 Frame 목록 반환, UI가 배속 재생). 상태는 프로세스 메모리 하나(작전 1개).
- REST(확정): `GET/POST /plays`, `POST /plays/check`, `POST /plays/draft`, `GET/POST /operation`, `POST /run/live`, `POST /run/preview`, `POST /run/reset`, `POST /decisions`, `POST /direct`, `POST /injections`, `POST /injections/{id}/approve|reject`, `POST /mode` (role|manual_baseline), `POST /run/jump?t_ms=` (발표용 "다음 사건으로"). WS `/ws`: Frame.
- 완료 기준: smoke가 사건 5개 대본을 두 모드로 돌려 Metrics 두 벌을 낸다. 리셋 뒤 같은 seed로 같은 결과.
- 하지 않는 것: 인증, 다중 작전, 영속 저장.

### 3.8 cop-ui (map·live·replay 리드, editor·setup 팀원 3)
- 목표: 화면 2개. 편집기(설정 포함)와 상황판.
- 방향:
  - 편집기: React Flow를 쓰지 않는다. 역할별 세로 열에 step 카드, 카드 안 줄 목록, 연결은 드롭다운(next_step·then_step·choice). 상단에 AI 초안 입력 칸. 저장 버튼이 `/plays/check` 결과를 카드 옆에 표시. 작전 설정(이름·작전 구역 그리기·기체 선택)은 편집기 왼쪽 패널.
  - 상황판: MapLibre + 백령도 위성 타일(로컬 캐시, 결정 0004·0001), 기체·표적·작전 구역·경로, 오른쪽에 카드 열(보고·역할 공백·승인 대기·차단), 카드의 선택지 버튼이 `/decisions`. 직접 조종은 기체 클릭 후 지도 클릭. 아래에 지표 패널: 역할 모드와 수동 기준선 나란히. 발표용 배속과 "다음 사건으로".
  - 미리 보기(시뮬레이션 화면)는 별도 화면이 아니라 상황판의 재생 모드.
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
손으로 쓴 플레이 JSON → `check_play` 통과 → `/run/live` → 드론이 순찰 → 표적 출현(사건 1) → `target_found` → `report` 줄 → Report 카드가 WS Frame에 실림 → `/decisions`로 선택 → 역할 3개의 기체가 각자 step으로 이동 → `check_command`가 전부 통과 → 지도에 세 기체가 움직임. Metrics에 operator_actions=1이 찍힘.

**통합 2 (10/11 00:00)** — 화면 조작만으로.
편집기에서 AI 초안 입력 → 검사 실패 카드(보고 지점 없음) → 카드 추가 → 저장 통과 → 상황판에서 실행 → 사건 1·2·3(귀환·이어받기·역할 공백 카드)·4(주입 승인 대기 → 승인)·6(구역 밖 차단·배터리 차단) → 지표 패널에 두 모드 나란히 → 3분 안에 리허설 1회.

**동결 (10/11 06:00)** — `KDTH_FREEZE=1`. 이후 데이터·문구·대본만.

---

## 4.5 어디까지 대본이고 어디부터 계산인가

심사에서 "그거 계산된 겁니까?"에 답할 선. 세 층으로 나누고, 발표와 `demo/BUILT_HERE.md`에 같은 말로 적는다.

| 층 | 내용 | 시연에서 | 왜 |
|---|---|---|---|
| **대본(입력)** | 사건 5개의 시각·위치(표적 출현·분리, 드론 1 배터리 강제 설정), 기체 제원 5개, 작전 구역 폴리곤, 템플릿 플레이 2개 | `Scenario` JSON 파일. 화면 기록 줄에 `[대본]` 표시 | 공개·가상 데이터 정책. 환경은 우리가 정하는 것이 맞다 |
| **계산(엔진)** | 기체 이동·배터리, 센서 범위 탐지, step 진행, 보고 카드 생성, 배정과 이어받기, 역할 공백, 주입 승인 대기, 직접 조종, 하한선 규칙 3개와 대안 지점, 지표 전부(두 모드) | 틱마다 실제로 계산. 같은 seed면 같은 결과 | 이것이 "계산·측정·보장"이다. 여기에 고정값을 넣는 순간 SUPPORTY와 같아진다 |
| **캐시(외부 응답)** | AI 초안의 LLM 응답 2개, 백령도 위성 타일 | 파일에서 읽음. 캐시 미스면 라이브 호출, 실패하면 템플릿으로 대체하고 화면에 표시 | 결정 0001의 "끊겨도 이어감" |

**하지 않는 것(연출 금지 목록).** 아래가 하나라도 들어가면 심사 질의에서 무너진다.
- 보고 카드를 시각으로 띄우기(예: T+11분에 카드 생성). 카드는 `target_found` 조건이 센서 범위 계산으로 참이 될 때만 생긴다. 대본은 표적을 그 시각에 그 위치에 놓을 뿐이다.
- 배정을 시나리오 파일에 적어 두기. 배정은 거리·배터리 점수로 계산하고 `Assignment.reason`에 근거를 쓴다. 빼는 순서 4번(고정 배정)으로 내려갈 때만 예외이고, 그때는 발표에서 "배정은 고정"이라고 말한다.
- 지표를 손으로 적기. 두 모드의 숫자는 같은 seed로 돌린 Metrics에서만 나온다.
- 차단 카드를 직접 조종 입력에 붙여 두기. 차단은 safety가 실제로 규칙을 평가한 결과여야 한다. 시연 대본은 운용자가 어디를 찍을지만 정한다.
- 사건 2의 "결정 한 번에 세 기체 이동"을 기체별 이동 명령 3개로 미리 적어 두기. 이동은 `Choice.step_by_role`과 runtime의 step 전이에서 나와야 한다.

**발표에서 말할 문장.** "사건의 시각과 위치는 우리가 정한 대본입니다. 그 뒤의 탐지·보고·배정·차단·숫자는 전부 엔진이 틱마다 계산한 것이고, 같은 시드로 다시 돌리면 같은 결과가 나옵니다. AI 초안 응답과 지도 타일은 행사장 인터넷 때문에 미리 받아 둔 캐시입니다."

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

| 파트 | 담당 | 모듈 | 첫 사이클에서 끝낼 것 |
|---|---|---|---|
| 1 | 리드 | contracts, gateway, cop-ui map/live, demo | contracts 확정(10/9 밤), gateway 틱 루프와 WS, 백령도 타일, 시나리오 데이터 |
| 2 | 팀원 2 | sim, sensing, runtime, safety | sim 이동·배터리, safety 규칙 3, runtime 한 줄 진행과 report→decision |
| 3 | 팀원 3 | play, cop-ui editor/setup | 플레이 형식 로드·검사, 템플릿 2개, 편집기 카드 열 |

도움 가능(순수 함수): play 검사 4종, safety 규칙 3개, runtime 배정 점수, Metrics 집계, 펼치기 표. 막히면 5분 안에 "막힘: 모듈, 함수, 증상"을 채팅에.

---

## 7. 빼는 순서(늦어질 때, 앞에서부터)

1. 작전 설정 패널(기체 선택은 시나리오 파일 고정값으로)
2. 액션 뒤쪽 7종(search_area, relay_comms, loop, wait, send_signal, wait_signal, watch_point)
3. 비상 규칙 link_lost·operator_call(battery_low만 남김)
4. 배정 점수(고정 배정 + reason 문장)
5. 미리 보기 재생(라이브만)
6. AI 초안 라이브 호출(캐시 응답만, 입력 칸은 유지)
7. 편집기 카드 편집(읽기 전용 카드 + 저장 검사만)

끝까지 남기는 것: 결정 한 번에 세 역할 이동, 보고 카드, 이어받기와 역할 공백 카드, 주입 승인 대기, 구역 밖·배터리 차단, 지표 두 모드 나란히.

---

## 8. 대회 전(10/9 밤) 할 일

1. 2절을 `contracts/models.py`로 옮기고 예시 JSON·TS 생성.
2. 백령도 위성 타일 캐시(Esri 또는 VWorld, bbox 124.55~124.85E / 37.88~38.02N, z8~16 약 2,500장). 이용 약관 확인.
3. `modules/cop-ui/AGENTS.md`·루트 AGENTS.md 소유 표 수정(팀원 4 → 실제 배정, 외부 네트워크 문구).
4. `new_module.py`로 play·runtime·safety 뼈대 생성.
5. 템플릿 플레이 2개와 사건 5개 대본을 JSON으로.
6. AI 초안 프롬프트와 캐시 2개 생성(인터넷 되는 곳에서).

---

## 9. 알려진 구현 위험(다음 세션 공격 대상)

- runtime의 "한 틱에 한 줄" 규칙이 report 대기·조건 대기와 섞일 때 상태 전이가 꼬일 수 있다.
- safety 규칙 3(배터리)의 추정식이 orbit·keep_distance처럼 목적지가 없는 명령에 애매하다.
- 수동 기준선 정의(2.3)가 심사위원에게 "지어낸 숫자"로 보일 수 있다.
- 두 모드를 같은 seed로 돌릴 때 결정 입력을 어떻게 재생하는가(결정 시각을 대본에 넣어야 함).
- 80줄 제한이 runtime 상태 기계를 과도하게 쪼개게 만들 수 있다.
- 백령도 타일 캐시의 약관과 용량.
- 3명 중 React 경험자가 없으면 파트 3이 막힌다.

---

## 10. 다음 세션 devil-advocate 주장 블록 초안

```
CLAIM: 이 문서(09)의 모듈 경계·데이터 형식·통합 슬라이스대로 가면 3명이 10/10 18:00 통합 1과
  10/11 00:00 통합 2를 넘기고, 동결 뒤 3분 시연이 화면 조작만으로 재현된다.
EVIDENCE FOR: (1) 엔진 함수가 전부 순수 함수이고 예시 JSON으로 테스트 가능. (2) 통합 1은 편집기 없이
  정의돼 가장 큰 위험(UI)을 뒤로 뺐다. (3) 저장소에 gateway·WS·지도·guard·테스트 골격이 돌고 있다
  (smoke·pytest 통과). (4) 빼는 순서 7단계가 있다.
COST IF WRONG: 24시간과 단일 제출 기회. 통합 1 실패 시 시연 자체가 없다.
LOAD-BEARING ASSUMPTION: runtime(한 줄 진행 + 보고/결정 + 이어받기 + 주입 + 직접 조종 + 비상 + 지표)을
  팀원 한 명이 80줄 액션들로 쪼개 10/10 15:00~21:00 안에 통합 1 수준까지 만든다.
```
