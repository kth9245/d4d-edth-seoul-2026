# 타격 단계(정찰 → 추적 → 사람 허락 → 타격) 설계

2026-10-10 KST · 결정 0031(이 설계), 0003(하한선 규칙 3개), 0004(시나리오), 0005(연출 금지), 0016(전환·표적 선택) · 항목 Part1-18~20(리드), Part2-21~23(황승주), Part2-24(최동호)

## 1. 목적과 완료 기준

시연이 감시에서 끝나지 않고 "사람이 승인해야만 타격까지 가는 지휘 체계"로 보이게 한다. 정찰·추적은 이미 있는 장면이므로 끝에 '사람 허락 → 타격'을 붙인다.

- 완료 기준(통합 2, 10/11 00:00): 화면 조작만으로 s7(타격 승인 카드)과 s8(fast1 무력화, 작전 성공)이 나온다.
- 하한선: 운용자 결정(카드 선택지)이 붙지 않은 타격 명령은 safety가 막는다. 표적이 작전 구역 밖이면 승인해도 막힌다. 둘 다 엔진이 명령마다 계산한다(결정 0005 연출 금지).
- 통합 1(10/10 18:00)은 바뀌지 않는다.

## 2. 시연 장면 순서

| 장면 | 단계 | 내용 |
|---|---|---|
| s1 | 정찰 | 드론1 순찰 → boat1 탐지 → 보고 카드 |
| s2 | 추적 | '근접 확인' 결정 한 번 → 4대 동시 전환 |
| s3 | 추적 | 드론1 배터리 귀환 → 드론3 이어받기, 기체 공백 카드 |
| s5 | 하한선 | 순찰 중 드론2를 운용자가 NLL 너머로 직접 조종 → 구역 차단 → 대안 지점 |
| s6 | 하한선 | 먼 지점으로 직접 조종 → 배터리 차단 |
| s4 | 추적 | fast1 분리(해안을 따라 동쪽으로 우회) → '고속 보트 추적' 전환 승인 → 표적 선택 카드 2장(드론2·수상정) |
| s7 | 사람 허락 | 드론2·수상정이 fast1을 센서에 잡으면 각자 '타격 승인 요청' 카드 → '함께 타격' |
| s8 | 타격 | 두 기체가 fast1로 → 100 m 안에서 무력화 → 결과 카드, 작전 성공, 지표 |

s5·s6은 fast1과 떼어 s4 앞으로 옮긴다(장면 이름은 예시 파일과 맞추려고 그대로 둔다). 이 단계의 운용자 조작은 4번(전환 승인 1, 표적 선택 2, 함께 타격 1).

## 3. 계약 변경 (Part1-18, 리드, 한 커밋)

| 파일 | 추가 |
|---|---|
| `contracts/models/enums.py` | `ActionKind.strike_target`, `CommandKind.strike`, `ReportKind.target_neutralized` |
| `contracts/models/world.py` | `VehicleState.decision_id: str \| None = None` — 이 기체를 지금 플레이로 옮긴 운용자 결정 id |
| `contracts/models/events.py` | `Target.neutralized_ms: int \| None = None` — 무력화 시각 |
| `modules/play/actions/expand_action.py` 표 | `strike_target` → air `strike`, sea `strike`, ground 없음 |
| `modules/cop-ui/src/features/editor/describe.ts` | `ACTION_LABEL.strike_target = "표적 타격"` |
| `contracts/API.md` | 1절: 표적이 필요한 행동에 `strike_target`, 타격 명령의 결정 id 규칙. 2절: `mission_success` = 표적 하나라도 무력화. 3절: 8 다음에 sim `resolve_strikes` |

- 같은 커밋이어야 하는 이유: `modules/play/tests/test_expand_action.py`가 표에 `ActionKind` 전부가 있기를 요구하고, `describe.ts`의 `Record<ActionKind, string>`이 새 값을 요구한다. 따로 올리면 play 테스트나 TS 검사가 깨져 ship이 막힌다.
- 기본값 있는 추가라 기존 JSON·예시는 그대로 검증을 통과한다. `gen_contracts.py`(TS)와 `gen_examples.py`를 다시 돌린다.
- play 모듈(황승주) 파일을 고치므로 커밋 뒤 채팅으로 알린다.

