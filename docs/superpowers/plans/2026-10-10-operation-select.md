# 작전 고르기 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 편집기에서 작전(시나리오) 여러 개 중 하나를 고르면 gateway 실행 작전이 바뀌고, "▶ 시뮬레이션"으로 상황판에 시작 전 멈춤 상태로 넘어간다.

**Architecture:** gateway `Live`가 시나리오 목록(catalog)을 메모리에 들고 `activate(id)`로 실행 작전을 바꾼다. 기존 엔드포인트는 그대로 실행 작전을 가리키고, `GET /scenarios`·`POST /scenarios/{id}/activate` 두 개만 더한다. 화면은 편집기 사이드바 작전 목록·작전 패널 시뮬레이션 버튼·재생 막대 정지 시각 선택만 바꾼다.

**Tech Stack:** Python 3 · FastAPI · pydantic(contracts) · pytest / React · TypeScript · Vite · vitest

**Spec:** `docs/superpowers/specs/2026-10-10-operation-select-design.md` (결정 0041)

## Global Constraints

- 작업은 worktree `.claude/worktrees/Part3-12.3`에서. 명령은 `$(...)` 없이 따로 실행.
- TDD(결정 0014): 실패 테스트 먼저, 실패 확인, 구현, 통과.
- happy path(결정 0024): 시연 흐름 밖 예외 처리를 늘리지 않는다.
- 목록 작전: `demo/scenarios/baengnyeong_night.json`(`baengnyeong_night`), `demo/scenarios/baengnyeong_24h.json`(`baengnyeong_24h`). 백업 `baengnyeong_night_before_0036.json`은 넣지 않는다.
- 시뮬레이션 버튼은 `POST /run/reset` 뒤 `location.hash = "#live"`. 자동 재생 없음.
- 화면 색은 `theme.css` 토큰만(`var(--live)` 등). 새 CSS에 hex 금지. 배치는 `index.css`, 색은 `theme.css`.
- 자동 생성 파일(`contracts.gen.ts`, `contracts/schema/`, `decisions/INDEX.md`)은 손으로 고치지 않고 스크립트로 만든다.
- 커밋 메시지는 `Part1-29: ...` 영어, 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. 작전을 오가도, 실행 중인 작전을 다시 activate해도 저장한 플레이가 남아야 한다 → Task 2 `test_a_saved_play_survives_going_to_another_operation_and_back`, `test_activating_the_running_operation_again_keeps_its_saved_play`.
2. `KDTH_SCENARIO`가 목록의 작전과 같은 id인 다른 파일(백업)이면 실행 작전 내용이 목록에 보여야 한다 → Task 2 `test_the_running_scenario_wins_over_a_catalog_entry_with_its_id`.
3. 없는 작전 id로 activate하면 아무것도 바뀌지 않아야 한다(서버 404, 화면은 오류 한 줄) → Task 2 `test_activate_an_unknown_id_raises_and_changes_nothing`, Task 3 `test_activate_an_unknown_scenario_is_404`, Task 4 activateScenario 404 throw.
4. gateway가 꺼진 채 상황판을 열면 정지 시각이 없다가 첫 Frame 뒤 다시 읽어야 한다 → Task 5 RunBar가 `hasFrame`에 걸어 다시 읽음(화면 확인 단계에서 확인).
5. 개발 서버에서 `/scenarios`가 index.html로 떨어지면 안 된다 → Task 1 viteProxy 테스트.

---

### Task 1: 계약 `ScenarioInfo` + API.md + dev proxy

**Files:**
- Modify: `contracts/models/api.py`, `contracts/models/__init__.py`
- Modify: `scripts/gen_examples.py` (예시 한 줄)
- Generated: `contracts/examples/scenario_info.json`, `contracts/schema/*`, `modules/cop-ui/src/contracts.gen.ts`
- Modify: `contracts/API.md` 5절, `contracts/README.md` 표
- Modify: `modules/cop-ui/vite.config.ts`
- Test: `tests/test_contracts.py`(기존 parametrize), `modules/cop-ui/src/viteProxy.test.ts`(기존)

**Interfaces:**
- Produces: `contracts.models.ScenarioInfo(id: str, name: str, purpose: str = "", active: bool = False)`, TS `interface ScenarioInfo { id: string; name: string; purpose?: string; active?: boolean }`(생성기 결과 그대로).

- [ ] **Step 1: 모델 추가 (예시 없이) → 계약 테스트 실패 확인**

`contracts/models/api.py` 끝에 추가:

```python
class ScenarioInfo(BaseModel):  # GET /scenarios: an operation the gateway can run (decision 0041)
    id: str  # Scenario.id
    name: str  # Operation.name
    purpose: str = ""  # Operation.purpose
    active: bool = False  # the running operation
```

