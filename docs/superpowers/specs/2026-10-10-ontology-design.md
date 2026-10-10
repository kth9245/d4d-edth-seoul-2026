# 작전 온톨로지(기체 종류 계층·능력 추론) + 객체 그래프 설계

2026-10-10 KST · 결정 0038(범위 A + B) · 관련 0035(시나리오 원본은 JSON), 0036(시연 B안), 0037(VehicleSpec.recharge_min, 같은 파일) · 할 일 Part1-24 · 담당: 리드(계약·ontology 모듈·gateway·cop-ui·시나리오), 황승주(play 메시지, 알림), 최동호(sim 로더·engine.py 기록, 알림)

## 1. 목적과 완료 기준

"ROLECALL의 플레이는 작전 온톨로지 위에서 쓰인다"고 발표에서 말할 수 있게 한다. 심사 질문을 버티려면 세 가지가 있어야 한다.

1. 종류 계층(is-a)이 데이터로 적혀 있다.
2. 시스템이 그 계층을 따라가 실제 판정을 한다(추론). 검사기와 화면이 같은 추론 코드를 쓴다.
3. 작동하는 화면에서 보인다(NO SLIDES).

완료 기준:
- 시연 시나리오 기체 5대의 `capabilities`가 JSON에 손으로 적히지 않고 계층에서 계산된다. 계산 결과는 2절 표와 같다.
- 편집기에서 d1의 플레이에 `strike_target` 카드를 넣고 저장하면 검사가 막고, 메시지에 "정찰 드론 → 공중 기체 → 기체" 경로가 나온다.
- 편집기 사이드바 "온톨로지"에서 계층도와 기체별 판정(경로 포함)과 예비 자격이 보인다.
- 상황판에서 무력화 카드의 "연결 보기"를 누르면 표적 → 보고 카드 → 결정 → 타격 명령(통과한 검사) → 기체 그래프가 보인다.
- 시연 3분 대본은 그대로 끝까지 돈다(smoke·엔진 테스트 통과).

용어: 이 설계의 온톨로지는 경량 온톨로지(lightweight ontology)다. OWL 파일·범용 추론기는 쓰지 않는다. 판정은 닫힌 세계 가정(계층 어디에도 없으면 "못 함")이다. 명령을 내보내는 검사라 허용 목록 방식이 맞다.

## 2. 종류 계층과 능력 (사람 확정 "ㄱㄱ")

행동 묶음:

| 묶음 id | 이름 | 행동 |
|---|---|---|
| `move` | 이동 | `move_to`, `patrol_route`, `return_home`, `hold` |
| `watch` | 감시 | `watch_target`, `watch_point`, `search_area` |
| `approach` | 접근 | `approach_target` |
| `relay` | 통신 중계 | `relay_comms` |
| `strike` | 타격 | `strike_target` |

기체 종류:

| 종류 id | 이름 | 상위(`is_a`) | 더하는 능력(`provides`) | 물려받은 것까지 | 기체 |
|---|---|---|---|---|---|
| `vehicle` | 기체 | — | `move` | 이동 | |
| `air_vehicle` | 공중 기체 | `vehicle` | `watch`, `approach`, `relay` | 이동·감시·접근·통신 중계 | |
| `recon_drone` | 정찰 드론 | `air_vehicle` | — | 공중 기체와 같음 | d1, d3 |
| `armed_drone` | 무장 드론 | `air_vehicle` | `strike` | + 타격 | d2 |
| `sea_vehicle` | 해상 기체 | `vehicle` | `watch`, `approach` | 이동·감시·접근 | |
| `armed_usv` | 무장 수상정 | `sea_vehicle` | `strike` | + 타격 | usv |
| `ground_vehicle` | 지상 기체 | `vehicle` | `watch_point`(행동 하나) | 이동·지점 감시 | |
| `ground_robot` | 지상 로봇 | `ground_vehicle` | — | 지상 기체와 같음 | ugv |

`provides`의 원소는 묶음 id 또는 행동 이름이다(지상 기체처럼 묶음의 일부만 줄 때).

시연 확인(2026-10-10 시나리오 기준): 기체마다 받을 수 있는 플레이(assign·선택지·전환 버튼·예비)가 쓰는 행동은 d1·d3 `hold patrol_route return_home watch_target`, d2 + `strike_target`, usv `approach_target hold return_home strike_target watch_target`, ugv `hold move_to return_home`으로 모두 표 안이다. 새로 막히는 것: d1·d3의 타격, ugv의 표적 감시·구역 탐색·접근·통신 중계·타격. AI 초안 시연 문장("드론으로 … 접근해서 따라붙어")의 드론 `approach_target`은 공중 기체가 가진다.

