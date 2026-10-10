# 작전 고르기 설계 (Part1-29, 결정 0041)

## 목적
시나리오 파일이 여러 개(야간 해안 경계, 24시간 해안 순찰 교대)인데 gateway는 켤 때 하나만 읽어서, 다른 작전을 보려면 gateway를 다시 켜야 했다. 편집기에서 작전을 고르고 "시뮬레이션"으로 상황판에 넘어가게 한다.

## 범위
- 목록에 넣는 작전: `demo/scenarios/baengnyeong_night.json`(시나리오 id `baengnyeong_night`), `demo/scenarios/baengnyeong_24h.json`(`baengnyeong_24h`). 백업 `baengnyeong_night_before_0036.json`은 id가 본편과 같아 뺀다.
- 하지 않음: 작전 새로 만들기·지우기, 파일 저장, 24시간 작전용 배속·다음 사건, 플레이 삭제(접음).

## 동작
1. gateway는 켤 때 목록의 시나리오를 모두 메모리에 읽는다. 처음 실행 작전은 `KDTH_SCENARIO`(없으면 야간). `KDTH_SCENARIO`가 목록에 없는 파일이면 그 파일도 목록 맨 앞에 넣는다. 같은 시나리오 id가 두 번이면 앞의 것만.
2. `GET /scenarios` → `ScenarioInfo[]`(`id`, `name` = 작전 이름, `purpose` = 작전 목적, `active`). 순서는 목록 순서.
3. `POST /scenarios/{id}/activate` → 지금 실행 작전(저장한 플레이·작전 수정 포함)을 목록에 되돌려 놓고 그 작전으로 바꾼 뒤 `reset`(작전 시작 직전 `paused`). 응답 `RunState`. 없는 id 404. 이미 실행 작전이어도 reset한다.
4. 기존 `/plays`·`/operation`·`/vehicles`·`/enemies`·`/plays/check`·`/plays/draft`·`/run/*`·`/ws`는 그대로 실행 작전을 쓴다.
5. 편집기 사이드바: "＋ 새로 만들기" 아래 "작전" 묶음에 작전 이름 버튼들. 실행 작전은 `on`. 다른 작전을 누르면 activate → 편집기 데이터(작전·플레이·기체·적)를 다시 읽고 → 그 작전의 "작전 개요"를 연다. 저장 안 한 수정·검사 결과·화면 기록은 버린다. 실패면 편집기 위에 오류 한 줄, 화면은 그대로.
6. 작전 개요 위 작전 패널 제목 옆 "▶ 시뮬레이션": `POST /run/reset` 뒤 `location.hash = "#live"`. 자동 재생 없음. 실패면 버튼 옆에 오류.
7. 상황판 재생 막대: `GET /scenarios`로 실행 작전 id를 읽어 `baengnyeong_night`면 지금 정지 시각(`RUN_STOPS`), 그 밖이나 읽기 실패면 정지 시각 없음 → "다음 사건 없음". 상황판은 탭을 오갈 때 다시 그려지므로 넘어올 때마다 다시 읽는다.

## 파일
| 층 | 파일 | 변경 |
|---|---|---|
| contracts | `contracts/models/api.py`, `__init__.py` | `ScenarioInfo` 추가, `_MODELS` 등록 |
| contracts | `scripts/gen_examples.py` → `contracts/examples/scenario_info.json`, `gen_contracts.py` → TS·schema | 다시 생성 |
| contracts | `contracts/API.md` 5절 | 두 엔드포인트 줄과 동작 문단 |
| gateway | `modules/gateway/live.py` | `Live(scenario, init, tick, others=())`, `scenario_infos()`, `activate(id)` |
| gateway | `modules/gateway/app.py` | `DEMO_SCENARIOS` 목록·읽기, `GET /scenarios`, `POST /scenarios/{id}/activate`(KeyError → 404) |
| gateway | `tests/test_live.py`, `tests/test_app.py` | 아래 테스트 |
| cop-ui | `vite.config.ts` | proxy 정규식에 `scenarios` |
| cop-ui | `features/editor/fetchScenarios.ts` (액션) | `GET /scenarios` → `ScenarioInfo[]`, 실패·모양 틀림이면 `[]` |
| cop-ui | `features/editor/activateScenario.ts` (액션) | `POST /scenarios/{id}/activate`, 2xx 아니면·연결 실패면 throw |
| cop-ui | `features/run/stopsFor.ts` (액션) | 시나리오 id → `RunStop[]` |
| cop-ui | `PlaySidebar.tsx`, `EditorScreen.tsx`, `OperationPanel.tsx`, `OperationOverview.tsx`, `RunBar.tsx`, CSS | 화면 연결 |

## 테스트
- gateway `Live`: activate 뒤 `scenario.id`가 바뀌고 run은 `paused`, 엔진 init이 새 시나리오로 불림. 저장한 플레이가 다른 작전에 갔다 와도 남음. 없는 id는 KeyError. `scenario_infos`의 `active`는 하나.
- gateway app: `GET /scenarios`가 두 작전(야간 active), activate 뒤 `/operation`의 이름이 24시간 작전, 없는 id 404.
- cop-ui: fetchScenarios(정상·실패·모양 틀림), activateScenario(경로·메서드, 4xx throw), stopsFor(야간이면 RUN_STOPS, 그 밖은 []), viteProxy(기존 테스트가 API.md 경로를 읽어 확인).
- 화면 확인: dev 서버에서 24시간 작전 선택 → 개요가 바뀜 → 시뮬레이션 → 상황판에 드론 3대가 출발 위치에 멈춰 있고 "다음 사건 없음" → 편집기에서 야간으로 돌아감 → 시뮬레이션 → 다음 사건 버튼이 돌아옴.