`contracts/models/__init__.py`: `from .api import Accepted, DecisionIn, DirectIn, DraftIn, ScenarioInfo, SwitchIn`, `_MODELS`의 `DecisionIn, DirectIn, SwitchIn, DraftIn, Accepted,` 줄을 `DecisionIn, DirectIn, SwitchIn, DraftIn, Accepted, ScenarioInfo,`로.

Run: `uv run pytest tests/test_contracts.py -n 0 -q`
Expected: FAIL `test_example_matches_model[scenario_info]` (FileNotFoundError scenario_info.json)

- [ ] **Step 2: 예시·TS 생성 → 통과**

`scripts/gen_examples.py`의 `from contracts.models import (` 목록에 `ScenarioInfo,`를 넣고, `examples()` 사전의 `"accepted": ...` 다음 줄에:

```python
        "scenario_info": ScenarioInfo(
            id=SCENARIO.id, name=OPERATION.name, purpose=OPERATION.purpose, active=True
        ),
```

Run: `uv run python scripts/gen_examples.py` 그리고 `uv run python scripts/gen_contracts.py`
Run: `git status --short` — 새 파일 `contracts/examples/scenario_info.json`, `contracts/schema/scenario_info.json`, `contracts.gen.ts` 변경만 있어야 한다. 다른 예시 파일이 바뀌었으면 그 diff를 읽고 이번 변경과 무관하면 `git checkout -- <파일>`로 되돌린다.
Run: `uv run pytest tests/test_contracts.py -n 0 -q`
Expected: PASS

- [ ] **Step 3: API.md에 두 엔드포인트 → proxy 테스트 실패 확인**

`contracts/API.md` 5절 표의 `` | `POST /run/live?speed=` · ... `` 줄 바로 위에 두 줄:

```markdown
| `GET /scenarios` | — | `ScenarioInfo[]`(gateway가 켤 때 읽은 시연 작전, 실행 작전은 `active`, 결정 0041) |
| `POST /scenarios/{id}/activate` | — | `RunState`(그 작전을 실행 작전으로, 작전 시작 직전 `paused`). 없는 id 404 |
```

표 아래 `POST /plays/check`… 문단 다음에 문단 하나:

```markdown
`GET /scenarios`는 gateway가 켤 때 읽은 시연 작전 목록이다(`baengnyeong_night`, `baengnyeong_24h`. 처음 실행 작전은 `KDTH_SCENARIO`, 목록에 없는 파일이면 맨 앞에 붙는다). `POST /scenarios/{id}/activate`는 지금 실행 작전(저장한 플레이·작전 수정 포함)을 메모리 목록에 남겨 두고 그 작전으로 바꾼 뒤 `/run/reset`처럼 작전 시작 직전(`paused`)으로 되돌린다. 나머지 엔드포인트와 `/ws`는 바뀐 실행 작전을 쓴다(결정 0041).
```

`contracts/README.md` 표 `api.py` 줄을 `DecisionIn, DirectIn, SwitchIn, DraftIn, Accepted, ScenarioInfo`로.

Run: `cd modules/cop-ui && npx vitest run src/viteProxy.test.ts`
Expected: FAIL — `["/scenarios", "/scenarios/x/activate"]`가 forward 안 됨

- [ ] **Step 4: proxy 정규식에 scenarios → 통과**

`modules/cop-ui/vite.config.ts`:

```ts
      "^/(operation|plays|vehicles|enemies|ontology|graph|run|decisions|direct|injections|scenarios)(/|\\?|$)": { target: GATEWAY },
```

Run: `cd modules/cop-ui && npx vitest run src/viteProxy.test.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add contracts scripts/gen_examples.py modules/cop-ui/vite.config.ts modules/cop-ui/src/contracts.gen.ts
git commit -m "Part1-29: contract ScenarioInfo, GET /scenarios and POST /scenarios/{id}/activate in API.md, dev proxy (decision 0041)"
```

---

### Task 2: `Live` 시나리오 목록과 `activate`

**Files:**
- Modify: `modules/gateway/live.py`
- Test: Create `modules/gateway/tests/test_live_scenarios.py`

**Interfaces:**
- Consumes: `ScenarioInfo` (Task 1)
- Produces: `Live(scenario: Scenario, init, tick, catalog: Sequence[Scenario] = ())`, `Live.scenarios: dict[str, Scenario]`(목록 순서), `Live.scenario_infos() -> list[ScenarioInfo]`, `Live.activate(scenario_id: str) -> RunState`(없는 id면 `KeyError`, 아무것도 안 바뀜)

