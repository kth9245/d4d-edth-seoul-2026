# 멸공 작전 적 양동 침투와 동적 대응 선택지 설계

날짜: 2026-10-10 · 작성: 황승주 세션 · 대상 작전: 멸공(`demo/scenarios/baengnyeong_24h.json`)
승인: 사용자 10/10 (침투 시각 A안, 계약 변경 A안, 이 설계 전체)

## 목표

멸공 작전에 두 갈래 양동 침투 적 4기를 넣고, 아군 드론이 발견하면 나머지 교대 드론과 아군 USV·UGV에게
그때 상황에 맞는 선택지를 준다. 적이 바다·땅·공중 중 어디 있는지는 발견한 드론이 판단하고,
USV는 바다 적기, UGV는 땅 적기만 추적할 수 있다.

성공 기준: 멸공 실행 시 T+11:00 이후 해안 순찰 드론이 적을 발견해 호버링 추적하고, 카드에
"이탈 지역 순찰 / 적기 N 발견 지점 집중 순찰 / usv·ugv → 적기 N 추적 / 대기"가 상황대로 뜨며,
고른 대로 기체가 움직인다. 야간 작전(`baengnyeong_night.json`)은 파일도 smoke 결과도 그대로다.

## 제약

- 야간 작전 파일은 수정하지 않는다(사용자 10/10). 멸공 JSON은 `scripts/make_coast_routes.py`가 만든다.
- runtime·sim은 두 작전 공용 코드다. 야간 smoke(`scripts/smoke.py`)가 계속 같은 결과여야 한다.
- 계약 변경은 `TargetKind`에 값 3개 추가만. `/decide`로 기록하고 최동호·리드에게 알린다.
- 액션 파일 80줄, TDD, 단계마다 ship.

## 1. 계약

`contracts/models/enums.py` `TargetKind`에 `drone`, `usv`, `ugv` 추가. 기존 값은 그대로.
`scripts/gen_contracts.py`로 schema·`contracts.gen.ts` 재생성(수동 수정 금지).

## 2. 적 4기 (멸공 시나리오)

| id | kind | 등장 | 위치 | 행동(적 role) |
|---|---|---|---|---|
| e_drone | drone | T+11:00 | 북쪽 해안 약 5 km 바다 위 | 드론 기지 정사각형 중심으로 move_to, 도착 후 hold |
| e_usv | usv | T+11:00 | 남쪽 바다 | 남쪽 해안 상륙점으로 move_to(섬 우회), 도착 후 hold. T+23:00 전 도착하도록 출발점·속도 조정 |
| e_ugv1 | ugv | T+23:00 | from_enemy e_usv | 드론 기지 중심으로 move_to, 도착 후 hold |
| e_ugv2 | ugv | T+23:00 | from_enemy e_usv | 섬 해안선을 육지 쪽으로 들인 시계 방향 경로 patrol_route 반복 |

자폭 드론 속도는 아군 드론보다 느리게 둬 호버링 추적이 가능하게 한다.

## 3. sim 이동

`steer_enemies`(SIM-12)의 섬 우회 대상 `BOATS`에 `usv`를 더한다. `drone`·`ugv`는 직선 이동.
shortcut: UGV가 땅을 벗어나는지는 막지 않는다(경로가 땅 위에 있음). 지형 제약이 필요해지면 그때 추가.

## 4. 영역 판단 (runtime 새 액션)

`target_domain(target, land) -> "air" | "ground" | "sea"`: kind가 drone이면 air, 아니면
`shared.land.inside(pos, land)`가 참이면 ground, 거짓이면 sea. 카드 문구에 영역 표시("적기 2 · 지상").

## 5. 동적 선택지 (`fleet_choices`, RT-11 확장)

- 적기 번호: 탐지된 적 표적을 first_seen_ms 순으로 1, 2, 3…
- 나머지 교대 드론 x마다:
  - "x → 이탈 지역 순찰(해안)": 기존 take 선택지 그대로.
  - "x → 적기 N 발견 지점 집중 순찰": 새 role `focus_orbit`. 중심 = 그 적기를 처음 보고한 지점, 반경 800 m 원 반복.
    한 지점(적기)에 집중 순찰 드론은 1대. 이미 붙은 적기는 선택지를 만들지 않고, 같은 적기를 두 카드에서
    고르면 먼저 처리된 결정만 적용한다(apply_decision에서 확인).
- 아군 USV: 바다 적기마다 "usv → 적기 N 추적"(`track_fast_sea` 계열 watch_target). UGV: 땅 적기마다
  "ugv → 적기 N 추적"(새 role `track_ground`). 공중 적기는 둘 다 없음. "대기"는 항상.
- 멸공 온톨로지에서만 지상 로봇에 감시 묶음(watch_target)을 더한다. 야간 UGV는 그대로.
- Part2-45의 고정 선택지 "근접 확인"·"수상정 인계"는 빼고 이 동적 선택지로 바꾼다.

## 6. 범위 밖

자폭 드론 기지 도달 효과, 적 UGV 정찰 결과 활용, 타격, 새 적 아이콘(cop-ui는 리드 담당, 필요 시 요청).

## 7. 순서와 검증

1. Part2-46(병렬 세션, 같은 생성 스크립트 수정) main 반영 대기
2. 계약 3값 + /decide + 팀 알림
3. 시나리오(생성 스크립트) — 적 4기, focus_orbit·track_ground role, 온톨로지
4. sim — usv 섬 우회
5. runtime — target_domain, fleet_choices 확장, apply_decision 중복 집중 순찰 무시
6. 화면 확인(멸공 활성화 후 재생)

각 단계 TDD 후 ship. 매 ship마다 야간 smoke 결과가 그대로인지 확인.