## 4. 엔진

### 4.1 runtime (Part2-21, 황승주) — 기존 액션 수정

- `switch_play`(RT-09): 비우는 칸에 `decision_id: None`을 더한다. 전환 버튼·예비 이어받기로 바뀐 기체는 결정 id가 없다.
- `apply_decision`(RT-03): 선택지 `play_by_vehicle`로 옮긴 기체마다 `switch_play` 뒤에 `decision_id = decision.id`, `target_id = 보고 카드의 target_id`를 적는다. 옮긴 기체가 기다리던 다른 카드(선택지 있고 미처리, `vehicle_id`가 옮긴 기체)는 `resolved_ms = decision.t_ms`, `decision_id = decision.id`로 닫는다.
- `enter_step`(RT-08):
  - `TARGET_ACTIONS`에 `strike_target`.
  - `Provenance(..., decision_id=st.decision_id)`.
  - `strike_target`이면 명령 params에 표적의 현재 위치 `target`(GeoPoint dict)을 넣는다. safety 규칙 2·3이 이 값으로 걸린다.
  - 보고 카드의 `target_id`는 정해진 표적(`upd["target_id"]`)을 먼저 쓰고, 없을 때만 지금처럼 "처음 본 표적".
- 테스트: 결정 뒤 옮긴 기체의 `decision_id`·`target_id`, 다른 카드 닫힘, `switch_play`가 `decision_id`를 지움, 타격 step 진입 명령의 kind(공중·해상 strike)·출처 결정 id·params `target`, 보고 카드 표적이 추적 중 표적.

### 4.2 safety (Part2-22, 황승주) — `check_command`(SFT-03) 수정

- 규칙 1: `cmd.kind == strike`이고 출처가 없거나 `provenance.decision_id`가 없으면 `no_provenance`, detail "운용자 결정 없는 타격". 대안 없음.
- 규칙 2·3은 코드 그대로(params `target`이 있으므로 적용된다).
- 테스트: 결정 id 있는 타격 통과, 없는 타격 차단, 구역 밖 표적 위치의 타격은 `outside_zone`.

### 4.3 sim (Part2-23, 황승주, sim은 최동호 모듈 — 시작할 때 알림)

- `advance_vehicles`(SIM-08): `K.strike`를 `orbit_or_keep` 분기에 더한다(`distance_m` 0으로 표적에 붙는다).
- 새 액션 `resolve_strikes`(SIM-10): `(states, targets, t_ms) -> (targets, list[Report])`. 기체의 `active` 명령이 strike이고, 그 `target_id` 표적이 아직 무력화되지 않았고, 거리 ≤ 100 m이면 표적에 `neutralized_ms = t_ms`, 속도 0. 카드 `Report(id=rep-<기체>-<t_ms>, kind=target_neutralized, vehicle_id, target_id, text="<표적> 무력화(<기체>)")`, 선택지 없음. 같은 틱에 두 기체가 닿으면 카드는 처음 한 장만. `modules/sim/__init__.py`에 공개.
- `update_metrics`(RT-04, runtime): `outcome.targets`에 `neutralized_ms`가 있는 표적이 있으면 `mission_success = True`.
- 테스트: 100 m 안·밖, 이미 무력화된 표적은 카드 없음, 무력화 뒤 `apply_events`에서 표적이 멈춤, 작전 성공.

### 4.4 gateway (Part2-24, 최동호)

- `engine.py`: 8(advance) 다음에 `targets, hit = resolve_strikes(states, targets, t)`, `hit`을 이번 틱 새 카드와 전체 카드에 더한다. `TickOutcome.targets`는 이 뒤의 값.
- `tick_log`(GW-07): 통과한 strike 명령마다 "[계산] HH:MM 타격 명령 통과: <기체> → <표적>, 운용자 결정 <dec-N> 확인", 무력화 카드마다 "[계산] HH:MM <표적> 무력화(<기체>)".

## 5. 시나리오·플레이 (Part1-19, 리드)

`demo/scenarios/baengnyeong_night.json`과 `demo/plays/*.json`을 같이 고친다.