- [ ] **Step 1: 실패 테스트 작성**

`modules/gateway/tests/test_live_scenarios.py`:

```python
import pytest

from contracts.models import Scenario
from modules.gateway.live import Live
from modules.gateway.tests.test_live import ROOT, SCENARIO, FakeEngine, make
from modules.gateway.tests.test_live_plays import PATROL_A

DAY = Scenario.model_validate_json(
    (ROOT / "demo/scenarios/baengnyeong_24h.json").read_text(encoding="utf-8")
)


def make_two() -> tuple[Live, FakeEngine]:
    eng = FakeEngine()
    return Live(SCENARIO, eng.init, eng.tick, [SCENARIO, DAY]), eng


def test_scenario_infos_list_the_catalog_with_the_running_one_active():
    live, _ = make_two()
    infos = live.scenario_infos()
    assert [(i.id, i.active) for i in infos] == [
        ("baengnyeong_night", True),
        ("baengnyeong_24h", False),
    ]
    assert infos[1].name == DAY.operation.name
    assert infos[1].purpose == DAY.operation.purpose


def test_activate_runs_the_other_operation_from_its_start_paused():
    live, eng = make_two()
    live.set_speed(5)
    run = live.activate("baengnyeong_24h")
    assert run.status == "paused"
    assert live.scenario.id == "baengnyeong_24h"
    assert eng.inits[-1].id == "baengnyeong_24h"
    assert [i.active for i in live.scenario_infos()] == [False, True]


def test_a_saved_play_survives_going_to_another_operation_and_back():
    live, _ = make_two()
    assert live.save_play(PATROL_A.model_copy(update={"name": "해안 순찰 A2"})).ok
    live.activate("baengnyeong_24h")
    live.activate("baengnyeong_night")
    assert next(p for p in live.scenario.plays if p.id == "patrol_a").name == "해안 순찰 A2"


def test_activating_the_running_operation_again_keeps_its_saved_play():
    live, _ = make_two()
    assert live.save_play(PATROL_A.model_copy(update={"name": "해안 순찰 A2"})).ok
    assert live.activate("baengnyeong_night").status == "paused"
    assert next(p for p in live.scenario.plays if p.id == "patrol_a").name == "해안 순찰 A2"


def test_activate_an_unknown_id_raises_and_changes_nothing():
    live, eng = make_two()
    inits = len(eng.inits)
    with pytest.raises(KeyError):
        live.activate("nope")
    assert live.scenario.id == "baengnyeong_night"
    assert len(eng.inits) == inits


def test_without_a_catalog_only_the_running_scenario_is_listed():
    live, _ = make()
    assert [(i.id, i.active) for i in live.scenario_infos()] == [("baengnyeong_night", True)]


def test_the_running_scenario_wins_over_a_catalog_entry_with_its_id():
    backup = SCENARIO.model_copy(
        update={"operation": SCENARIO.operation.model_copy(update={"name": "백업"})}
    )
    eng = FakeEngine()
    live = Live(backup, eng.init, eng.tick, [SCENARIO, DAY])
    assert [i.name for i in live.scenario_infos()] == ["백업", DAY.operation.name]
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest modules/gateway/tests/test_live_scenarios.py -n 0 -q`
Expected: FAIL (`TypeError: Live.__init__() takes 4 positional arguments but 5 were given`, `AttributeError: 'Live' object has no attribute 'scenario_infos'`)

- [ ] **Step 3: 구현**

`modules/gateway/live.py`:
- 모듈 docstring 첫 줄을 `"""The running operation in process memory: run state, queued operator inputs and the last Frame.`로, 끝에 한 줄 `Other demo operations wait in `scenarios`; `activate` swaps the running one (decision 0041).` 추가.
- import에 `from collections.abc import Callable, Sequence`, contracts import 목록에 `ScenarioInfo`.
- `__init__`과 새 메서드 두 개:

```python
    def __init__(
        self,
        scenario: Scenario,
        init: Callable[[Scenario], Any],
        tick: Callable[[Any, TickInputs], tuple[Any, Frame]],
        catalog: Sequence[Scenario] = (),
    ):
        self.scenario, self._init, self._tick = scenario, init, tick
        # Operations the editor can pick (decision 0041), in catalog order; the running one is put
        # first when the catalog lacks its id and replaces a catalog entry that has it.
        ids = [s.id for s in catalog]
        self.scenarios: dict[str, Scenario] = {} if scenario.id in ids else {scenario.id: scenario}
        for s in catalog:
            self.scenarios.setdefault(s.id, s)
        self.scenarios[scenario.id] = scenario
        self.reset()
```

`save_play` 아래에:

