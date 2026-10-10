# 경로 선택과 offset 행동 설계 (Part1-31, 결정 0044, 0045)

## 목적
경로·웨이포인트를 화면에서 고를 방법이 없었다(시나리오 JSON을 손으로 고침). 편집기 카드 패널에서 경로를 선택칸으로 고르고, 위치 offset(기준점에서 m 거리)과 시간 offset(T+)에 맞춰 행동하게 한다.

## 사용 예
```
[경로 비행: 기지 → 북쪽 해역 · 한 번]      ← 고정 경로, 마지막 점에서 "도착"
     │ 도착
     ▼
[경로 비행: 사각형 수색 300m · 반복]        ← 상대 경로, 들어간 순간의 기체 위치 기준
     │ 표적 발견            │ T+25:00
     ▼                      ▼
[감시·보고]               [귀환]
```

## 범위
- 하는 것: 시나리오 경로 목록, 편집기 "경로 비행 + 반복" 행동과 경로 선택칸, 이동 카드가 경로를 한 번 따라가기, 상대 경로를 카드 진입 때 실제 좌표로, 연결 조건 `at_time`(T+).
- 하지 않는 것: 지도에서 점 찍기, N번째 지점 도착 조건, 표적을 기준점으로, 계약의 행동 종류 합치기, 구역 수색·지점 감시·통신 중계(시뮬레이터가 아직 안 움직임).

## 데이터 (contracts)
- `RouteOffset{north_m: float, east_m: float}`, `RouteDef{id: str, name: str, points: list[GeoPoint] = [], offsets: list[RouteOffset] = []}` (world.py). 둘 중 하나만 채운다. 상대 경로의 기준점은 항상 "카드에 들어가는 순간의 기체 위치".
- `Scenario.routes: list[RouteDef] = []`.
- 카드(`Action.params`, 형식 자유 dict라 모델 변경 없음, API.md에 적음):
  - 고정 경로: `{route: [GeoPoint...], route_name}`
  - 상대 경로: `{offsets: [{north_m, east_m}...], route_name}`
  - 점 하나 이동(기존): `{target: GeoPoint}` 그대로
- `ConditionKind.at_time`, params `{offset_ms: int}`: 작전 시작 후 offset_ms 이상이면 성립. `time_elapsed`(적 대본의 "카드 시작 후 `sec`")는 그대로.
- 예시: `route_def.json`, `route_offset.json`(gen_examples), TS 재생성.

## 서버 (gateway, 리드)
- `GET /routes` → 실행 작전의 `Scenario.routes`. vite proxy에 `routes`.
- engine.py(최동호): `step_vehicle(..., started_ms=sc.operation.started_ms)` 한 곳.

## 실행 (runtime 황승주, sim 최동호)
- `enter_step`: params에 `offsets`가 있으면 `route = [offset_latlon(기체 위치, o) ...]`(shared/geo)로 바꾸고 `offsets`는 명령에서 뺀다. 행동이 `move_to`이고 `route`가 있으면 명령 종류를 `follow_route`, params에 `loop: false`. `patrol_route`는 지금처럼(`loop` 없음 = 반복).
- `step_vehicle(st, spec, play, targets, t_ms, started_ms: int | None = None)`: `at_time`이면 `t_ms - started_ms >= offset_ms`. `started_ms`가 없으면 성립하지 않는다(0이면 epoch 시각이라 즉시 성립해 버림).
- sim `follow_route`: `loop`가 false면 마지막 점에 닿을 때 `waypoint_idx = -1`(도착)로 두고, 그 뒤로는 움직이지 않는다. 반복이면 지금처럼 처음으로.
- 안전 검사(safety check_command)는 명령의 `route`를 보므로 바꿀 것이 없다(상대 경로도 실제 좌표로 바뀐 뒤 검사됨, 구역 밖이면 차단).

