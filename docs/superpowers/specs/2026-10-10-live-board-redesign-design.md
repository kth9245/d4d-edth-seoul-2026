# 상황판 개편 설계 (Part1-32)

2026-10-10 KST · 결정 0047(탐지 상태), 0048(함께 감시 범위·표적 지목), 0049(지목은 바로 승인) · 관련 0015(전환 미리 보기 뒤 승인), 0033(타격), 0040(정답은 화면에 내보내지 않음), 0046(정해진 선택지 먼저) · 담당: 리드(계약·gateway·cop-ui), 최동호(sensing), 황승주(runtime)

시안: 실제 엔진 Frame(결정 0046 흐름)으로 그린 1366×768 목업을 리드가 장면별로 보고 고쳤다(브레인스토밍 세션, 시안 v17).

## 1. 목적과 완료 기준

리드: "상황판이 너무 정신 없고 한눈에 들어오지 않으며 필요할 때 내가 해야 하는 일을 잘 모르겠고 어떤 상황인지도 한눈에 안 들어옴."

완료 기준(1366×768, 스크롤 없이):
- 결정할 카드가 오른쪽 열 맨 위에 있고, 펼친 한 장이 질문 한 줄·이유 한 줄·버튼으로 끝난다. 결정이 없으면 같은 자리에 "할 일 없음" 또는 무력화 결과.
- 머리 한 줄로 적 수와 단계별 개수(순서 가정 없음), 결정 대기 수, 운용자 조작 대 수동 기준이 보인다.
- 왼쪽 목록에서 기체마다 하는 일·맡은 표적·배터리, 적마다 탐지 상태·위험도가 보인다.
- 지도에서 기체→표적 관계(선), 위험도(색), 놓친 배(마지막 위치와 추정)가 보인다.
- 판단에 쓰는 글자는 13px 이상, 보조 글자 최소 11px(실측: 고치기 전 12px 미만 글자 54~61% → 시안 30~34%, 남은 것은 11px).
- 3분 대본(야간 시연)이 화면 조작만으로 끝까지 돈다. 화면 점검 `scripts/qa/live.json` 통과.

## 2. 화면 구성

```
┌ ROLECALL 편집기 상황판 │ 적 3척 1 허락 대기 2 추적 1 미탐 │ [2 결정 대기] │ 10 운용자 조작 vs 33 수동 · LIVE ┐
├ 아군 6 ────────┬──────────── 지도 ────────────┬ 결정 대기 2 ───────────────┤
│ d1 해안 순찰 A  │  기체→표적 선, 위험도 색, 놓침  │ ┌ 표적 발견 boat1   [지금] │
│  → boat1 ▮▮ 83% │  점선, 미탐 흐리게              │ │ 질문 · 이유 · 위험 0.50  │
│ ...            │                                 │ │ [근접 확인]               │
│ 적 3           │                                 │ │ 기지 대기 드론에게 맡기기 │
│ boat1 추적 0.50│                                 │ └ ...                      │
│ boat3 미탐     │ T+16:38 ▶ ×1 ×5 ×10 ×30 다음 사건│ boat2 0.42 d2 발견 ▸ (한 줄)│
│                │                                 │ ▸ 작전 전환  ▸ 지난 기록   │
└────────────────┴─────────────────────────────────┴────────────────────────────┘
  236px                     나머지                           384px
```

색은 뜻 하나에 하나(`theme.css` 토큰, 새 hex 없음):

| 색 | 뜻 | 쓰는 곳 |
|---|---|---|
| 흰색(`--text`) | 당신 차례 | 결정 카드 왼쪽 줄, '지금', 결정 대기 수, 주 버튼 |
| 노랑·주황·빨강(`--unknown`·`--warn`·`--hostile`) | 위험도 0.40 미만·이상·0.70 이상 | 표적 마커·목록·카드 점수. 빨강은 타격·차단에도 |
| 하늘(`--friend`) | 아군 | 기체, 기체→표적 선, '추적' 단계 |
| 초록(`--live`) | 시스템 상태 | LIVE, 선택한 기체 테두리, 배속 |

카드 앞 영어 코드(CONTACT 등)는 한글 제목과 같은 말이라 뺀다. 목록 줄은 상자 대신 구분선과 왼쪽 색 막대.

## 3. 화면 로직 (cop-ui, 액션 파일 1개 = 함수 1개 = vitest)