```python
    def scenario_infos(self) -> list[ScenarioInfo]:
        self.scenarios[self.scenario.id] = self.scenario  # saved plays and operation edits
        return [
            ScenarioInfo(
                id=s.id,
                name=s.operation.name,
                purpose=s.operation.purpose,
                active=s.id == self.scenario.id,
            )
            for s in self.scenarios.values()
        ]

    def activate(self, scenario_id: str) -> RunState:
        """Run another operation from its start, paused. The one left keeps what was saved to it."""
        if scenario_id not in self.scenarios:
            raise KeyError(scenario_id)  # 404, before anything changes
        self.scenarios[self.scenario.id] = self.scenario  # write back first: the same id may come back
        self.scenario = self.scenarios[scenario_id]
        return self.reset()
```

- [ ] **Step 4: 통과 확인 + gateway 전체**

Run: `uv run pytest modules/gateway/tests/test_live_scenarios.py -n 0 -q`
Expected: PASS (7 passed)
Run: `uv run pytest modules/gateway -q`
Expected: PASS (기존 테스트 깨짐 없음)

- [ ] **Step 5: Commit**

```bash
git add modules/gateway/live.py modules/gateway/tests/test_live_scenarios.py
git commit -m "Part1-29: Live keeps the demo operations and activate swaps the running one, paused at its start; saved plays stay with their operation (decision 0041)"
```

---

### Task 3: gateway 엔드포인트와 시연 작전 목록

**Files:**
- Modify: `modules/gateway/app.py`
- Test: `modules/gateway/tests/test_app.py`

**Interfaces:**
- Consumes: `Live(scenario, init, tick, catalog)`, `Live.scenarios`, `Live.scenario_infos()`, `Live.activate(id)` (Task 2)
- Produces: `create_app(scenario_path=None, ui_dist=None, engine=None, period_s=0.2, scenario_paths: list[str] | None = None)`, `DEMO_SCENARIOS: list[str]`, `GET /scenarios`, `POST /scenarios/{scenario_id}/activate`

- [ ] **Step 1: 실패 테스트 작성**

`modules/gateway/tests/test_app.py`의 `test_enemies_come_from_the_scenario` 다음에:

```python
def test_scenarios_lists_the_demo_operations_with_the_running_one_active():
    # decision 0041: the editor picks one of the demo operations
    client, _ = fake_app()
    got = client.get("/scenarios").json()
    assert [(s["id"], s["active"]) for s in got] == [
        ("baengnyeong_night", True),
        ("baengnyeong_24h", False),
    ]


def test_activate_switches_what_the_editor_endpoints_answer():
    client, _ = fake_app()
    run = client.post("/scenarios/baengnyeong_24h/activate").json()
    assert run["status"] == "paused"
    assert client.get("/operation").json()["name"] == "백령도 해안 순찰 24시간 교대(가상)"
    assert [v["id"] for v in client.get("/vehicles").json()] == ["d1", "d2", "d3"]
    assert [s["active"] for s in client.get("/scenarios").json()] == [False, True]


def test_activate_an_unknown_scenario_is_404():
    client, _ = fake_app()
    assert client.post("/scenarios/nope/activate").status_code == 404
    assert client.get("/operation").json()["name"] == "백령도 야간 해안 경계"


def test_scenario_paths_replace_the_demo_list():
    client, _ = fake_app(scenario_paths=[SCENARIO])
    assert [s["id"] for s in client.get("/scenarios").json()] == ["baengnyeong_night"]
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest modules/gateway/tests/test_app.py -n 0 -q -k "scenario"`
Expected: FAIL (`/scenarios` 404, `create_app() got an unexpected keyword argument 'scenario_paths'`)

- [ ] **Step 3: 구현**

`modules/gateway/app.py`:
- docstring 셋째 줄 `One operation lives in process memory (`Live`)`를 `The demo operations live in process memory (`Live`, one of them running, decision 0041)`로.
- `from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect`
- `DEFAULT_SCENARIO` 아래:

```python
# Operations the editor can pick (decision 0041). The backup baengnyeong_night_before_0036.json
# shares the night scenario id, so it is left out.
DEMO_SCENARIOS = [
    DEFAULT_SCENARIO,
    str(ROOT / "demo/scenarios/baengnyeong_24h.json"),
]
```

- `create_app` 서명 끝에 `scenario_paths: list[str] | None = None,` 추가, 본문의 `live = Live(...)` 두 줄을:

```python
    path = scenario_path or os.environ.get("KDTH_SCENARIO", DEFAULT_SCENARIO)
    paths = DEMO_SCENARIOS if scenario_paths is None else scenario_paths
    catalog = [eng.load_scenario_json(p) for p in paths]
    live = Live(eng.load_scenario_json(path), eng.init_engine, eng.tick, catalog)
    log.info("scenario %s loaded; %d operations to pick", path, len(live.scenarios))
```