## 편집기 (cop-ui, 리드)
- 행동 선택칸: "이동"·"순찰 경로" 대신 **"경로 비행"** 하나. 그 아래 **"반복" 체크칸**(켜면 `patrol_route`, 끄면 `move_to`)과 **"경로" 선택칸**.
  - 경로 선택칸: `GET /routes`의 목록을 "고정 경로"·"상대 경로(기체 위치 기준)" 두 묶음으로. 고르면 그 경로의 `points`→`route` 또는 `offsets`를 카드에 복사하고 `route_name`을 넣는다. 지금 카드 값이 목록에 없는 경로면(이름 없는 경로·점 하나 이동) "지금 값 유지: 경로 N곳" 항목으로 둔다.
  - 반복 체크를 바꾸면 경로 값은 그대로 두고 행동 종류만 바꾼다. 점 하나 이동(`target`)에서 반복을 켜면 그 점 하나짜리 `route`가 된다(`setActionKind` 지금 동작).
- 경로 칸은 경로 비행 카드에만. 표적 감시·접근·타격, 대기, 귀환은 지금 칸 그대로. 행동을 바꾸면 경로 값을 지운다(`setActionKind`가 이미 행동별로 params를 새로 만든다).
- 연결 조건 목록에 **"T+ 시각"**, 값은 분·초 숫자 칸 두 개 → `offset_ms`(문자열 mm:ss를 고치다 만 상태를 담지 않으려고).
- 카드 문구: `경로 비행 · <route_name 또는 "경로 N곳"> · 한 번|반복`, 상대 경로면 `· 기체 위치 기준`, 점 하나 이동은 `경로 비행 · <좌표> · 한 번`(행동 이름을 하나로 합쳤으므로). 조건 `T+m:ss`.

## 시나리오 데이터 (demo, 두 시나리오 모두)
- 고정: 지금 플레이에 있는 경로(야간: 순찰 A·B, 두 시나리오: 해안 A(북)·해안 B(남)) + 한 번 가는 경로 "기지 → 북쪽 해역"(드론 기지에서 북쪽 해역 2~3점).
- 상대: "사각형 수색 300m"(북300·동300 사각형 후 기준점), "지그재그 수색 600m"(북쪽으로 200m 간격 좌우 ±300m), "원 선회 200m"(기준점 둘레 8점), "북쪽으로 1km"(점 하나).
- 기존 순찰 플레이 params에 `route_name`을 붙인다. 플레이 동작은 바뀌지 않는다.
- AI 초안 프롬프트는 작전 이름·목적·구역만 쓰므로 캐시는 영향 없음.

## 한계
- 상대 경로 카드는 기준점이 실행 중에 정해져, 저장 검사(작전 구역·귀환 배터리)와 MAVLink 변환이 그 카드의 경로를 미리 보지 못한다. 실행 중 안전 검사는 막는다.
- 해안 교대 순찰 플레이(rotation)는 고정 경로만 쓴다(`rotate_patrols`가 `route`를 직접 읽음).

## 테스트
- contracts: 예시가 모델과 맞음, `Scenario.routes` 기본 빈 목록.
- runtime: enter_step 상대 경로 → 기체 위치 기준 실제 좌표 route, move_to+route → follow_route loop false, at_time 전/후.
- sim: follow_route loop false 마지막 점에서 waypoint_idx -1 후 정지, 반복은 처음으로.
- gateway: `GET /routes`가 시나리오 목록, engine이 started_ms를 넘겨 at_time이 실제 틱에서 성립.
- cop-ui: 경로 선택 → params 복사(고정/상대), 반복 토글 → 종류만 바뀜, 경로 칸이 경로 비행에만, T+ 입력 → offset_ms, 카드 문구, vite proxy.
- 화면 점검(`scripts/qa/route_select.json`): 24시간 작전의 "대기" 플레이(d3·d4가 씀)에 "T+0:30" 연결로 새 카드 "경로 비행 · 사각형 수색 300m · 반복"을 이어 저장 → 시뮬레이션 → 30초 전에는 d3·d4가 기지에 있고, 지난 뒤에는 각자 자리를 기준으로 사각형을 돌기 시작. 점검은 제 포트의 gateway 메모리에서만 하고 끝나면 버린다.

## 알릴 사람
- 황승주: runtime enter_step·step_vehicle, play 검사는 그대로(상대 경로는 정적 검사 생략됨).
- 최동호: sim follow_route `loop`, engine.py step_vehicle 호출 한 줄.