| id | 액션 | 입력 | 출력 | 완료 기준 |
|---|---|---|---|---|
| UI-82 | trackState | Frame, Target, 기준점 | {k, pos, est?, agoMs?, dir?} | k: seen(seen_by 있음)·rf(RF만)·lost(first_seen_ms 있고 지금 못 봄)·never·gone. lost는 pos=last_seen_pos, 속도 0.3 m/s 미만 still, 기준점 쪽 approach, 반대 away, est=마지막 위치+속도×지난 시간 (결정 0047) |
| UI-83 | targetStage | Frame, Target | {key, label, detail} | 무력화 > 타격 중(그 표적에 strike 명령 기체) > 허락 대기(열린 타격 승인 요청) > 놓침 > RF 탐지 > 미탐 > 추적(임무 중 기체가 맡음) > 발견 |
| UI-84 | situationCounts | Frame | {targets, stages[], decisions} | 단계별 개수를 급한 순(허락 대기·타격 중·놓침·RF·추적·발견·무력화·미탐), 0개는 뺌, 결정 수는 결정 단위(합친 표적 선택은 기체 수) |
| UI-80 | decisionQueue | Card[](frameCards), t_ms | {action, alerts, history} | action: 선택지 있는 미처리 보고·대기 전환·30초 안의 대안 있는 차단. 같은 전환이 만든 표적 선택 여러 장은 한 항목. 순서 타격 허락 > 차단 > 전환 > 위험도. alerts: 2분 안의 무력화·공백·배터리·차단. 나머지 history(최신 위) |
| UI-81 | choiceGroups | Card | {planned, requests} | planned = 카드의 정해진 선택지(엔진 순서, 결정 0046), requests = "X → 무엇" 꼴 1기체 선택지를 무엇별로 묶고 기체 목록 |
| UI-85 | vehicleRows | Frame, 플레이 이름, VehicleSpec[] | Row[] | 하는 일(귀환 중·기지 정비·플레이 이름), 표적은 status active일 때만(귀환한 기체의 target_id는 무시), 배터리, 결정 대기 표시 |
| UI-86 | targetPlays | Play[], 도메인 | Play[] | 첫 step 행동이 watch_target·approach_target이고 그 도메인을 쓰는 플레이. strike_target은 없음 (결정 0048) |
| UI-87 | cameraPoints | Frame, action | GeoPoint[] | 살아 있는(2분 안 무력화 포함) 표적의 표시 위치·추정 위치, 임무 중 표적 맡은 기체, 열린 카드의 기체(보고·선택지), 차단의 대안 지점 |
| UI-88 | postPoint | 기체, 플레이, 표적 | Sent | POST /injections {play_by_vehicle, target_by_vehicle, approve: true} (결정 0049), 실패해도 throw 없이 |

`frameCards`(UI-19)·보내기 잠금(UI-20·21)·`RunBar`(UI-27) 요청 로직은 그대로 쓴다.

## 4. 화면 부품 (테스트 생략 가능)

- `Screen.tsx`: 3열 + 머리. `MetricsPanel`은 머리 한 줄(`LoadBar`)로, `SwitchPanel`은 오른쪽 아래 접힘, 지난 기록 접힘.
- `SituationBar`(머리 가운데), `LoadBar`(머리 오른쪽).
- `RosterPanel`(왼쪽): 아군 줄(`vehicleRows`), 적 줄(`targetStage`, 위험도 막대에 0.40 눈금).
- `DecisionQueue`(오른쪽, `CardList` 대체): 한 장만 펼치고 나머지 한 줄(누르면 펼침). 펼친 카드 = 제목·표적·시각, 센서 문구, 이유 한 줄, 위험 점수와 이유(항목마다 띄움), 질문, planned 큰 버튼, "기지 대기 드론에게 맡기기" 아래 requests(무엇 한 줄 + 기체 버튼에 배터리). 표적 선택은 위험도 순 칩, 타격 허락은 빨간 버튼. 결정이 없으면 "할 일 없음 · 재생" 또는 무력화 결과 상자.
- `MapView`·`markers.ts`: 표적 마커 클래스에 탐지 상태(lost 점선 테두리·이름표 "놓침 m:ss 전 · 접근/이탈 추정", never 흐리게·위험도 없음), 표시 위치는 `trackState.pos`. 선 레이어 하나(감시 점선 하늘, 타격 실선 빨강, 놓침 추정 점선 주황, 대안 점선 초록). 기체 이름표는 왼쪽, 표적 이름표는 오른쪽. 기준점 원은 테두리만. 장면이 바뀔 때(열린 카드 집합이 바뀔 때) `cameraPoints`로 fitBounds(maxZoom 13.4), 프레임마다는 움직이지 않는다.
- 표적 지목(`useDirectControl` 확장): 기체 선택 상태에서 표적 마커를 누르면 그 옆에 메뉴(`targetPlays` 버튼, 버튼에 "지금 플레이 → 새 플레이 · 표적"), 누르면 `postPoint`. 빈 바다를 누르면 지금처럼 직접 이동. 기체를 고른 동안만 표적 마커가 클릭을 받는다(지금은 표적이 클릭을 통과시켜 기체 선택을 막지 않음, 그 동작은 기체 미선택 때 유지). 아래에 안내 줄 "d3 선택 · 표적을 누르면 붙일 플레이 · 빈 바다를 누르면 직접 이동 · Esc 취소".
- 지금 화면이 쓰는 선택자 중 QA가 읽는 것은 유지: `.runbar .play`·`.clock`·`.next`, `.status`(LIVE), `.mk.vehicle`, `.mk.target`, `.mk.target.rf span`, `.card`, `.card .threat`. 바뀌는 것은 `live.json`을 같이 고친다.