- `@app.get("/enemies")` 핸들러 다음에:

```python
    @app.get("/scenarios")
    async def scenarios():
        return live.scenario_infos()

    @app.post("/scenarios/{scenario_id}/activate")
    async def activate(scenario_id: str):
        if scenario_id not in live.scenarios:
            raise HTTPException(404, f"no scenario {scenario_id}")
        log.info("POST /scenarios/%s/activate", scenario_id)
        return live.activate(scenario_id)
```

- [ ] **Step 4: 통과 확인 + gateway 전체**

Run: `uv run pytest modules/gateway/tests/test_app.py -n 0 -q -k "scenario"`
Expected: PASS (4 passed)
Run: `uv run pytest modules/gateway -q`
Expected: PASS

- [ ] **Step 5: Commit 후 ship(서버 쪽 완성)**

```bash
git add modules/gateway/app.py modules/gateway/tests/test_app.py
git commit -m "Part1-29: gateway reads the demo operations and serves GET /scenarios and POST /scenarios/{id}/activate (decision 0041)"
```

Run: `scripts/ship.sh` — rebase·테스트·smoke 통과 뒤 main에 push. 실패하면 출력의 실패 테스트를 고치고 다시.

---

### Task 4: 화면 액션 세 개 (fetchScenarios · activateScenario · stopsFor)

**Files:**
- Create: `modules/cop-ui/src/features/live/fetchScenarios.ts` + `.test.ts`
- Create: `modules/cop-ui/src/features/editor/activateScenario.ts` + `.test.ts`
- Create: `modules/cop-ui/src/features/run/stopsFor.ts` + `.test.ts`
- Modify: `modules/cop-ui/SPEC.md` (UI-49~51 행)

**Interfaces:**
- Consumes: TS `ScenarioInfo`, `RunState` (contracts.gen.ts), `RUN_STOPS`, `RunStop` (`features/run/runStops.ts`), 예시 `contracts/examples/scenario_info.json` (Task 1)
- Produces: `fetchScenarios(f?: (url: string) => Promise<Response>): Promise<ScenarioInfo[]>`(실패면 `[]`), `activateScenario(id: string, f?: (url, init?) => Promise<Response>): Promise<RunState>`(2xx 아니면 throw), `stopsFor(scenarioId: string | null): RunStop[]`

- [ ] **Step 1: 실패 테스트 세 개 작성**

`modules/cop-ui/src/features/live/fetchScenarios.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import info from "../../../../../contracts/examples/scenario_info.json";
import { fetchScenarios } from "./fetchScenarios";

const reply = (body: unknown, status = 200) => Promise.resolve(new Response(JSON.stringify(body), { status }));

describe("fetchScenarios", () => {
  it("returns the list from GET /scenarios", async () => {
    const urls: string[] = [];
    const got = await fetchScenarios((url) => {
      urls.push(url);
      return reply([info]);
    });
    expect(got).toEqual([info]);
    expect(urls).toEqual(["/scenarios"]);
  });
  it("is empty when the gateway answers an error", async () => {
    expect(await fetchScenarios(() => reply({ detail: "Not Found" }, 404))).toEqual([]);
  });
  it("is empty when the body is not a JSON list", async () => {
    expect(await fetchScenarios(() => Promise.resolve(new Response("<html>", { status: 200 })))).toEqual([]);
    expect(await fetchScenarios(() => reply({ id: "x" }))).toEqual([]);
  });
  it("is empty when the request fails", async () => {
    expect(await fetchScenarios(() => Promise.reject(new TypeError("fetch failed")))).toEqual([]);
  });
});
```

`modules/cop-ui/src/features/editor/activateScenario.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { activateScenario } from "./activateScenario";

const reply = (body: unknown, status = 200) => Promise.resolve(new Response(JSON.stringify(body), { status }));

describe("activateScenario", () => {
  it("POSTs to /scenarios/{id}/activate and returns the RunState", async () => {
    const seen: { url: string; init?: RequestInit }[] = [];
    const run = { status: "paused", speed: 1 };
    const got = await activateScenario("baengnyeong_24h", (url, init) => {
      seen.push({ url, init });
      return reply(run);
    });
    expect(got).toEqual(run);
    expect(seen[0].url).toBe("/scenarios/baengnyeong_24h/activate");
    expect(seen[0].init?.method).toBe("POST");
  });
  it("throws with the status on a non-2xx answer", async () => {
    await expect(activateScenario("nope", () => reply({ detail: "no scenario nope" }, 404))).rejects.toThrow("404");
  });
  it("throws when the server cannot be reached", async () => {
    await expect(activateScenario("x", () => Promise.reject(new TypeError("fetch failed")))).rejects.toThrow();
  });
});
```