- 기체 제원: d1·d2·d3·usv `capabilities`에 `strike_target`(ugv는 없음). `check_play`가 받는 기체의 능력을 보므로 없으면 검사에서 거부된다.
- `split_target` 사건: fast1을 북쪽 대신 해안을 따라 동쪽으로(초기값 `ve` 6.0, `vn` -0.5). 바다 위인지 지도에서 확인하고 정확한 값은 Part2-19 튜닝.
- `op.switches`에 `{"id": "track_fast", "label": "고속 보트 추적", "play_by_vehicle": {"d2": "track_fast", "usv": "track_fast_sea"}}`.
- `track_fast`(air, 수정)와 `track_fast_sea`(sea, 새로): step 둘.
  - `track`: `watch_target {target: "operator", distance_m: 300}`, `on: [target_found → ask]`.
  - `ask`: `watch_target {target: "operator", distance_m: 300}`, `report {text: "타격 승인 요청", choices: [이 기체로 타격 {<자기>: strike}, 함께 타격 {d2: strike, usv: strike}]}`. 선택지 id는 `strike_d2`·`strike_usv`·`strike_both`.
- `strike`(air·sea, 새로): step 하나 `strike`: `strike_target {target: "operator", distance_m: 0}`, `on: []`. 표적은 `apply_decision`이 카드의 표적으로 정해 두므로 표적 선택 카드가 다시 뜨지 않는다.
- 확인: `check_operation` 통과(`ask`가 선택지 있는 보고라 승인 지점 검사도 통과).

## 6. 화면 (Part1-20, 리드)

- 지도: `neutralized_ms`가 있는 표적은 회색 X와 "무력화" 이름표.
- 카드 열: `target_neutralized`는 선택지 없는 알림 카드. 승인 카드는 기존 선택지 버튼 그대로.
- 지표 패널: `mission_success`가 참이면 "작전 성공".
- 예시: `scripts/example_scenes.py`에 `s7_strike_approval`(승인 카드 2장), `s8_neutralized`를 더하고, s5·s6을 순찰 중 드론2 기준으로 고친다. `gen_examples.py`.

## 7. 일정·담당·빼는 순서

| 순서 | 항목 | 담당 | 언제 |
|---|---|---|---|
| 1 | Part1-18 계약 | 리드 | 지금 |
| 2 | Part2-21 runtime, Part2-22 safety, Part2-23 sim | 황승주 | 1 뒤, 셋은 동시에 가능 |
| 3 | Part2-24 engine.py·기록 줄 | 최동호 | 틱 루프(Part2-17) 뒤, Part2-23 뒤 |
| 4 | Part1-19 시나리오·플레이 | 리드 | 2 뒤 |
| 5 | Part1-20 화면 | 리드 | 통합 1 뒤 |
| 6 | Part2-19 튜닝에 fast1 경로·타격 시점 | 최동호 | 통합 2 전 |
| 7 | Part1-15 3분 대본 새 순서 | 리드 | 동결 뒤 |

빼는 순서(늦으면 앞에서부터): ① 수상정 추적(드론2 단독 추적·타격, 선택지는 '타격' 하나) ② 결과 카드(기록 줄만). 승인 카드 → 타격 → 무력화는 끝까지 남긴다.

## 8. 하지 않는 것

- 저장 전 검사(편집기에서 승인 없는 타격 플레이 거부). 사람이 실행 중 검사만 골랐다.
- 명령을 낸 뒤 표적이 구역 밖으로 나가는 경우의 재검사. 명령을 낼 때 한 번만 본다.
- 부수피해 계산, 탄약 수, 타격 기체 손실, 경고 방송·경고 사격 단계.

## 9. 알려진 위험

- 승인 없는 타격은 시연 흐름에서 생기지 않아 차단 장면이 화면에 안 나온다. 통과 기록 줄로 검사가 있음을 보이고, 차단은 테스트와 발표 문장으로 말한다.
- 드론2가 fast1보다 boat1을 먼저 센서에 잡으면 '타격 승인 요청'이 일찍 뜬다. 카드의 표적은 추적 중 표적(fast1)이므로 동작은 맞고, 장면 시각만 튜닝에서 맞춘다.
- 실제 백령도 위성사진 위 선박 타격은 민감하게 보일 수 있다. 화면·발표에 "실제 지형 위 가상 상황, 가상 선박, 작전 구역 안에서만"을 적는다(결정 0004).
