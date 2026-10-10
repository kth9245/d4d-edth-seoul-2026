# 해상 기체는 육지를 지나지 않는다 — 설계

작업 기록 Part2-19.1(kth9245). 결정 0034. 2026-10-10 리드 승인(브레인스토밍).

## 1. 문제와 측정

백령도 시나리오에서 수상정이 섬을 가로지른다. 원인은 두 가지다.
- sim의 이동(`move_straight`·`follow_route`·`orbit_or_keep`·`steer_enemies`)이 모두 두 점 사이 직선이다. 육지 개념이 없다.
- 시나리오에 섬 지형이 없다(결정 0004 영향에 적은 "섬 지형"이 빠짐).

로컬 위성 타일(줌 13)의 색 마스크(바다 = B > 1.5·R)로 잰 값:

| 경로 | 길이 | 육지 위 |
|---|---|---|
| 수상정 home(37.94, 124.71) → boat1 출현점 | 5,086 m | 4,921 m |
| 대본 boat1 남하 720 s | 720 m | 621 m |
| fast1 분리 뒤 300 s | 1,897 m | 672 m(육지 위에서 출발) |
| 수상정 → AI 초안 캐시 서쪽 항로 첫 점 | 12,128 m | 7,259 m |
| 지상로봇 home → 상륙 예상 지점 | 2,835 m | 바다 0 m(문제 없음) |

바다로만 간 최단 거리(60 m 격자): 지금 수상정 home → boat1 10.2 km(8 m/s로 21분), 북쪽 해안 앞바다(37.981, 124.691) → boat1 1.1 km(2분), 동쪽 해안 → 5.7 km, 서쪽 항로 첫 점 15.8 km(33분).

## 2. 결정 (사람 답)

- 결정 0034: "B도 해야하고 happy path에 수상은 지상을 못지난다는건 당연히 포함되어야함". sim이 육지를 피하고(B) 시나리오 좌표도 바다로(A).
- A는 이 세션이 전부("이 세션이 A 전부"). 최동호 Part1-19·Part2-19와 같은 파일이라 채팅으로 맞춘다.
- 우회 방식 1안, 적 배 포함("1안, 적 배 포함").
- 수상정 home은 북쪽 해안 앞바다("북쪽 해안 앞바다"). 사건 시각은 그대로.

## 3. 범위

한다
- 계약 `Scenario.land`, 섬 다각형 데이터(타일에서 추출).
- sim 해상 기체와 적 배(boat·fast_boat)의 육지 우회.
- 시나리오 좌표: 수상정 home, boat1·fast1, 지상로봇 상륙 예상 지점.
- 데이터 테스트와 엔진 경로 테스트.

안 한다
- 지상 기체가 바다로 못 나가는 반대 규칙(시연에서 지상로봇은 육지 위만 다님).
- 편집기 저장 검사에서 "해상 점이 육지 위" 거부(하한선 규칙은 3개 고정. sim이 가장 가까운 바다 점으로 대신 간다).
- 화면에 섬 다각형 그리기(위성사진이 보여 줌).
- 사건(`spawn_target`·`split_target`) 속도로 움직이는 옛 방식 표적의 우회(boat1·fast1은 적 플레이로 바꿈).

## 4. 계약

- `contracts/models/frame.py` `Scenario`에 `land: list[Polygon] = []  # decision 0034: sea vehicles and enemy boats route around these`. 기본값이 비어 있어 기존 시나리오·예시·테스트는 그대로다.
- `scripts/gen_contracts.py`로 schema·`contracts.gen.ts` 재생성, `scripts/gen_examples.py`로 예시 재생성.
- `contracts/API.md`
  - 1절 개념 표: 시나리오 행에 "섬(육지) 다각형 `land`".
  - 3절 틱 표: 1.5 `steer_enemies(..., land)`, 8 `advance(..., land)`.
  - 3절 그 밖의 공개 API에 sim `sea_aim(pos, goal, land) -> GeoPoint` 한 줄과 규칙 한 줄: "해상 기체(domain sea)와 적 배(boat·fast_boat)는 직선이 육지를 지나면 섬 모서리를 돌아간다. 목표가 육지 안이면 가장 가까운 바다 점까지 간다(결정 0034)."

## 5. 섬 다각형 데이터