`modules/cop-ui/src/features/run/stopsFor.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { RUN_STOPS } from "./runStops";
import { stopsFor } from "./stopsFor";

describe("stopsFor", () => {
  it("gives the night demo its scene stops", () => {
    expect(stopsFor("baengnyeong_night")).toEqual(RUN_STOPS);
  });
  it("gives any other operation, or none known, no stops", () => {
    expect(stopsFor("baengnyeong_24h")).toEqual([]);
    expect(stopsFor(null)).toEqual([]);
  });
});
```

- [ ] **Step 2: 실패 확인**

Run: `cd modules/cop-ui && npx vitest run src/features/live/fetchScenarios.test.ts src/features/editor/activateScenario.test.ts src/features/run/stopsFor.test.ts`
Expected: FAIL (세 모듈 모두 "Failed to resolve import")

- [ ] **Step 3: 구현 세 개**

`modules/cop-ui/src/features/live/fetchScenarios.ts`:

```ts
import type { ScenarioInfo } from "../../contracts.gen";

type Fetch = (url: string) => Promise<Response>;

// GET /scenarios (decision 0041): the operations the gateway can run, the running one active.
// Any failure (old gateway, network, not a list) is [], so the list just does not show.
export async function fetchScenarios(f: Fetch = (url) => fetch(url)): Promise<ScenarioInfo[]> {
  try {
    const r = await f("/scenarios");
    if (!r.ok) return [];
    const list: unknown = await r.json();
    return Array.isArray(list) ? (list as ScenarioInfo[]) : [];
  } catch {
    return [];
  }
}
```

`modules/cop-ui/src/features/editor/activateScenario.ts`:

```ts
import type { RunState } from "../../contracts.gen";

type Fetch = (url: string, init?: RequestInit) => Promise<Response>;

// POST /scenarios/{id}/activate (decision 0041): the gateway runs that operation from its start, paused.
export async function activateScenario(id: string, f: Fetch = (url, init) => fetch(url, init)): Promise<RunState> {
  const url = `/scenarios/${encodeURIComponent(id)}/activate`;
  const r = await f(url, { method: "POST" });
  if (!r.ok) throw new Error(`${url} answered ${r.status}`);
  return (await r.json()) as RunState;
}
```

`modules/cop-ui/src/features/run/stopsFor.ts`:

```ts
import { RUN_STOPS, type RunStop } from "./runStops";

// "다음 사건" stops are scenes of the night demo (Part1-13.1); other operations have none (decision 0041).
export function stopsFor(scenarioId: string | null): RunStop[] {
  return scenarioId === "baengnyeong_night" ? RUN_STOPS : [];
}
```

- [ ] **Step 4: 통과 확인**

Run: `cd modules/cop-ui && npx vitest run src/features/live/fetchScenarios.test.ts src/features/editor/activateScenario.test.ts src/features/run/stopsFor.test.ts`
Expected: PASS (9 tests)

- [ ] **Step 5: SPEC 행 추가**

`modules/cop-ui/SPEC.md` 표 끝(UI-48 다음)에:

```markdown
| UI-49 | fetchScenarios | — | ScenarioInfo[] | GET /scenarios(결정 0041), 오류·연결 실패·목록 아님이면 빈 목록 | 리드 | 완료 |
| UI-50 | activateScenario | 작전 id | RunState | POST /scenarios/{id}/activate(그 작전을 실행 작전으로, 시작 전 멈춤), 2xx 아니면·연결 실패면 오류 | 리드 | 완료 |
| UI-51 | stopsFor | 실행 작전 id | RunStop[] | 야간 시연(baengnyeong_night)이면 RUN_STOPS, 그 밖은 없음(다음 사건 없음, 결정 0041) | 리드 | 완료 |
```

- [ ] **Step 6: Commit**

```bash
git add modules/cop-ui/src/features/live/fetchScenarios.ts modules/cop-ui/src/features/live/fetchScenarios.test.ts modules/cop-ui/src/features/editor/activateScenario.ts modules/cop-ui/src/features/editor/activateScenario.test.ts modules/cop-ui/src/features/run/stopsFor.ts modules/cop-ui/src/features/run/stopsFor.test.ts modules/cop-ui/SPEC.md
git commit -m "Part1-29: UI actions fetchScenarios, activateScenario and stopsFor (decision 0041)"
```

---

### Task 5: 화면 연결 (사이드바 작전 목록 · 시뮬레이션 버튼 · 재생 막대)

