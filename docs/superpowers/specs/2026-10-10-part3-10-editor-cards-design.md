# 편집기: 카드 열(읽기 전용) 설계 — Part3-10

2026-10-10 KST · 09 문서 6절 Part3-10, 3.8절 · 결정 0006(step = 행동 하나 + 탈출 조건), 0009(읽기 전용 카드), 0015·0016(두 층) · 담당 리드(cop-ui)

## 1. 목적과 완료 기준

편집기 화면의 첫 단계. 작전(Operation)과 플레이(Play)를 읽어 카드로 그린다. 고치지는 않는다(편집은 Part3-12).

- 완료 기준(09 6절): 예시 작전이 화면에 그려진다.
- 뒤 항목의 바탕: Part3-11(저장 → 검사 표시), 3-12(카드 편집), 3-13(AI 초안)은 모두 플레이 하나를 주고받는다. 그래서 화면도 "플레이 하나"를 기본 단위로 둔다.
- 시간 제한: 10/10 12:00. 넘으면 남은 부분(작전 개요)을 두고 Part1-9로 간다(통합 1 경로 우선).

## 2. 화면

### 2.1 탭

화면 맨 위에 `편집기 | 상황판` 탭. 지금의 지도 + 경보 목록은 "상황판" 탭에 그대로 둔다. 고른 탭은 `location.hash`(`#editor`, `#live`)에 둔다. 없으면 `#live`. 라우터 라이브러리는 넣지 않는다.

### 2.2 편집기 = 왼쪽 바 + 가운데

왼쪽 바(사람이 고름, 2026-10-10):
- 맨 위 `작전 개요`(기본 선택. 작전 개요를 못 만들고 멈추면 첫 플레이가 기본).
- 아래 플레이 목록, 영역별 묶음: 드론(air) · 수상정(sea) · 지상(ground) · 공통. `Play.domains`가 하나면 그 묶음, 둘 이상이거나 비었으면 공통. 묶음 안 순서는 받은 순서.
- 데이터가 예시로 대체됐으면 맨 위에 "예시 데이터(서버 없음)" 표시(3절).

가운데 — 작전 개요를 골랐을 때:
- 위 띠: 작전 이름, 전체 전환 버튼(`op.switches`)의 label을 표시만 한다.
- 기체마다 세로 열 하나(`op.vehicle_ids` 순서). 열 머리 = 기체 id(이름·영역은 Operation에 없음), 예비면 "예비: d1 대신"(`op.reserve`에서 찾음).
- 열 내용 = 시작 플레이(`op.assign[id]`) + 이어지는 플레이(사람이 고름, 2026-10-10). 이어지는 플레이마다 구분선 "'<선택지 label>' 선택 시".
- 열 안 플레이 이름을 누르면 그 플레이 화면으로 간다.

가운데 — 플레이를 골랐을 때:
- 머리: 플레이 이름, 영역, 쓰는 기체 목록. 예 "d1 — 작전 시작", "d2 — 해안 순찰 A의 '근접 확인' 뒤", "d1 — 전체 전환 '전 기체 귀환'".
- step 카드 세로 목록(`steps` 배열 순서). 첫 step(`entry`)에 ▶.

### 2.3 step 카드

- step 이름.
- 행동 한 줄(`describeAction`).
- 탈출 조건 목록: "<조건 한 줄> → <갈 step 이름>". 없는 step id면 id를 빨간 글씨로.
- 보고(`report`가 있을 때): 문구, 선택지마다 label과 "기체 → 플레이 이름" 목록. 플레이 이름을 누르면 그 플레이로 간다. 없는 플레이 id면 빨간 글씨.

## 3. 데이터

`loadEditorData(fetchFn) -> Promise<{operation, plays, source}>`:
1. `GET /operation`과 `GET /plays`(contracts/API.md 5절)를 부른다. 둘 다 2xx면 `source: "gateway"`.
2. 어느 쪽이든 네트워크 오류나 2xx 아님이면 `demo/scenarios/baengnyeong_night.json`의 `operation`·`plays`로 대체하고 `source: "example"`. 이 파일은 빌드 때 번들에 들어간다.
3. 대체는 화면에 반드시 표시한다(조용한 대체 금지: 시연 중 서버가 죽은 걸 못 알아챔).