- `scripts/make_land.py`(일회성, `uv run --with pillow python scripts/make_land.py`). Pillow는 프로젝트 의존성에 넣지 않는다.
  1. `modules/cop-ui/public/tiles/baengnyeong/13/`을 이어 붙인다.
  2. 바다 = B > 1.5·R, 메디안 필터 9로 잡음 제거.
  3. 가장 큰 육지 덩어리(본섬)만 남기고 외곽선을 딴다(작은 바위·색 얼룩은 버림).
  4. Douglas-Peucker로 줄인다(허용 오차 약 30 m, 점 30~90개). 위경도 소수 5자리.
  5. `demo/scenarios/baengnyeong_land.json`에 `[{"points": [...]}]`로 쓴다. 시나리오 JSON은 손으로 고치지 않는다: `scripts/example_world.py`가 이 파일을 읽어 `Scenario(land=...)`에 넣고 `scripts/gen_examples.py`가 `baengnyeong_night.json`을 다시 만든다(시나리오 좌표 수정(7절)도 example_world.py에서).
- 출처: EOX Sentinel-2 cloudless 2020 타일에서 만든 파생 데이터. `demo/BUILT_HERE.md`에 한 줄.

## 6. sim

### 6.1 기하 도우미 `shared/land.py`(액션 아님, 줄 수 제한 없음)
- 위경도 ↔ 지역 미터는 `shared/geo`의 `enu_delta_m`·`offset_latlon`을 쓴다.
- `inside(p, poly) -> bool`: 점이 다각형 안(광선 교차).
- `blocked(a, b, land) -> bool`: 선분 a-b가 어느 다각형의 변과 진짜로 교차하거나, 중점이 다각형 안이면 참.
- `to_sea(p, land, margin_m=50) -> GeoPoint`: p가 육지 안이면 가장 가까운 변 위의 점에서 바깥 법선으로 50 m 밀어낸 점, 아니면 p 그대로.
- `corners(poly, margin_m=100) -> list[GeoPoint]`: 볼록한 꼭짓점(다각형 방향 기준)을 바깥 이등분선으로 100 m 밀어낸 점들. 밀어낸 점이 어느 다각형 안이면 버린다. `functools.lru_cache`로 다각형마다 한 번.
- 모서리끼리 보이는지(정적 그래프)도 다각형 묶음마다 한 번 계산해 캐시한다.

### 6.2 새 액션 SIM-13 `sea_aim(pos, goal, land) -> GeoPoint`(80줄 이하)
1. `land`가 비었거나 `pos`가 육지 안이면 `goal`(데이터 테스트가 육지 위 시작을 막는다).
2. `goal = to_sea(goal, land)`.
3. `blocked(pos, goal)`이 거짓이면 `goal`.
4. 노드 = 모서리 점들 중 `pos`에서 1 m 넘게 떨어진 것. `pos`에서 보이는 노드, `goal`에서 보이는 노드를 구하고 정적 그래프와 합쳐 Dijkstra. 최단 경로의 첫 노드를 돌려준다(이미 도착한 모서리에서 멈추지 않게 1 m 안 노드는 뺀다).
5. 경로가 없으면 `goal`(섬이 하나인 시연에서는 생기지 않음).

공개 API로 `modules/sim/__init__.py`에 export(엔진·테스트가 씀).

### 6.3 호출하는 곳
- `advance_vehicles(states, specs, passed, dt_ms, targets, land=())`(SIM-08): `spec.domain == sea`일 때만 이동 함수에 `land`를 넘긴다. 공중·지상은 지금과 같다.
  - `move_straight`(SIM-05): `tgt = to_sea(tgt, land)`, `move_toward(pos, sea_aim(pos, tgt, land), step)`. 도착 판정은 `tgt` 기준.
  - `follow_route`(SIM-06): 지금 경로점을 `to_sea`로 바꾸고 같은 방식. 경로점 넘김은 바꾼 점 기준.
  - `orbit_or_keep`(SIM-07, 해상은 keep_distance·strike만 씀): 표적까지 직선이 막혔으면 `sea_aim` 점으로 한 틱 거리만큼, 열려 있으면 지금처럼 거리 유지.
- `steer_enemies(enemies, plays, targets, t_ms, dt_ms, land=())`(SIM-12): 적 kind가 boat·fast_boat면 목적지를 `to_sea`로 바꾸고 속도 방향을 `sea_aim` 점으로. 도착(위치 맞춤·속도 0)은 바꾼 목적지 기준.
- `modules/gateway/engine.py`(최동호 파일, 알림): `steer_enemies(..., sc.land)`, `advance(..., sc.land)` 두 줄.