## 5. 계약 (리드, 한 커밋)

| 파일 | 추가 | 기본값 |
|---|---|---|
| `contracts/models/events.py` `Target` | `last_seen_pos: GeoPoint \| None`, `last_seen_vel_east_mps: float`, `last_seen_vel_north_mps: float` | None, 0, 0 |
| `contracts/models/api.py` `SwitchIn` | `target_by_vehicle: dict[str, str]`, `approve: bool` | {}, False |
| `contracts/models/events.py` `Injection` | `target_by_vehicle: dict[str, str]` | {} |

기본값이 있어 기존 JSON·예시·테스트는 그대로. `gen_contracts.py`, `gen_examples.py`, `API.md`(표적 칸, POST /injections).

## 6. 엔진

- sensing `observe_targets`(SNS-02, 최동호): 표적을 본 틱에 `last_seen_pos`·`last_seen_vel_*`를 그때 값으로. 테스트: 보는 동안 갱신, 못 보면 유지.
- runtime `fleet_choices`(RT-11, 황승주 영역·Part2-28 최동호): 함께 감시 후보 Y를 카드를 올린 드론으로만. 테스트: boat1 카드에 boat2 함께 감시가 없다.
- runtime `apply_injection`(RT-05, 황승주): `switch_play` 뒤 `target_by_vehicle`에 있는 기체의 `target_id`를 그 표적으로. 테스트.
- gateway `request_switch`(리드): `target_by_vehicle`을 Injection에 싣고, `approve`면 `status: approved`로 만든다(`record_injections`가 대기 카드 없이 바로 적용). 테스트: approve 요청은 다음 틱에 기체 플레이·표적이 바뀌고 운용자 조작 +1.
- 위험도 계산(`score_targets`)은 바꾸지 않는다(결정 0047).

## 7. 순서와 빼는 순서

통합 2(10/11 00:00) 전, 순서대로 하나씩 ship:
1. 오른쪽 열(UI-80·58, `DecisionQueue`), 머리(UI-84, `SituationBar`·`LoadBar`), 색·글자 크기(theme.css) — 가장 큰 효과, 계약 없음.
2. 왼쪽 목록(UI-85, UI-83 중 계약 없는 단계), 지도 선·이름표·카메라(UI-87).
3. 계약 커밋 → 탐지 상태(UI-82, sensing) → 지목(UI-86·62, runtime·gateway).
4. `live.json`·`runStops.ts` 맞춤, 3분 대본 리허설.

늦으면 뒤에서부터 뺀다: ① 지목 메뉴(지금처럼 전환 패널로 대체) ② 놓침 추정선(마지막 위치만) ③ 카메라 자동 맞춤(고정 화면).

## 8. 하지 않는 것

- 정답 보기(시뮬레이터 실제 위치 전환) — 리드가 뺌(결정 0047).
- 놓친 배의 위험도 재계산, 이름표 자동 충돌 회피(왼쪽·오른쪽 고정 규칙만), 편집기 화면 변경, 모바일 화면.

## 9. 알려진 위험

- runtime·sensing은 다른 사람 영역이다. 6절 세 줄은 담당자 동의 뒤 시작하고, 리드가 하면 채팅으로 알린다.
- 귀환한 기체도 `target_id`가 남는다(엔진). 화면은 임무 중 기체만 표적과 잇는다(UI-85·61). 엔진 정리는 이번 범위 밖.
- 카메라 자동 맞춤은 장면이 바뀔 때 지도가 움직인다. 리허설에서 어지러우면 고정 화면으로 뺀다(7절 ③).
- 미탐 배는 실제 위치에 흐리게 보인다(시뮬레이션이라 리드가 고름). 발표에서 "센서에 안 잡힌 배는 흐리게, 운용자 판단에는 쓰이지 않음"을 말한다.
