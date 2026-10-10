# T1 공격 작전 1단계 Implementation Plan (고정 거점, 방출, 점수, 카드)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 새 작전 `baengnyeong_strike`("해안 거점 무력화", 가상)를 만든다. 가상 고정 적 거점 3곳(하나는 방출 중)을 정찰 드론이 RF로 먼저 잡고, 스캔한 뒤 위험 점수가 붙은 발견 카드를 올린다. 작전 고르기에서 고를 수 있다.

**Architecture:** 코드(계약·sim·runtime·sensing)는 바꾸지 않는다. 시나리오 JSON을 생성 스크립트(`scripts/make_coast_routes.py`와 같은 방식)로 만들고, 거점은 기존 표적 종류 `unknown`에 속도 0, 대기 Role, 방출 시작 시각으로 표현한다. 작전 목록(`DEMO_SCENARIOS`)에 한 줄을 더하고 그 목록을 가정한 테스트를 맞춘다.

**Tech Stack:** Python, pytest(`uv run pytest …`, 디버깅 `-n 0`), 시나리오 JSON.

**Spec:** `docs/superpowers/specs/2026-10-10-t1-coastal-strike-operation-design.md`(1단계, 8절).

## Global Constraints

- **cop-ui, `contracts/models/**`, `modules/{sim,sensing,runtime,safety,role}` 코드는 수정하지 않는다.** 바꾸는 것은 시나리오 JSON, 생성 스크립트, 테스트, `DEMO_SCENARIOS` 한 줄, 기록 문서뿐이다.
- 용어는 **Role**을 쓴다(결정 0052). 코드·JSON 키는 이미 `roles`, `role_id`다.
- 모든 좌표·수치는 **가상**이다. 실제 시설과 무관하다. 타격과 식별은 이 단계에 없다(2~3단계).
- **`appear_offset_ms`는 0이면 안 된다.** `spawn_enemies`는 `t − dt < 시작 + offset <= t`일 때만 적을 만들어서 0이면 첫 틱 전에 지나가 **거점이 영영 나타나지 않는다**(사전 실험에서 확인). 1000 ms로 한다.
- 시나리오 JSON은 생성 뒤에 **정본**이다(결정 0035). 스크립트는 다시 만들 때만 돌린다.
- 작업은 자기 worktree에서, 모든 코드 변경은 실패하는 테스트를 먼저 쓴다(결정 0014). 커밋 메시지 끝에 `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`를 붙인다.
- 같은 파일(`modules/gateway/app.py`의 `DEMO_SCENARIOS`, 그 목록을 가정한 `modules/gateway/tests/test_app.py`, `tests/test_demo_routes.py`)을 황승주의 작전도 고친다. **rebase 충돌이 나면 양쪽 항목을 모두 살리고** 기대 목록을 같은 순서로 맞춘다.

## Review Focus

- 거점이 실제로 나타난다(`appear_offset_ms` 함정): Task 2의 틱 루프 테스트가 잡는다.
- **RF로 먼저 잡히고 나중에 스캔된다**(`heard < seen`): 사전 측정 T+05:02 → T+06:30. 이 순서가 시연 이야기의 시작이다.
- 무음 거점(B·C)은 RF로 안 잡히고, 카드는 방출 거점 하나에서만 뜬다(Task 2).
- 수상정이 칠 수 있어야 한다: 거점이 해안의 바다 점(`to_sea`)에서 **100 m 이내**(Task 1).
- 거점은 작전 구역 안이다(`outside_zone` 규칙)(Task 1).
- 야간·24시간 작전은 영향이 없다(Task 3의 전체 테스트).

## 사전 실험으로 확정한 값 (실제 틱 루프, 일회용 스크립트)