**Files:**
- Modify: `modules/cop-ui/src/features/editor/PlaySidebar.tsx`
- Modify: `modules/cop-ui/src/features/editor/EditorScreen.tsx`
- Modify: `modules/cop-ui/src/features/editor/OperationOverview.tsx`
- Modify: `modules/cop-ui/src/features/editor/OperationPanel.tsx`
- Modify: `modules/cop-ui/src/features/run/RunBar.tsx`
- Modify: `modules/cop-ui/src/index.css`, `modules/cop-ui/src/theme.css`

**Interfaces:**
- Consumes: `fetchScenarios`, `activateScenario`, `stopsFor` (Task 4), `postRun` (`features/run/runApi.ts`), `loadEditorData` (`features/editor/loadEditorData.ts`)
- Produces: `PlaySidebar` props `scenarios?: ScenarioInfo[]`, `onPickScenario?: (id: string) => void`; `OperationOverview`·`OperationPanel` prop `onSimulate?: () => void`

화면 컴포넌트는 테스트를 생략한다(cop-ui AGENTS.md). 확인은 타입 검사·빌드·실제 화면.

- [ ] **Step 1: PlaySidebar 작전 목록**

`PlaySidebar.tsx` import에 `import type { ScenarioInfo } from "../../contracts.gen";`, `Props`에:

```ts
  // Decision 0041: the operations the gateway can run; picking another makes it the running one.
  scenarios?: ScenarioInfo[];
  onPickScenario?: (id: string) => void;
```

함수 인자에 `scenarios = [], onPickScenario`를 더하고, `{top}` 바로 다음에:

```tsx
      {scenarios.length > 0 && (
        <div className="ops">
          <div className="group">작전</div>
          {scenarios.map((s) => (
            <button key={s.id} className={s.active ? "item op active" : "item op"} title={s.purpose}
              onClick={() => !s.active && onPickScenario?.(s.id)}>
              {s.name}
            </button>
          ))}
        </div>
      )}
```

- [ ] **Step 2: OperationPanel·OperationOverview 시뮬레이션 버튼**

`OperationPanel.tsx`: `Props`에 `onSimulate?: () => void;`, 인자에 `onSimulate`, `<h2>{op.name}</h2>`를:

```tsx
        <div className="op-title">
          <h2>{op.name}</h2>
          {onSimulate && <button className="save simulate" onClick={onSimulate}>▶ 시뮬레이션</button>}
        </div>
```

`OperationOverview.tsx`: `Props`에 `onSimulate?: () => void;`, 인자에 `onSimulate`, `<OperationPanel ... onOpen={onOpen} />`에 `onSimulate={onSimulate}` 추가.

- [ ] **Step 3: EditorScreen 작전 고르기·시뮬레이션**

import 추가:

```ts
import type { Play, ScenarioInfo } from "../../contracts.gen";
import { fetchScenarios } from "../live/fetchScenarios";
import { postRun } from "../run/runApi";
import { activateScenario } from "./activateScenario";
```

(기존 `import type { Play } from "../../contracts.gen";` 줄은 위 줄로 바꾼다.)

`const [fresh, setFresh] = ...` 다음에:

```ts
  // Decision 0041: the operations to pick, and why a pick or "시뮬레이션" failed.
  const [scenarios, setScenarios] = useState<ScenarioInfo[]>([]);
  const [opError, setOpError] = useState<string | null>(null);
```

`useEffect` 본문에 `fetchScenarios().then(setScenarios);` 한 줄 추가.

`const save = ...` 정의 다음에:

```ts
  // Picking another operation makes it the gateway's running one, paused at its start; the editor reads it
  // again and drops what belonged to the old one (unsaved edits, check results, view history).
  const pickScenario = (id: string) => {
    setOpError(null);
    activateScenario(id)
      .then(() => Promise.all([loadEditorData(), fetchScenarios()]))
      .then(
        ([d, list]) => {
          setData(d);
          setScenarios(list);
          setEdits({});
          setResults({});
          setFresh({});
          setNav({ current: OVERVIEW, stack: [] });
        },
        (e) => {
          console.warn("editor: operation switch failed", e);
          setOpError(`작전을 바꾸지 못했습니다 (${String(e)})`);
        },
      );
  };
  // "▶ 시뮬레이션": the run goes back to the operation's start, paused, and the live tab opens (no auto play).
  const simulate = () => {
    setOpError(null);
    postRun("/run/reset").then((r) => {
      if (r.ok) location.hash = "#live";
      else setOpError(`시뮬레이션을 열지 못했습니다 (${r.error})`);
    });
  };
```