표적 종류 계층(선박 > 보트·고속정)은 만들지 않는다. 그 계층을 쓰는 규칙이 없다.

## 3. 계약 (리드, 한 커밋)

새 파일 `contracts/models/ontology.py`:

```python
class ActionGroup(BaseModel):
    id: str
    label: str
    actions: list[ActionKind]

class VehicleKind(BaseModel):
    id: str
    label: str
    is_a: str | None = None
    provides: list[str] = []  # ActionGroup id or ActionKind value

class Ontology(BaseModel):
    groups: list[ActionGroup]
    kinds: list[VehicleKind]

class CapabilityReason(BaseModel):
    action: ActionKind
    allowed: bool
    path: list[str]  # kind ids walked from the vehicle's kind up to the giver (allowed) or the root (denied)
    via: str | None = None  # the provides entry that matched (group id or action)

class VehicleCapabilities(BaseModel):
    vehicle_id: str
    kind: str
    reasons: list[CapabilityReason]  # one per ActionKind, in enum order

class OntologyView(BaseModel):  # GET /ontology
    ontology: Ontology
    vehicles: list[VehicleCapabilities]

class ObjectNode(BaseModel):
    id: str
    type: Literal["vehicle", "target", "report", "decision", "command", "block"]
    label: str
    t_ms: int | None = None

class ObjectLink(BaseModel):
    src: str
    dst: str
    rel: Literal["reported", "about", "answers", "from_decision", "sent_to", "aims_at", "blocked"]

class ObjectGraph(BaseModel):  # GET /graph
    focus: str
    nodes: list[ObjectNode]
    links: list[ObjectLink]
```

기존 모델에 더함:

| 모델 | 칸 | 뜻 |
|---|---|---|
| `VehicleSpec` | `kind: str \| None = None` | 종류 id. JSON에 손으로 적는다 |
| `VehicleSpec` | `kind_path: list[str] = []` | 종류부터 맨 위까지의 이름(예: `["정찰 드론", "공중 기체", "기체"]`). 로더가 채운다 |
| `VehicleSpec` | `capabilities: list[ActionKind] = []` | 기본값만 추가. `kind`가 있으면 로더가 계층에서 채운다 |
| `Scenario` | `ontology: Ontology \| None = None` | 없으면 지금처럼 손으로 적은 capabilities를 쓴다(24시간 시나리오, 결정 0037) |

- `check.sh`가 `contracts/schema/`·`contracts.gen.ts`를 다시 만든다. 새 모델마다 `contracts/examples/<snake>.json`을 `scripts/gen_examples.py`로 만든다.
- 결정 0037이 `VehicleSpec.recharge_min`을 같은 파일에 더한다. rebase 충돌이면 두 줄 다 살린다.
- `contracts/API.md`: 1절 개념 표에 "온톨로지" 행, 3절 공개 API에 ontology 모듈과 로더 동작, 5절에 `GET /ontology`·`GET /graph`.

## 4. 추론: 새 모듈 `modules/ontology` (리드, 접두사 ONT)

`uv run python scripts/new_module.py ontology ONT`. 액션(1 액션 = 1 파일 = 1 테스트):

| 액션 | 서명 | 하는 일 |
|---|---|---|
| `kind_chain` | `(kind: str, onto) -> list[VehicleKind]` | 종류부터 `is_a`를 따라 맨 위까지 |
| `explain_capability` | `(kind: str, action: ActionKind, onto) -> CapabilityReason` | 체인을 아래부터 올라가며 `provides`에 그 행동 또는 그 행동을 담은 묶음이 있는 첫 종류에서 멈춤. 없으면 `allowed=False`, path = 체인 전체 |
| `infer_capabilities` | `(kind: str, onto) -> list[ActionKind]` | 행동 enum 순서로 `explain_capability`가 허용한 것만 |
| `fill_vehicle_kinds` | `(sc: Scenario) -> Scenario` | `sc.ontology`가 있으면 `kind`가 있는 기체의 `capabilities`·`kind_path`를 채운 새 Scenario |
| `ontology_view` | `(sc: Scenario) -> OntologyView` | 기체마다 행동 10개의 `explain_capability` |

공개 API(`modules/ontology/__init__.py`): 위 다섯 개.