| 거점 | 좌표(위도, 경도) | 방출 | 해안 바다 점까지 | 순찰 경로까지 | 기준점(37.978, 124.70)까지 | 점수 |
|---|---|---|---|---|---|---|
| `site_a` | 37.98230, 124.72247 | **방출 중** | 94 m | 495 m | 2027 m(근접 +0.15) | 0.75 |
| `site_b` | 37.96382, 124.74617 | 무음 | 92 m | 113 m | 4343 m(근접) | 0.45 |
| `site_c` | 37.97272, 124.64615 | 무음 | 90 m | 320 m | 4756 m(근접) | 0.45 |

d1이 `site_patrol`(북쪽 해안 경로)을 돌 때: `site_a`가 **T+05:02에 RF로 잡히고**, T+06:30에 스캔되어 **T+06:36에 카드**가 뜬다(d1, 721 m, 점수 0.75). `check_operation`은 통과(d1 귀환 배터리 예상 58.2%).

---

### Task 1: 시나리오 생성 스크립트와 시나리오 JSON

**Files:**
- Create: `scripts/make_strike_scenario.py`
- Create(생성): `demo/scenarios/baengnyeong_strike.json`
- Test: `tests/test_strike_scenario.py`

**Interfaces:**
- Produces: `build() -> dict`(검증된 시나리오 dict), `main()`은 JSON을 쓴다. 시나리오 id `baengnyeong_strike`, 적 `site_a/b/c`, Role `site_patrol`(드론용 탐색 순찰), `site_hold`(적 대기).

- [ ] **Step 1: 실패하는 테스트**

```python
import json
from pathlib import Path

import pytest

from modules.role import check_operation
from modules.safety import point_in_polygon
from modules.sim import load_scenario_json
from shared.geo import dist_m
from shared.land import inside, to_sea

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def sc():
    return load_scenario_json(str(ROOT / "demo/scenarios/baengnyeong_strike.json"))


def test_one_drone_starts_on_the_north_search_patrol(sc):
    assert sc.id == "baengnyeong_strike"
    assert sc.operation.assign["d1"] == "site_patrol"
    assert {v for k, v in sc.operation.assign.items() if k != "d1"} == {"standby"}


def test_three_fixed_unknown_sites_and_only_site_a_emits(sc):
    assert [e.id for e in sc.enemies] == ["site_a", "site_b", "site_c"]
    for e in sc.enemies:
        assert (e.kind.value, e.speed_mps, e.role_id) == ("unknown", 0.0, "site_hold")
    assert [e.emit_start_offset_ms for e in sc.enemies] == [0, None, None]


def test_sites_appear_after_the_first_tick(sc):
    # spawn_enemies needs t - dt < start + offset <= t, so an offset of 0 never spawns the enemy
    assert all(e.appear_offset_ms >= sc.tick_ms for e in sc.enemies)


def test_sites_are_inside_the_zone_and_a_strike_boat_can_reach_them(sc):
    for e in sc.enemies:
        assert point_in_polygon(e.pos, sc.operation.zone), e.id
        assert inside(e.pos, sc.land), e.id  # on the island
        assert dist_m(e.pos, to_sea(e.pos, sc.land)) <= 100, e.id  # the USV aims at the nearest sea point


def test_sites_are_within_threat_range_of_the_watch_point(sc):
    wp = sc.watch_points[0]
    for e in sc.enemies:
        assert dist_m(e.pos, wp.pos) <= 3 * wp.radius_m, e.id  # near step, else a silent site never scores 0.40


def test_the_operation_passes_the_role_checks(sc):
    roles, specs = {r.id: r for r in sc.roles}, {v.id: v for v in sc.vehicles}
    assert check_operation(sc.operation, roles, specs).ok


def test_the_json_is_what_the_script_builds(sc):
    from scripts.make_strike_scenario import build

    on_disk = json.loads((ROOT / "demo/scenarios/baengnyeong_strike.json").read_text(encoding="utf-8"))
    assert build() == on_disk
```

- [ ] **Step 2: 실패 확인** — `uv run pytest tests/test_strike_scenario.py -n 0 -q` → `FileNotFoundError: …baengnyeong_strike.json`(파일이 아직 없음).
- [ ] **Step 3: 생성 스크립트** — `scripts/make_strike_scenario.py`:

```python
"""Strike operation "해안 거점 무력화" (virtual): demo/scenarios/baengnyeong_strike.json.

Three fixed enemy sites on the north coast are unknown-kind targets with speed 0, a hold Role and an emission
start (no contract change, spec 8절). site_a emits from the start and is the first one the north search patrol
meets, so its RF shows before the drone sees it. The JSON is the source afterwards (decision 0035);
rerun only to rebuild. Usage: uv run python scripts/make_strike_scenario.py
"""

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT)]

from contracts.models import Scenario  # noqa: E402

NIGHT = ROOT / "demo" / "scenarios" / "baengnyeong_night.json"
DAY = ROOT / "demo" / "scenarios" / "baengnyeong_24h.json"
OUT = ROOT / "demo" / "scenarios" / "baengnyeong_strike.json"
# (id, lat, lon, emit_start_offset_ms); virtual positions on the island's north coast, inside the zone
SITES = [
    ("site_a", 37.98230, 124.72247, 0),
    ("site_b", 37.96382, 124.74617, None),
    ("site_c", 37.97272, 124.64615, None),
]
# spawn_enemies needs t - dt < start + offset <= t: an offset of 0 would never spawn the enemy
APPEAR_MS = 1000


def site_hold() -> dict:
    step = {"id": "hold", "name": "대기", "do": {"kind": "hold", "params": {}}, "on": [], "report": None, "ui": {}}
    return {"id": "site_hold", "name": "적: 거점 대기", "domains": ["ground"], "steps": [step],
            "entry": "hold", "origin": "human", "approved": True, "template": False,
            "emergency": {"battery_low_pct": 30.0, "link_lost_step": None, "battery_low_step": None,
                          "operator_call_step": None}}  # fmt: skip


def build() -> dict:
    night = json.loads(NIGHT.read_text(encoding="utf-8"))
    day = json.loads(DAY.read_text(encoding="utf-8"))
    roles = {r["id"]: r for r in night["roles"]}
    patrol = copy.deepcopy(next(r for r in day["roles"] if r["id"] == "coast_a"))
    patrol["id"], patrol["name"] = "site_patrol", "거점 탐색 순찰 · 북"
    patrol["steps"][1]["report"] = {"text": "미식별 거점 감지", "choices": [], "auto_choices": True}
    north = next(r for r in day["routes"] if r["id"] == "coast_a")
    skip = ("patrol_a", "patrol_b", "coast_a", "coast_b")
    op = night["operation"] | {
        "id": "op_strike",
        "name": "해안 거점 무력화(가상)",
        "purpose": "정찰 드론이 가상 해안 거점을 RF 방출로 먼저 찾고 스캔해서 위협 카드를 올린다(1단계)",
        "assign": {"d1": "site_patrol", "d2": "standby", "d3": "standby", "d4": "standby",
                   "usv": "standby", "ugv": "standby"},
        "reserve": {}, "switches": [], "rotation": [], "rotation_pools": {}, "rotation_roles": [],
    }  # fmt: skip
    enemies = [
        {"id": i, "kind": "unknown", "speed_mps": 0.0, "appear_offset_ms": APPEAR_MS,
         "pos": {"lat": lat, "lon": lon, "alt_m": 0.0}, "from_enemy": None, "role_id": "site_hold",
         "emit_start_offset_ms": emit}
        for i, lat, lon, emit in SITES
    ]  # fmt: skip
    out = night | {
        "id": "baengnyeong_strike",
        "operation": op,
        "roles": [patrol, roles["standby"], roles["go_home"], roles["watch"], roles["approach"], site_hold()],
        "events": [],
        "enemies": enemies,
        "routes": [north, *(r for r in night["routes"] if r["id"] not in skip)],
    }  # fmt: skip
    Scenario.model_validate(out)
    return out


def main() -> None:
    out = build()
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{OUT.name}: {len(out['enemies'])} sites, {len(out['roles'])} roles, {len(out['routes'])} routes")


if __name__ == "__main__":
    main()
```
  (`op`의 `id`는 작전 id, 시나리오 id와 별개다. 야간·24시간과 같은 방식이다.)