JSX: `<PlaySidebar ...>`에 `scenarios={scenarios} onPickScenario={pickScenario}`, `<main className="editor-main">` 바로 안 첫 줄에 `{opError && <div className="issue">⚠ {opError}</div>}`, `<OperationOverview ... onOpen={open} />`에 `onSimulate={simulate}`.

- [ ] **Step 4: RunBar 정지 시각을 실행 작전에 맞춤**

`RunBar.tsx` import:

```ts
import { fetchScenarios } from "../live/fetchScenarios";
import { nextStop, type RunStop } from "./runStops";
import { stopsFor } from "./stopsFor";
```

(기존 `import { nextStop } from "./runStops";` 줄은 위 줄로 바꾼다.)

`const [armedAt, ...]` 다음에:

```ts
  // "다음 사건" stops of the running operation (decision 0041). Like startedMs, read again once a Frame
  // arrives if the gateway was down when the screen opened.
  const [stops, setStops] = useState<RunStop[] | null>(null);
  useEffect(() => {
    if (stops !== null) return;
    fetchScenarios().then((list) => {
      if (list.length) setStops(stopsFor(list.find((s) => s.active)?.id ?? null));
    });
  }, [hasFrame, stops]);
```

`const next = offset === null ? null : nextStop(offset);`를 `const next = offset === null ? null : nextStop(offset, stops ?? []);`로.

- [ ] **Step 5: CSS**

`index.css`의 `.op-head h2 { margin: 0 0 6px; }` 다음 줄에:

```css
.op-title { display: flex; align-items: baseline; gap: 12px; }
```

`theme.css`의 `.play-sidebar .item.on { ... }` 다음 줄에:

```css
.play-sidebar .item.op::before { content: "○ "; color: var(--dim); }
.play-sidebar .item.op.active { color: var(--text); cursor: default; }
.play-sidebar .item.op.active::before { content: "● "; color: var(--live); }
```

- [ ] **Step 6: 타입 검사·테스트·빌드**

Run: `cd modules/cop-ui && npx tsc -b`
Expected: 오류 없음
Run: `cd modules/cop-ui && npx vitest run`
Expected: PASS (전부)
Run: `cd modules/cop-ui && npm run build`
Expected: 빌드 성공

- [ ] **Step 7: 실제 화면 확인**

`scripts/dev.sh`를 백그라운드로 띄우고(gateway 8000 + vite 5173) 브라우저로 `http://localhost:5173/#editor`:
1. 사이드바 "작전"에 "● 백령도 야간 해안 경계", "○ 백령도 해안 순찰 24시간 교대(가상)".
2. 24시간 작전 클릭 → 작전 개요 제목이 바뀌고 기체 3대, 플레이 목록이 순찰 플레이들.
3. "▶ 시뮬레이션" → 상황판 탭, 드론 3대가 출발 위치, "▶ 재생" 상태(멈춤), "다음 사건 없음".
4. 편집기로 돌아가 야간 작전 클릭 → 시뮬레이션 → 상황판에 5대, "다음 사건 ▸ 16:25 보고 카드".
헤드리스 스크린샷이 필요하면 메모리 `reference-headless-map-screenshots`대로 CDP로 실제 대기 후 촬영. 확인 뒤 dev 서버를 끈다.

- [ ] **Step 8: Commit**

```bash
git add modules/cop-ui/src
git commit -m "Part1-29: editor sidebar lists the operations and switches the running one, 시뮬레이션 resets and opens the live tab paused, run bar stops follow the running operation (decision 0041)"
```

---

### Task 6: 기록과 반영

**Files:**
- Modify: `demo/BUILT_HERE.md`

- [ ] **Step 1: BUILT_HERE 한 줄**

`demo/BUILT_HERE.md` "해커톤 중 만든 것" 표 끝에(시각은 `date '+%m/%d %H:%M'`로 KST):

```markdown
| 10/10 HH:MM | gateway, cop-ui | Part1-29 작전 고르기(결정 0041): gateway가 시연 작전 2개(야간 경계·24시간 해안 순찰 교대)를 메모리에 들고 GET /scenarios·POST /scenarios/{id}/activate로 실행 작전을 바꿈(저장한 플레이는 작전별로 남음). 편집기 사이드바 작전 목록, 작전 개요 '▶ 시뮬레이션'(시작 전 멈춤으로 상황판), 다음 사건은 야간 작전만 | kth9245 |
```

- [ ] **Step 2: Commit, ship, 할 일 완료**

```bash
git add demo/BUILT_HERE.md
git commit -m "Part1-29: BUILT_HERE line for operation select"
```

Run: `scripts/ship.sh` — 통과 확인.
Run: `uv run python scripts/task.py done Part1-29`