## 5. 부르는 곳

| 곳 | 담당 | 바뀌는 것 |
|---|---|---|
| sim `load_scenario_json` | 최동호(알림) | 검증 통과 뒤 `return fill_vehicle_kinds(sc)`. 서버·smoke·예시 생성·테스트가 같은 계산 결과를 본다 |
| play `check_play` | 황승주(알림) | 판정(`s.do.kind not in sp.capabilities`)은 그대로. `sp.kind_path`가 있으면 메시지를 `"{vid}는 {action}를 못 함: {' → '.join(kind_path)} 어디에도 이 능력 없음"`으로. 없으면 지금 메시지 |
| gateway `GET /ontology` | 리드 | `ontology_view(scenario)`. 시나리오에 온톨로지가 없으면 404 |
| 시나리오 JSON | 리드 | `ontology` 칸(2절 그대로) 추가, 기체 5대에 `kind`, 기체 `capabilities` 목록 삭제. Part1-23.4(같은 파일)와 겹치지 않게 이 두 곳만 고친다 |
| 로더를 거치지 않고 JSON을 바로 읽는 곳 | 리드 | capabilities를 지우면 이곳들의 기체는 능력이 빈 목록이 된다. `scripts/example_world.py`(예시 생성)는 `fill_vehicle_kinds`를 거치게, `modules/gateway/tests/test_app.py`(검사 결과를 봄)는 실제 로더를 쓰게 고친다. `test_live.py`·mavlink·draft 테스트·`make_draft_cache.py`는 작전·플레이만 써서 그대로 |

## 6. 객체 그래프

### 6.1 기록 (gateway, `engine.py`는 최동호 틱 루프라 알림)

지금 Frame과 EngineState에는 운용자 결정 목록이 없고, 명령은 기체마다 실행 중인 것(`active`) 하나뿐이라 지나간 명령의 출처가 사라진다. `EngineState`(계약 아님)에 기록 세 칸을 더한다.

- `decisions: list[Decision] = []` — 틱에 들어온 `inputs.decisions`를 덧붙임
- `commands: list[Command] = []` — 그 틱의 `cmds`(통과·차단 모두)
- `passed: list[PassedCommand] = []` — 그 틱의 `passed`

`init_engine`은 빈 목록으로 시작한다. `engine.py`는 `replace(...)`에 세 칸을 더하는 것만 바뀐다(호출 순서 그대로).

### 6.2 `build_object_graph(es, focus) -> ObjectGraph` (새 gateway 액션, 번호는 new_action.py가 매김)

노드:

| type | 출처 | id | label |
|---|---|---|---|
| vehicle | `es.specs` | 기체 id | `"d2 · 무장 드론"`(kind_path 첫 이름, 없으면 spec.name) |
| target | `es.targets` | 표적 id | `"fast1 · 고속정"`, 무력화면 `" · 무력화"`. t_ms = neutralized_ms 또는 first_seen_ms |
| report | `es.reports` | 보고 id | 보고 `text` |
| decision | `es.decisions` | 결정 id | `"dec-4 '함께 타격'"`(답한 카드의 선택지 이름) |
| command | `es.commands` | 명령 id | `"strike · d2 · 출처·구역·배터리 통과"`(통과면 검사 이름, 차단이면 `"차단"`) |
| block | `es.blocks` | `"blk-" + command_id` | 차단 사유 `detail` |

링크(`src → dst`):

| rel | 화면 이름 | 만드는 규칙 |
|---|---|---|
| `reported` | 보고함 | 기체 → 보고(`report.vehicle_id`) |
| `about` | 이 표적 | 보고 → 표적(`report.target_id`) |
| `answers` | 답함 | 결정 → 보고(`decision.report_id`) |
| `from_decision` | 이 결정에서 나옴 | 명령 → 결정(`provenance.decision_id`) |
| `sent_to` | 이 기체에 | 명령 → 기체(`command.vehicle_id`) |
| `aims_at` | 겨눔 | 명령 → 표적(`params.target_id`) |
| `blocked` | 막음 | 차단 → 명령(`block.command_id`) |

펼치기: `focus`에서 시작해 링크를 방향 없이 따라간다. 기체 노드와 focus가 아닌 표적 노드는 끝(더 펼치지 않음)이다. 기체는 자기 명령 전부와 이어져 있어, 거쳐 펼치면 관계없는 명령이 모두 딸려 온다. 없는 focus면 ValueError(엔드포인트는 404).