- [ ] **Step 4: 생성** — `uv run python scripts/make_strike_scenario.py` → `baengnyeong_strike.json: 3 sites, 6 roles, N routes`.
- [ ] **Step 5: 통과 확인** — `uv run pytest tests/test_strike_scenario.py -n 0 -q` → 7개 통과. 실패하면 이유를 읽는다(좌표 검사 실패는 표의 값과 대조).
- [ ] **Step 6: 커밋** — 스크립트, JSON, 테스트.

---

### Task 2: 틱 루프 수락 테스트 (RF 먼저, 스캔, 카드)

**Files:**
- Test: `modules/gateway/tests/test_strike_threat.py`

**Interfaces:**
- Consumes: Task 1의 `baengnyeong_strike.json`.

- [ ] **Step 1: 테스트 작성**

```python
"""Strike operation stage 1: the emitting site is heard before it is seen, then gets a threat card."""

from contracts.models import TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json

SC = load_scenario_json("demo/scenarios/baengnyeong_strike.json")
START, MIN = SC.operation.started_ms, 60_000


def _run_ten_minutes():
    es, heard, seen = init_engine(SC), None, None
    for _ in range(10 * MIN // SC.tick_ms):
        es, _ = tick(es, TickInputs())
        a = next((t for t in es.targets if t.id == "site_a"), None)
        if a and a.rf_detected and heard is None:
            heard = es.t_ms - START
        if a and a.seen_by and seen is None:
            seen = es.t_ms - START
    return es, heard, seen


def test_the_sites_spawn_and_the_emitting_one_is_heard_before_it_is_seen():
    es, heard, seen = _run_ten_minutes()
    assert {t.id for t in es.targets} == {"site_a", "site_b", "site_c"}  # an offset of 0 would leave none
    assert heard is not None and seen is not None and heard < seen


def test_only_the_emitting_site_gets_a_card_and_it_has_its_threat_reasons():
    es, _, _ = _run_ten_minutes()
    cards = [r for r in es.reports if r.kind == "target_detected"]
    assert [(r.vehicle_id, r.target_id) for r in cards] == [("d1", "site_a")]
    assert cards[0].text.startswith("미식별 거점 감지")
    a = next(t for t in es.targets if t.id == "site_a")
    assert a.threat == 75 and a.threat_reasons == ["kind_unknown", "near_watch_radius", "rf_emission"]


def test_the_silent_sites_are_not_heard():
    es, _, _ = _run_ten_minutes()
    assert not any(t.rf_detected for t in es.targets if t.id in ("site_b", "site_c"))
```

- [ ] **Step 2: 확인** — `uv run pytest modules/gateway/tests/test_strike_threat.py -n 0 -q`. Task 1이 끝났으니 곧바로 통과해야 한다(이 테스트는 시나리오 데이터를 검증하는 수락 테스트라서 새 코드가 없다). **통과하면** 먼저 실패를 본 것으로 치지 않으므로, `appear_offset_ms`를 일시적으로 `0`으로 바꿔 첫 테스트가 `targets == set()`로 **실패하는지** 보고 되돌린다(함정이 테스트로 잡힘을 증명). 실패하면 이유를 읽는다(시각은 T+05:02, T+06:30, T+06:36 근처여야 한다).
- [ ] **Step 3: 커밋.**

---

### Task 3: 작전 고르기에 올리기

**Files:**
- Modify: `modules/gateway/app.py`(`DEMO_SCENARIOS`), `modules/gateway/tests/test_app.py`, `tests/test_demo_routes.py`