이 대체 경로는 Part1-7 전 개발용 스텁이다. 09 문서 4.5절대로 통합 2(10/11 00:00) 전에 걷어낸다.

설정 변경(`vite.config.ts`): `server.proxy`에 `/operation`·`/plays` → `http://localhost:8000` 추가, cop-ui 밖 시나리오 파일을 읽도록 `server.fs.allow`에 저장소 루트 추가.

## 4. 계산 함수 (순수, vitest, TDD)

모두 `modules/cop-ui/src/features/editor/`. 테스트 데이터는 시나리오 JSON.

| 함수 | 입력 → 출력 | 테스트 |
|---|---|---|
| `describeAction` | Action → string | patrol_route 2점 → "순찰 경로 2점", watch_target `target: "nearest"` → "표적 감시 · 가장 가까운 표적", `"operator"` → "운용자가 고름", 고정 id → 그 id |
| `describeCondition` | Condition → string | target_found → "표적 발견", battery_below `{pct: 30}` → "배터리 30% 미만". 키가 정해지지 않은 조건(time_elapsed 등, 시연 플레이에서 안 씀)은 라벨 뒤에 params를 "키 값"으로 붙임 |
| `groupPlays` | Play[] → {group, plays}[] | 시나리오: 드론 4(patrol_a·watch·patrol_b·track_fast), 수상정 1(approach), 지상 1(landing), 공통 2(standby·go_home) |
| `vehicleColumns` | Operation, Play[] → Column[] | d1: patrol_a → watch, d2: standby → patrol_b, d3: standby(예비: d1), usv: standby → approach, ugv: standby → landing |
| `playUsage` | Operation, Play[] → Record<playId, Usage[]> | patrol_b → [d2, patrol_a의 '근접 확인'], go_home → 5대 모두 전체 전환 '전 기체 귀환' |
| `loadEditorData` | fetch → 데이터 | 가짜 fetch 성공 → gateway, 예외·500 → example |

라벨 표는 `Record<ActionKind, string>`·`Record<ConditionKind, string>`로 둬서 빠진 종류는 컴파일에서 걸린다.

`vehicleColumns`의 "이어지는 플레이" 규칙:
- 작전에서 닿는 플레이 = `op.assign`의 플레이에서 시작해, 닿은 플레이의 모든 보고 선택지 `play_by_vehicle` 값을 따라 넓힌 집합(넓힌 순서 유지, 이미 본 플레이는 다시 안 봄).
- 기체 v의 열 = `op.assign[v]`, 그 뒤 닿는 플레이들의 선택지 중 `play_by_vehicle[v]`가 있는 것마다 그 플레이를 순서대로(한 열에 같은 플레이는 한 번).
- 전체 전환(`op.switches`)은 열에 넣지 않는다(넣으면 모든 열 끝에 귀환이 붙음). 위 띠와 `playUsage`에만.
- 없는 플레이 id는 열에 빨간 자리표시 카드로.

## 5. 파일

새 파일(`modules/cop-ui/src/features/editor/`):
- 계산: `describe.ts`, `groupPlays.ts`, `vehicleColumns.ts`, `playUsage.ts`, `loadEditorData.ts`와 각 `.test.ts`
- 화면(테스트 생략, cop-ui AGENTS.md): `EditorScreen.tsx`, `PlaySidebar.tsx`, `OperationOverview.tsx`, `PlayWorkflow.tsx`, `StepCard.tsx`

고치는 파일: `App.tsx`(탭), `vite.config.ts`, `index.css`, `modules/cop-ui/SPEC.md`(UI-06~), `demo/BUILT_HERE.md`. 파일마다 200줄 이하.

## 6. 순서와 확인

순서: 계산 함수 → 플레이 화면(StepCard·PlayWorkflow) → 왼쪽 바 → 탭 → 작전 개요. 12:00에 작전 개요가 남으면 멈춘다.

확인: `npm test`, `npm run build`(tsc 포함) 통과, `npm run dev`로 두 화면을 눈으로 확인(gateway 없이 "예시 데이터" 표시와 함께).

## 7. 하지 않는 것

편집, 저장·검사 표시, AI 초안 입력, 작전 설정 패널(Part3-11~3-14). `Step.ui` 좌표 사용. 기체 이름·영역 표시(Operation에 없음, 계약 변경 필요). 그래프 그리기(React Flow 안 씀, 3.8절).