### 6.3 `GET /graph?focus=<id>` → `ObjectGraph` (리드)

## 7. 화면 (cop-ui, 리드)

### 7.1 편집기 사이드바 "온톨로지" (작전 개요 바로 아래)

- 위: 계층도(들여쓰기 나무). 종류마다 `[더하는 능력 묶음 이름]`과 그 종류의 기체 id. 옆에 행동 묶음 표.
- 아래: 기체 고르기(d1 d2 d3 usv ugv) → 행동 10개마다 ✓/✗와 경로 한 줄(`정찰 드론 → 공중 기체 (감시 묶음)`, `정찰 드론 → 공중 기체 → 기체, 어디에도 없음`).
- 예비 자격 한 줄: `op.reserve`의 예비마다 "d3는 d1의 예비. d1의 플레이가 쓰는 행동 N개를 d3가 모두 할 수 있음(같은 정찰 드론)". 화면 계산(엔진 동작은 그대로, 결정 0038).
- 데이터: `GET /ontology` 하나. 순수 함수(나무 줄 만들기, 경로 문구, 예비 자격)는 vitest.

### 7.2 상황판 "연결 보기"

- 표적 발견 카드(`target_detected`)와 무력화 카드(`target_neutralized`)에 "연결 보기" 버튼. 누르면 `GET /graph?focus=<카드의 target_id>`를 한 번 받아 지도 칸 위에 겹친 창으로 그린다(닫기 버튼). 열린 뒤 실시간 갱신은 하지 않는다.
- React Flow(`@xyflow/react`, 이미 의존성). 열 고정: 기체 | 보고 카드 | 결정 | 명령 | 표적(차단은 명령 열 아래). 같은 열은 t_ms 순서로 위→아래. 좌표는 `playGraph.ts`처럼 직접 계산(순수 함수, vitest). 연결선에 rel 화면 이름.
- 지도 표적 마커는 그대로 클릭 통과(앞선 QA 수정 유지).

## 8. 시연 대본에 넣을 자리 (Part1-15)

- 편집기 장면 약 10초: d1 플레이에 타격 카드 → 저장 → 경로와 함께 막힘 → 사이드바 "온톨로지"에서 d1 판정.
- 마지막 무력화 장면 약 10초: 무력화 카드 "연결 보기" → "d2가 타격할 수 있었던 근거는 계층에, 실제로 타격한 근거는 이 연결에."

## 9. 테스트

- ontology 모듈: 액션마다 단위 테스트(2절 표의 계층으로 d1 watch_target 허용 경로, d1 strike_target 불가 경로, ugv watch_point 허용·watch_target 불가, infer 결과).
- 시나리오: `load_scenario_json(baengnyeong_night.json)`의 기체 5대 capabilities·kind_path가 2절 표와 같다. 기존 `check_operation` 통과·smoke 통과.
- play: kind_path가 있는 기체의 missing_capability 메시지에 경로.
- gateway: 엔진을 시연 시나리오로 돌려 결정·타격까지 간 EngineState에서 `build_object_graph(es, "fast1")`이 결정 → 타격 명령 → fast1 링크를 갖고 다른 표적의 명령을 펼치지 않는다. `GET /ontology`·`GET /graph` 응답 형식.
- 화면: vitest 순수 함수, `scripts/qa/editor.json`(온톨로지 칸·d1 타격 막힘 경로)·`scripts/qa/live.json`(무력화 카드 연결 보기) 점검 항목 추가 후 `scripts/qa.sh` 통과.

## 10. 순서와 나누기

1. 계약(3절) — 나머지 전부가 기댄다. 먼저 ship.
2. 동시에 진행 가능:
   - 가. ontology 모듈(4절) → 시나리오 JSON·로더·check_play 메시지·`GET /ontology`(5절)
   - 나. gateway 기록·`build_object_graph`·`GET /graph`(6절)
3. 화면(7절): 7.1은 가 뒤, 7.2는 나 뒤.
4. QA 점검 목록, `demo/BUILT_HERE.md`, `contracts/API.md` 마무리.

## 11. 범위 밖

표적 종류 계층, OWL·Turtle 내보내기, 규칙(check_play·safety)을 데이터로 옮기기, 예비 선택을 온톨로지 질의로 바꾸기, AI 초안 프롬프트 변경, 그래프 실시간 갱신, 지도 마커 클릭으로 그래프 열기, 그래프 노드를 눌러 다시 펼치기.