- [ ] **Step 1: 테스트를 먼저 고친다(RED).**
  - `modules/gateway/tests/test_app.py`의 `test_scenarios_lists_the_demo_operations_with_the_running_one_active` 기대 목록을 `("baengnyeong_night", True), ("baengnyeong_24h", False), ("baengnyeong_strike", False)`로, `test_activate_switches_what_the_editor_endpoints_answer`의 마지막 줄을 `== [False, True, False]`로 바꾼다.
  - `tests/test_demo_routes.py`의 `FILES`에 `"baengnyeong_strike.json"`을 더한다(경로가 구역 안이고, 모든 순찰이 목록의 경로 이름을 쓰는지 검사된다).
- [ ] **Step 2: 실패 확인** — `uv run pytest modules/gateway/tests/test_app.py tests/test_demo_routes.py -n 0 -q` → 작전이 목록에 없어서 두 테스트가 실패하고 `test_demo_routes[baengnyeong_strike.json]`은 통과한다.
- [ ] **Step 3: 구현** — `DEMO_SCENARIOS`에 `str(ROOT / "demo/scenarios/baengnyeong_strike.json"),`를 마지막 줄로 더한다.
- [ ] **Step 4: 통과 확인** — 같은 명령, 그다음 `uv run pytest modules/gateway tests -q`(야간·24시간 영향 없음 확인).
- [ ] **Step 5: 커밋.**

---

### Task 4: 전체 검증, 기록, 올리기

- [ ] **Step 1: 전체 검증**(각 출력을 읽는다) — `uv run pytest`, `uv run python scripts/smoke.py`, `scripts/check.sh --all`, cop-ui는 수정이 없지만 `npx tsc -b`, `npx vitest run`이 통과하는지 확인(`git diff --stat`에 `modules/cop-ui`가 없어야 한다).
- [ ] **Step 2: 실제 서버 확인** — UI 빌드 후 서버를 띄우고(`uvicorn …`, 절대 경로), `GET /scenarios`가 세 작전을 돌려주는지, `POST /scenarios/baengnyeong_strike/activate` 뒤 `POST /run/jump?offset_ms=420000`(T+07:00)으로 건너가 WebSocket Frame에서 `site_a`의 `rf_detected`가 True이고 발견 카드가 한 장인지 확인한다.
- [ ] **Step 3: 기록** — `demo/BUILT_HERE.md`에 한 줄(1단계: 작전 `baengnyeong_strike`, 거점은 기존 종류 `unknown`, 계약 변경 없음, 생성 스크립트).
- [ ] **Step 4: ship** — `scripts/ship.sh`. 충돌이 `BUILT_HERE.md`·`DEMO_SCENARIOS`·두 테스트의 기대 목록이면 양쪽을 모두 살린다. 올린 뒤 원격에서 커밋을 직접 확인한다.
- [ ] **Step 5: 알림(선택)** — 황승주: 같이 고친 파일 3개(`app.py`의 목록, `test_app.py`, `test_demo_routes.py`). 리드: `scripts/qa/operation_select.json`의 "작전 목록은 두 개"라는 기대가 세 개로 바뀐다(QA 파일은 건드리지 않았다).

---

## Self-Review

- 스펙 커버: 1단계(고정 거점, 방출 프로필, 점수, 카드)는 Task 1~2, 작전 고르기는 Task 3. 식별·신뢰도, 교전 가능성, 부수피해, 결과 평가, 무장 수량, 통신 두절 자율은 의도적으로 제외(2~5단계).
- 타입·이름 일관성: 거점 id `site_a/b/c`, Role `site_patrol`/`site_hold`, 시나리오 id `baengnyeong_strike`가 Task 1~3에서 같다.
- 알려진 한계: 카드가 뜨면 d1이 거점 위에서 멈춰 있으므로 `site_b`·`site_c`는 다른 드론이 이어받아야 보인다(이어받기 선택지가 그 역할). 타격 Role과 승인 카드 연결은 3단계다. 점수 0.75, 시각 T+05:02·06:30·06:36은 사전 실험값이며 Task 2의 테스트가 관계(`heard < seen`)와 점수를 고정한다.