### 6.4 속도
- 직선이 열린 틱: 변 수(약 50)만큼 선분 교차 검사.
- 막힌 틱: (보이는 노드 계산) 노드 약 25 × 변 약 50 + Dijkstra.
- 확인: 구현 뒤 실제 시나리오에서 `/run/jump`와 같은 연속 틱(작전 시작 → 30분)을 우회 있는 경우(서쪽 항로 캐시 플레이)로 재서 보고한다. 2배 넘게 느려지면 변 bounding box 선검사를 넣는다.

## 7. 시나리오 좌표 (A)

- 수상정 home: 북쪽 해안 앞바다 37.981, 124.691 근처(추출한 `land` 밖이고 다른 home과 500 m 이상).
- boat1·fast1을 적(`enemies`, 결정 0032)으로. Part1-19(최동호)가 이미 바꿨으면 그 위에 좌표만 고친다. 시작 전에 최동호에게 확인.
  - boat1: 북쪽 바다에서 나타나 해안 쪽 `move_to`(목표가 육지면 sim이 해안 바로 앞에서 멈춤) → `hold`. 드론 순찰 A가 감지해 보고 카드가 뜨는 시각이 지금과 비슷하게.
  - fast1: boat1 위치에서 나타나(`from_enemy`) 동쪽 해안 상륙 지점으로 `move_to`. 북동쪽 곶은 sim이 돌아간다. 수상정·드론2가 바다 위에서 100 m 안으로 붙어 타격할 수 있는 속도·시각(결정 0033 6번).
- 지상로봇 상륙 예상 지점(`landing` 플레이): 37.975, 124.70(내륙 약 800 m) → 북쪽 해안선 바로 안쪽.
- AI 초안 캐시 "서쪽 항로 순찰"은 그대로(실행하면 섬을 돌아감, 약 33분). 시연에서 지도로 실행할지는 Part1-15.

## 8. 테스트 (TDD, 결정 0014)

- `tests/test_land.py`(shared): inside, blocked(통과·비통과), to_sea(육지 안 점이 바다로, 바다 점은 그대로, 좁은 만 건너편에 떨어지면 더 밀기), corners(볼록 꼭짓점만, 바깥쪽, 시계·반시계 둘 다).
- `modules/sim/tests/test_sea_aim.py`: 사각형 섬 하나로 — 열린 직선이면 goal, 막히면 모서리 점, 모서리에 도착한 뒤 다음 모서리, 목표가 육지면 바다 점, land 비면 goal.
- SIM-05·06·07·08·12 테스트에 해상 기체·적 배가 사각형 섬을 돌아가는 케이스 하나씩(틱을 돌려 어느 틱에도 섬 안에 없고 결국 도착).
- `tests/test_demo_scenario.py`
  - `land`가 1개 이상, 해상 기체 home과 적 등장 위치(pos)가 육지 밖.
  - 엔진 경로 테스트: smoke와 같은 흐름(첫 보고 카드의 첫 선택지)으로 실제 시나리오를 작전 시작 후 45분까지 돌리고(fast1이 북동쪽 곶을 돌아 동쪽 해안에 닿는 시간 포함), 매 틱 해상 기체 위치와 boat·fast_boat 위치가 `land` 밖.
- smoke는 그대로 통과해야 한다.

## 9. 순서와 담당

1. 계약 `Scenario.land` + 재생성(리드).
2. `make_land.py`로 다각형 추출, `land`만 시나리오에 넣고 데이터 테스트.
3. `shared/land.py` → SIM-13 `sea_aim` → SIM-05·06·07·08·12 → engine.py 두 줄(최동호에게 채팅 알림: sim·engine 파일 변경).
4. 시나리오 좌표(A)와 엔진 경로 테스트. 최동호 Part1-19·Part2-19와 순서 맞춤.
5. 속도 확인, `demo/BUILT_HERE.md`, 1-9 세션에 land 계약 반영 알림.
각 단계 ship(액션 하나마다).

## 10. 위험

- 최동호가 같은 JSON(enemies 전환·튜닝)과 sim 파일을 동시에 고친다. 시작 전에 상태를 묻고, `land` 키 추가·좌표 수정은 작은 커밋으로 자주 ship한다.
- 타일 색 마스크는 해변 모래를 바다로 읽는다. 해안선이 수십 m 바다 쪽으로 어긋날 수 있다(우회 여유 100 m로 덮음).
- fast1이 해변(육지)에 닿은 뒤에는 수상정이 100 m 안에 못 붙을 수 있다. 타격은 fast1이 바다에 있을 때 일어나게 튜닝한다.
