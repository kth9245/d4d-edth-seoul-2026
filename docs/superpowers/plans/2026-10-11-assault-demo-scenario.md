# 발표용 공격 작전 시연 시나리오 (baengnyeong_assault) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 발표 라이브 시연의 유일한 공격 작전을 데이터로 만든다 — 1막 거점 타격(RF 단서→직접 조종→식별→사람 승인→타격)과 2막 적 무인 장비 타격(결정 한 번에 공중·해상·지상)을 한 실행에서 보인다.

**Architecture:** 엔진 코드는 바꾸지 않는다. 새 시나리오 JSON과 Role 데이터만 만들고, 생성 스크립트(`scripts/make_assault_scenario.py`)가 야간 작전에서 온톨로지·구역·기체 제원·공용 Role을 읽어 6대 편대와 적·Role을 조립한다. 1막 거점은 종류 `unknown`이라 식별 신뢰도와 자동 타격 카드(기존 GW-12·GW-13)가 동작하고, 2막 적 무인 장비(`usv`·`ugv`)는 Role 발견 카드의 선택지(야간 작전 '함께 타격' 방식)로 타격을 연다. 선택지로 옮겨진 기체에 `apply_decision`이 운용자 결정 id를 달아 safety 규칙 1을 통과한다.

**Tech Stack:** Python 3(pydantic 계약 모델, `scripts/`), pytest(+xdist), FastAPI(gateway), React/TypeScript+vitest(cop-ui), uv.

**Spec:** `docs/superpowers/specs/2026-10-11-assault-demo-scenario-design.md`

## Global Constraints
- 시연은 인터넷 없이 동작한다. AI 초안 캐시 키가 맞도록 새 작전의 `zone`·`area`는 야간 작전(`baengnyeong_night`)과 같은 폴리곤을 쓴다(정책 1, 결정 0062). (verbatim: zone·area = 야간 작전 그대로)
- 공개·가상 데이터만. 사람(`person`) 표적을 두지 않는다(정책 2, 결정 0078).
- 좌표는 WGS84 위경도(도), 고도 m, 시간 `t_ms`(UTC epoch ms)(정책 3).
- 액션 파일 규칙은 이 작업에 해당 없음(새 코드 모듈 없음). 생성 스크립트·테스트·데이터만 추가한다. 줄 수 제한 없음(결정 0023).
- `baengnyeong_strike`·`scripts/make_strike_scenario.py`와 그 테스트, 야간·24시간 작전, contracts·sim·sensing·runtime·safety·role 코드는 **고치지 않는다**(결정 0077, 통합 1 레거시 공개 API 보존).
- TDD(결정 0014): 각 코드·데이터 변경은 실패하는 테스트를 먼저 쓴다. 생성 스크립트는 "스크립트가 쓴 JSON == 디스크" 테스트로 고정한다(결정 0035 패턴).
- 작전 id = `baengnyeong_assault`. 기체 id = `r1`·`r2`·`a1`·`a2`·`usv`·`ugv`. 적 id = `site_rf`·`e_usv`·`e_ugv1`·`e_ugv2`.

## Review Focus
- **적 무인 장비(`usv`·`ugv`)에는 식별·자동 타격 카드가 안 붙는다** — 코드가 `unknown`만 처리한다. 2막 타격이 Role 카드 선택지로만 열리는지 Task 3이 검증한다.
- **2막 '함께 타격' 한 번에 옮겨진 공격 드론·수상정에 운용자 결정 id가 붙어 strike가 안전 규칙 1(출처)을 통과하는지** — 안 붙으면 `no_provenance`로 막힌다. Task 3이 `es.blocks` 비어 있음으로 검증한다.
- **직접 조종 목표·타격 목표가 작전 구역 안이고 귀환 배터리가 충분한지** — 벗어나면 규칙 2·3이 막아 시연이 멈춘다. Task 2·3이 `es.blocks` 비어 있음으로 검증한다.
- **1막 거점을 한 드론이 식별됨까지 올리는지** — RF(+25)+스캔(+40)만으로 65라 식별 기준 70 미만이다. 관측 지속(+최대 20) 또는 둘째 관측(+15)이 필요하다. Task 2가 `ident_state == "identified"` 도달로 검증한다.
- **AI 초안 캐시가 인터넷 없이 맞는지** — zone·area가 야간과 달라지면 캐시 키가 어긋나 외부 호출이 난다. Task 1이 `zone`·`area`가 야간과 같음을 검증한다.

---

### Task 1: 생성 스크립트와 시나리오 JSON, 구조 테스트

**Files:**
- Create: `scripts/make_assault_scenario.py`
- Create: `demo/scenarios/baengnyeong_assault.json` (스크립트 출력)
- Create: `tests/test_assault_scenario.py`

**Interfaces:**
- Consumes: `demo/scenarios/baengnyeong_night.json`(온톨로지·zone·area·routes·기체 제원·Role `standby`·`go_home`·`watch`·`approach`·`strike`), `contracts.models.Scenario`, `modules.sim.load_scenario_json`, `modules.role.check_operation`, `modules.safety.point_in_polygon`, `shared.land.inside`·`to_sea`, `shared.geo.dist_m`.
- Produces: `scripts.make_assault_scenario.build() -> dict`(시나리오 dict), 디스크 JSON `demo/scenarios/baengnyeong_assault.json`. 작전 id `baengnyeong_assault`, 기체 `["usv","r1","r2","a1","a2","ugv"]`, 적 `["site_rf","e_usv","e_ugv1","e_ugv2"]`, Role `site_recon`(r1·r2), `sea_patrol`(usv), `watch_landing`(ugv), 그리고 `standby`·`go_home`·`watch`·`approach`·`strike`·`site_hold`·`enemy_usv_run`·`enemy_hold`.

- [ ] **Step 1: 실패하는 구조 테스트를 쓴다**

```python
# tests/test_assault_scenario.py
import json
from pathlib import Path

import pytest

from contracts.models import GeoPoint
from modules.role import check_operation
from modules.safety import point_in_polygon
from modules.sim import load_scenario_json
from shared.land import inside

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "demo/scenarios/baengnyeong_assault.json"


@pytest.fixture(scope="module")
def sc():
    return load_scenario_json(str(PATH))


def test_fleet_is_six_vehicles_air_sea_ground(sc):
    assert [v.id for v in sc.vehicles] == ["usv", "r1", "r2", "a1", "a2", "ugv"]
    kinds = {v.id: v.kind for v in sc.vehicles}
    assert kinds == {
        "usv": "armed_usv",
        "r1": "recon_drone",
        "r2": "recon_drone",
        "a1": "armed_drone",
        "a2": "armed_drone",
        "ugv": "ground_robot",
    }
    assert sc.operation.vehicle_ids == [v.id for v in sc.vehicles]


def test_enemies_are_one_unknown_site_one_usv_two_ugv(sc):
    kinds = {e.id: e.kind.value for e in sc.enemies}
    assert kinds == {"site_rf": "unknown", "e_usv": "usv", "e_ugv1": "ugv", "e_ugv2": "ugv"}
    by_id = {e.id: e for e in sc.enemies}
    assert by_id["site_rf"].emit_start_offset_ms == 0  # RF from the start
    assert by_id["site_rf"].speed_mps == 0.0 and by_id["site_rf"].role_id == "site_hold"
    # the two ground robots are dropped by the enemy usv: they spawn at its position
    assert by_id["e_ugv1"].from_enemy == "e_usv" and by_id["e_ugv2"].from_enemy == "e_usv"
    assert by_id["e_usv"].from_enemy is None and by_id["e_usv"].role_id == "enemy_usv_run"
    assert all(e.appear_offset_ms >= sc.tick_ms for e in sc.enemies)  # offset 0 never spawns


def test_no_person_target_anywhere(sc):
    text = PATH.read_text(encoding="utf-8")
    assert '"person"' not in text and "person" not in {e.kind.value for e in sc.enemies}


def test_zone_and_area_match_night_for_the_ai_draft_cache(sc):
    night = load_scenario_json(str(ROOT / "demo/scenarios/baengnyeong_night.json"))
    assert sc.operation.zone == night.operation.zone
    assert sc.operation.area == night.operation.area


def test_site_rf_is_inland_off_the_recon_route_but_in_rf_range(sc):
    site = next(e for e in sc.enemies if e.id == "site_rf").pos
    assert inside(site, sc.land)  # on the island, not a sea point
    assert point_in_polygon(site, sc.operation.zone)
    route = next(r for r in sc.roles if r.id == "site_recon").steps[0].do.params["route"]
    from shared.geo import dist_m

    nearest = min(dist_m(GeoPoint(**p), site) for p in route)
    assert 800 < nearest <= 2000  # outside the 800 m camera, inside the 2000 m RF receive


def test_assign_and_roles_and_operation_checks(sc):
    assert sc.id == "baengnyeong_assault" and sc.operation.id == "op_assault"
    assert sc.operation.assign == {
        "usv": "sea_patrol",
        "r1": "site_recon",
        "r2": "site_recon",
        "a1": "standby",
        "a2": "standby",
        "ugv": "watch_landing",
    }
    ids = {r.id for r in sc.roles}
    assert {
        "site_recon",
        "sea_patrol",
        "watch_landing",
        "strike",
        "standby",
        "go_home",
        "site_hold",
        "enemy_usv_run",
        "enemy_hold",
    } <= ids
    roles, specs = {r.id: r for r in sc.roles}, {v.id: v for v in sc.vehicles}
    assert check_operation(sc.operation, roles, specs).ok


def test_the_json_is_what_the_script_builds():
    from scripts.make_assault_scenario import build

    on_disk = json.loads(PATH.read_text(encoding="utf-8"))
    assert build() == on_disk
```

- [ ] **Step 2: 테스트가 실패하는지 확인한다**

Run: `uv run pytest tests/test_assault_scenario.py -x -n 0`
Expected: FAIL — 파일 `demo/scenarios/baengnyeong_assault.json`·모듈 `scripts.make_assault_scenario` 없음.

- [ ] **Step 3: 생성 스크립트를 쓴다**

`scripts/make_strike_scenario.py`의 구조를 따른다(야간 JSON을 읽고, `Scenario.model_validate`로 검증, `build()`가 dict를 돌려주고 `main()`이 디스크에 쓴다). 좌표는 초기값이며 Task 6에서 측정해 조정한다.

```python
"""Assault operation "해안 거점·무인장비 무력화" (virtual): demo/scenarios/baengnyeong_assault.json.
발표 라이브 시연의 유일한 작전(결정 0074). 1막: RF 거점(site_rf, unknown)을 직접 조종으로 보고 식별·타격.
2막: 적 무인 수상정(e_usv)이 상륙 지점으로 가며 지상 로봇 둘(e_ugv1/2)을 내리고, 우리 수상정의 발견 카드
'함께 타격'으로 공격 드론·수상정이 타격하고 지상 로봇이 상륙 지점을 관측(결정 0075·0078). 엔진 코드 변경 없음.
JSON이 그 뒤로 정본(결정 0035); 다시 만들 때만 실행. Usage: uv run python scripts/make_assault_scenario.py
"""

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT)]

from contracts.models import Scenario  # noqa: E402

NIGHT = ROOT / "demo" / "scenarios" / "baengnyeong_night.json"
OUT = ROOT / "demo" / "scenarios" / "baengnyeong_assault.json"
APPEAR_MS = 1000  # spawn_enemies needs t - dt < start + offset <= t; 0 never spawns

# virtual positions (initial; tuned in Task 6). USV spot is the sea west of the island (lon < 124.61),
# inside the zone. site_rf is inland, off the recon route, within 2 km RF but outside 800 m camera.
USV_SPOT = {"lat": 37.955, "lon": 124.600, "alt_m": 0.0}
SITE_RF = {"lat": 37.962, "lon": 124.640, "alt_m": 0.0}
UGV_SPOT = {"lat": 37.955, "lon": 124.720, "alt_m": 0.0}
# the recon route: along the west/north coast, staying >800 m from SITE_RF (so the drone must be sent there)
RECON_ROUTE = [
    {"lat": 37.980, "lon": 124.620, "alt_m": 0.0},
    {"lat": 37.980, "lon": 124.660, "alt_m": 0.0},
    {"lat": 37.975, "lon": 124.690, "alt_m": 0.0},
    {"lat": 37.980, "lon": 124.660, "alt_m": 0.0},
]
# our usv patrols a short west-coast line where it will meet the enemy usv's run
SEA_ROUTE = [
    {"lat": 37.945, "lon": 124.610, "alt_m": 0.0},
    {"lat": 37.935, "lon": 124.650, "alt_m": 0.0},
    {"lat": 37.945, "lon": 124.610, "alt_m": 0.0},
]
# the enemy usv runs from a coastal base to a landing point, then drops the ugvs there
E_USV_BASE = {"lat": 37.930, "lon": 124.690, "alt_m": 0.0}
E_LANDING = {"lat": 37.942, "lon": 124.660, "alt_m": 0.0}
E_USV_APPEAR = 240_000  # T+4:00 (tuned in Task 6)
E_UGV_APPEAR = 360_000  # T+6:00, when e_usv reaches the landing point (tuned)


def _role(rid, name, domains, steps, entry, **extra):
    base = {
        "id": rid,
        "name": name,
        "domains": domains,
        "steps": steps,
        "entry": entry,
        "origin": "human",
        "approved": True,
        "template": False,
    }
    return base | extra


def _step(sid, name, kind, params, on, report=None):
    return {
        "id": sid,
        "name": name,
        "do": {"kind": kind, "params": params},
        "on": on,
        "report": report,
        "ui": {},
    }


EMERGENCY = {
    "battery_low_pct": 30.0,
    "link_lost_step": None,
    "battery_low_step": None,
    "operator_call_step": None,
}


def site_recon():
    """1막 정찰 Role (r1·r2). 긴 흐름: 순찰 → 근접 확인 → 발견·보고(식별 줄·타격 카드는 GW-13) → 무력화 뒤."""
    patrol = _step(
        "patrol",
        "해안 순찰",
        "patrol_route",
        {"route": RECON_ROUTE, "route_name": "서·북 해안"},
        [{"cond": {"kind": "target_found", "params": {}}, "go_step": "approach"}],
    )
    approach = _step(
        "approach",
        "근접 확인",
        "approach_target",
        {"target": "nearest", "distance_m": 120},
        [{"cond": {"kind": "time_elapsed", "params": {"sec": 4}}, "go_step": "report"}],
    )
    report = _step(
        "report",
        "발견·감시·보고",
        "watch_target",
        {"target": "nearest", "distance_m": 150},
        [{"cond": {"kind": "target_neutralized", "params": {}}, "go_step": "after_strike"}],
        report={"text": "미식별 거점 감지", "choices": [], "auto_choices": True},
    )
    after = _step(
        "after_strike",
        "무력화 뒤",
        "hold",
        {},
        [{"cond": {"kind": "operator_choice", "params": {"choice": "more"}}, "go_step": "patrol"}],
        report={
            "text": "거점 무력화됨. 이어서 어떻게 할까요?",
            "choices": [
                {"id": "more", "label": "더 정찰", "role_by_vehicle": {}, "target_by_vehicle": {}},
                {
                    "id": "home",
                    "label": "수상정으로 복귀",
                    "role_by_vehicle": {"r1": "go_home", "r2": "go_home"},
                    "target_by_vehicle": {},
                },
            ],
            "auto_choices": False,
        },
    )
    return _role(
        "site_recon",
        "거점 탐색 순찰",
        ["air"],
        [patrol, approach, report, after],
        "patrol",
        emergency=EMERGENCY,
    )


def sea_patrol():
    """2막 해상 순찰 Role (usv). 발견 카드의 '함께 타격'이 공중·해상·지상을 한 번에 옮긴다(결정 0075)."""
    together = {
        "id": "strike_all_domains",
        "label": "함께 타격(공격 드론·수상정) · 지상 로봇 상륙 지점 관측",
        "role_by_vehicle": {
            "a1": "strike",
            "a2": "strike",
            "usv": "strike",
            "ugv": "watch_landing",
        },
        "target_by_vehicle": {"a1": "e_usv", "a2": "e_usv", "usv": "e_usv"},
    }
    watch_only = {
        "id": "watch_usv",
        "label": "수상정만 계속 감시",
        "role_by_vehicle": {},
        "target_by_vehicle": {},
    }
    patrol = _step(
        "patrol",
        "서쪽 항로 순찰",
        "patrol_route",
        {"route": SEA_ROUTE, "route_name": "서쪽 항로"},
        [{"cond": {"kind": "target_found", "params": {}}, "go_step": "report"}],
    )
    report = _step(
        "report",
        "발견·보고",
        "watch_target",
        {"target": "nearest", "distance_m": 200},
        [
            {
                "cond": {"kind": "operator_choice", "params": {"choice": "watch_usv"}},
                "go_step": "patrol",
            }
        ],
        report={
            "text": "미식별 수상정 접근",
            "choices": [together, watch_only],
            "auto_choices": False,
        },
    )
    return _role(
        "sea_patrol", "해상 순찰", ["sea"], [patrol, report], "patrol", emergency=EMERGENCY
    )


def watch_landing():
    """ugv가 상륙 지점을 지킨다(지점 감시만, 타격 능력 없음 = 온톨로지 장면)."""
    step = _step("watch", "상륙 지점 관측", "watch_point", {"point": E_LANDING}, [])
    return _role(
        "watch_landing", "상륙 지점 관측", ["ground"], [step], "watch", emergency=EMERGENCY
    )


def site_hold():
    step = _step("hold", "대기", "hold", {}, [])
    return _role("site_hold", "적: 거점 대기", ["ground"], [step], "hold", emergency=EMERGENCY)


def enemy_usv_run():
    """적 수상정: 기지에서 상륙 지점으로 간 뒤 멈춘다(결정 0032, sim이 검사 없이 움직임)."""
    go = _step(
        "go",
        "상륙 지점으로",
        "move_to",
        {"target": E_LANDING},
        [{"cond": {"kind": "arrived", "params": {}}, "go_step": "land"}],
    )
    land = _step("land", "하선 대기", "hold", {}, [])
    return _role("enemy_usv_run", "적: 상륙 침투", ["sea"], [go, land], "go", emergency=EMERGENCY)


def enemy_hold():
    step = _step("hold", "대기", "hold", {}, [])
    return _role("enemy_hold", "적: 지상 대기", ["ground"], [step], "hold", emergency=EMERGENCY)


def fleet(night_vehicles):
    by_id = {v["id"]: v for v in night_vehicles}
    usv = copy.deepcopy(by_id["usv"]) | {"id": "usv", "name": "무장 수상정", "home": dict(USV_SPOT)}
    recon = [
        copy.deepcopy(by_id["d1"])
        | {"id": f"r{i}", "name": f"정찰 드론{i}", "home": dict(USV_SPOT)}
        for i in (1, 2)
    ]
    armed = [
        copy.deepcopy(by_id["d2"])
        | {"id": f"a{i}", "name": f"공격 드론{i}", "home": dict(USV_SPOT)}
        for i in (1, 2)
    ]
    ugv = copy.deepcopy(by_id["ugv"]) | {"home": dict(UGV_SPOT)}
    return [usv, *recon, *armed, ugv]


def build():
    night = json.loads(NIGHT.read_text(encoding="utf-8"))
    nr = {r["id"]: r for r in night["roles"]}
    vehicles = fleet(night["vehicles"])
    op = night["operation"] | {
        "id": "op_assault",
        "name": "해안 거점·무인장비 무력화(가상)",
        "purpose": "정찰 드론이 RF 거점을 직접 조종으로 보고 식별·타격하고, 적 무인 수상정이 지상 로봇을 내리면 결정 한 번에 공격 드론·수상정이 타격하고 지상 로봇이 상륙 지점을 관측한다(가상 상황).",
        "vehicle_ids": [v["id"] for v in vehicles],
        "assign": {
            "usv": "sea_patrol",
            "r1": "site_recon",
            "r2": "site_recon",
            "a1": "standby",
            "a2": "standby",
            "ugv": "watch_landing",
        },
        "reserve": {},
        "switches": [],
        "rotation": [],
        "rotation_pools": {},
        "rotation_roles": [],
    }
    enemies = [
        {
            "id": "site_rf",
            "kind": "unknown",
            "speed_mps": 0.0,
            "appear_offset_ms": APPEAR_MS,
            "pos": dict(SITE_RF),
            "from_enemy": None,
            "role_id": "site_hold",
            "emit_start_offset_ms": 0,
        },
        {
            "id": "e_usv",
            "kind": "usv",
            "speed_mps": 6.0,
            "appear_offset_ms": E_USV_APPEAR,
            "pos": dict(E_USV_BASE),
            "from_enemy": None,
            "role_id": "enemy_usv_run",
            "emit_start_offset_ms": None,
        },
        {
            "id": "e_ugv1",
            "kind": "ugv",
            "speed_mps": 0.0,
            "appear_offset_ms": E_UGV_APPEAR,
            "pos": None,
            "from_enemy": "e_usv",
            "role_id": "enemy_hold",
            "emit_start_offset_ms": None,
        },
        {
            "id": "e_ugv2",
            "kind": "ugv",
            "speed_mps": 0.0,
            "appear_offset_ms": E_UGV_APPEAR + APPEAR_MS,
            "pos": None,
            "from_enemy": "e_usv",
            "role_id": "enemy_hold",
            "emit_start_offset_ms": None,
        },
    ]
    out = night | {
        "id": "baengnyeong_assault",
        "operation": op,
        "vehicles": vehicles,
        "roles": [
            site_recon(),
            sea_patrol(),
            watch_landing(),
            nr["standby"],
            nr["go_home"],
            nr["watch"],
            nr["approach"],
            nr["strike"],
            site_hold(),
            enemy_usv_run(),
            enemy_hold(),
        ],
        "events": [],  # Task 6 adds ScenarioEvent stops if needed; '다음 사건' stops live in cop-ui
        "enemies": enemies,
        "routes": [r for r in night["routes"] if r["id"] not in ("coast_a", "coast_b")],
        "watch_points": [
            {**night["watch_points"][0], "id": "target_area", "name": "목표 지역 중심"}
        ],
    }
    Scenario.model_validate(out)
    return out


def main():
    out = build()
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(
        f"{OUT.name}: {len(out['vehicles'])} vehicles, {len(out['enemies'])} enemies, "
        f"{len(out['roles'])} roles"
    )


if __name__ == "__main__":
    main()
```

주의(구현자):
- `EnemySpec.pos`가 `None`을 허용하는지 계약을 먼저 확인한다(`from_enemy`로 위치가 정해지는 적). 허용하지 않으면 `pos`에 `E_USV_BASE`를 넣어 두고 `from_enemy`로 덮이게 둔다(`spawn_enemies`가 `from_enemy`면 그 적의 현재 위치를 쓴다 — `modules/sim/actions/spawn_enemies.py` 확인).
- `watch_point` 행동의 params 키가 `point`인지 다른 이름인지 야간 작전 `landing` Role이나 계약에서 확인하고 맞춘다.
- `approach_target`가 `time_elapsed`로 다음 단계로 가는지, `approach` Role(야간)에 출구가 어떻게 달렸는지 확인한다. 안 맞으면 `approach` 단계를 빼고 `patrol → report`로 줄인다(테스트 `test_assault_scenario.py`의 Role id 집합은 유지).

- [ ] **Step 4: 스크립트를 실행해 JSON을 만든다**

Run: `uv run python scripts/make_assault_scenario.py`
Expected: `baengnyeong_assault.json: 6 vehicles, 4 enemies, 11 roles` 비슷한 출력, 파일 생성.

- [ ] **Step 5: 구조 테스트를 통과시킨다**

Run: `uv run pytest tests/test_assault_scenario.py -x -n 0`
Expected: PASS. 실패하면 좌표(SITE_RF가 섬 안·경로에서 800~2000 m)나 Role id를 고친다.

- [ ] **Step 6: 커밋**

```bash
git add scripts/make_assault_scenario.py demo/scenarios/baengnyeong_assault.json tests/test_assault_scenario.py
git commit -m "Part1-15.1: assault scenario JSON — 6-vehicle fleet, RF site, enemy usv+ugv (decisions 0074-0078)"
```

---

### Task 2: 1막 인수 테스트 (RF → 직접 조종 → 식별 → 승인 → 무력화)

**Files:**
- Modify: `tests/test_assault_scenario.py` (인수 테스트 추가)

**Interfaces:**
- Consumes: `modules.gateway.engine.init_engine`·`tick`, `contracts.models.TickInputs`·`Decision`·`DirectControl`·`GeoPoint`, Task 1의 `sc` fixture.
- Produces: 없음(테스트만).

- [ ] **Step 1: 실패하는 인수 테스트를 쓴다**

`DirectControl`로 직접 조종을 흉내 낸다(화면의 `POST /direct`와 같은 경로). r1을 거점 근처로 보내 센서에 들어오게 한 뒤, 식별됨→타격 카드→승인→무력화를 확인한다.

```python
from contracts.models import Decision, DirectControl, GeoPoint, TickInputs
from modules.gateway.engine import init_engine, tick


def _run_until(es, pred, limit=12000):
    for _ in range(limit):
        if pred(es):
            return es
        es, _ = tick(es, TickInputs())
    raise AssertionError("never happened")


def _site(es):
    return next(t for t in es.targets if t.id == "site_rf")


def _site_card(es):
    return next(
        (r for r in es.reports if r.kind == "target_detected" and r.target_id == "site_rf"), None
    )


def test_rf_clue_comes_before_the_drone_sees_the_site(sc):
    es = init_engine(sc)
    es = _run_until(es, lambda e: _site(e).ident_state == "rf_only")
    # heard on RF, not yet scanned: no detection card, nothing to strike
    assert _site_card(es) is None


def test_operator_direct_sends_a_recon_drone_to_the_off_route_site(sc):
    es = init_engine(sc)
    es = _run_until(es, lambda e: _site(e).ident_state == "rf_only")
    site = _site(es).pos
    dc = DirectControl(
        id="dir-1",
        vehicle_id="r1",
        t_ms=es.t_ms + sc.tick_ms,
        target=GeoPoint(lat=site.lat, lon=site.lon, alt_m=0.0),
    )
    es, _ = tick(es, TickInputs(direct=[dc]))
    assert not es.blocks  # the direct order is inside the zone and battery-feasible
    es = _run_until(es, lambda e: "r1" in _site(e).seen_by)  # r1 reaches camera range


def test_site_is_identified_then_approved_then_neutralized(sc):
    es = init_engine(sc)
    es = _run_until(es, lambda e: _site(e).ident_state == "rf_only")
    site = _site(es).pos
    dc = DirectControl(
        id="dir-1",
        vehicle_id="r1",
        t_ms=es.t_ms + sc.tick_ms,
        target=GeoPoint(lat=site.lat, lon=site.lon, alt_m=0.0),
    )
    es, _ = tick(es, TickInputs(direct=[dc]))
    es = _run_until(es, lambda e: _site(e).ident_state == "identified")
    card = _site_card(es)
    assert card is not None and "식별: 식별됨" in card.text
    strike_choices = [c for c in card.choices if c.id.startswith("strike_")]
    assert {"strike_a1", "strike_a2"} <= {c.id for c in strike_choices}  # armed drones offered
    dec = Decision(id="dec-1", t_ms=es.t_ms + sc.tick_ms, report_id=card.id, choice_id="strike_a1")
    es, _ = tick(es, TickInputs(decisions=[dec]))
    es = _run_until(es, lambda e: _site(e).neutralized_ms is not None, limit=15000)
    assert any(r.kind == "target_neutralized" and r.target_id == "site_rf" for r in es.reports)
    assert not es.blocks  # no safety rule (provenance, zone, battery) stopped the strike
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `uv run pytest tests/test_assault_scenario.py -k "rf_clue or direct or identified_then" -n 0`
Expected: FAIL. 흔한 실패와 조치:
- `ident_state`가 `rf_only`에 안 닿음 → SITE_RF가 RF 수신 2000 m 밖. Task 1의 SITE_RF를 r1 출발 경로 쪽으로 당긴다.
- 직접 조종이 `es.blocks`에 걸림 → 목표가 구역 밖이거나 귀환 배터리 부족. USV_SPOT에서 SITE_RF까지 왕복이 드론 지구력 안인지 본다.
- `identified`에 안 닿음 → r1 혼자 RF+스캔=65. `report` 단계 `watch_target` 거리를 늘려 관측을 유지시키거나 r2도 경로가 거점을 지나게 한다(관측 지속 또는 둘째 관측으로 70 돌파).

- [ ] **Step 3: 테스트가 통과하도록 좌표·시각을 조정한다**

`scripts/make_assault_scenario.py`의 좌표(SITE_RF·RECON_ROUTE·USV_SPOT)를 고치고 `uv run python scripts/make_assault_scenario.py`로 다시 만든 뒤 테스트를 돌린다. 코드는 바꾸지 않는다.

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_assault_scenario.py -n 0`
Expected: PASS (Task 1 테스트 포함 — JSON을 다시 만들었으므로 `test_the_json_is_what_the_script_builds`도 통과).

- [ ] **Step 5: 커밋**

```bash
git add tests/test_assault_scenario.py scripts/make_assault_scenario.py demo/scenarios/baengnyeong_assault.json
git commit -m "Part1-15.1: act 1 acceptance — RF clue, direct control, identified, approved, neutralized"
```

---

### Task 3: 2막 인수 테스트 (적 무인 장비, 결정 한 번에 공중·해상·지상)

**Files:**
- Modify: `tests/test_assault_scenario.py`

**Interfaces:**
- Consumes: Task 2의 헬퍼(`_run_until`), `init_engine`·`tick`·`TickInputs`·`Decision`.
- Produces: 없음(테스트만).

- [ ] **Step 1: 실패하는 인수 테스트를 쓴다**

```python
def _e_usv(es):
    return next((t for t in es.targets if t.id == "e_usv"), None)


def _sea_card(es):
    return next(
        (
            r
            for r in es.reports
            if r.kind == "target_detected" and r.target_id == "e_usv" and not r.resolved_ms
        ),
        None,
    )


def test_enemy_usv_spawns_and_drops_two_ground_robots(sc):
    es = init_engine(sc)
    es = _run_until(es, lambda e: _e_usv(e) is not None, limit=20000)
    es = _run_until(es, lambda e: {"e_ugv1", "e_ugv2"} <= {t.id for t in e.targets}, limit=20000)
    # the ground robots are dropped at the enemy usv's run, i.e. near the landing point
    ugv1 = next(t for t in es.targets if t.id == "e_ugv1")
    assert ugv1.kind.value == "ugv"


def test_one_decision_moves_air_sea_and_ground_and_neutralizes_the_enemy_usv(sc):
    es = init_engine(sc)
    es = _run_until(es, lambda e: _sea_card(e) is not None, limit=25000)
    card = _sea_card(es)
    assert any(c.id == "strike_all_domains" for c in card.choices)
    dec = Decision(
        id="dec-1", t_ms=es.t_ms + sc.tick_ms, report_id=card.id, choice_id="strike_all_domains"
    )
    es, _ = tick(es, TickInputs(decisions=[dec]))
    moved = {s.id: s.role_id for s in es.states}
    assert moved["a1"] == "strike" and moved["a2"] == "strike" and moved["usv"] == "strike"
    assert moved["ugv"] == "watch_landing"
    # the three strikers carry the operator decision id, so strike passes safety rule 1
    strikers = {s.id: s for s in es.states}
    for vid in ("a1", "a2", "usv"):
        assert strikers[vid].decision_id == "dec-1" and strikers[vid].target_id == "e_usv", vid
    es = _run_until(es, lambda e: _e_usv(e) and e_usv_down(e), limit=25000)
    assert not es.blocks  # no provenance/zone/battery block on the whole-domain strike


def e_usv_down(es):
    t = next((t for t in es.targets if t.id == "e_usv"), None)
    return t is not None and t.neutralized_ms is not None


def test_mission_success_when_the_enemy_usv_is_down(sc):
    es = init_engine(sc)
    es = _run_until(es, lambda e: _sea_card(e) is not None, limit=25000)
    card = _sea_card(es)
    dec = Decision(
        id="dec-1", t_ms=es.t_ms + sc.tick_ms, report_id=card.id, choice_id="strike_all_domains"
    )
    es, _ = tick(es, TickInputs(decisions=[dec]))
    es = _run_until(es, e_usv_down, limit=25000)
    assert es.metrics.mission_success  # a target was neutralized
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `uv run pytest tests/test_assault_scenario.py -k "enemy_usv or one_decision or mission_success" -n 0`
Expected: FAIL. 흔한 실패와 조치:
- 우리 usv가 적 usv를 발견 못 함(`_sea_card` None) → 적 usv 경로(E_USV_BASE→E_LANDING)가 우리 usv 순찰선(SEA_ROUTE)의 감시 거리(usv sensor 500 m) 안을 지나지 않음. 두 경로를 겹치게 당긴다. 또는 위협 누적이 4.5에 못 미쳐 `target_found`가 안 뜸 → 적 usv를 기준점(target_area) 반경 3배 안으로 지나게 하거나 접근 속도를 올린다(`score_target` 가산).
- 적 usv가 섬을 못 피해 멈춤 → E_USV_BASE·E_LANDING을 바다 점으로(섬 폴리곤 밖). `shared.land.inside`로 확인하는 보조 테스트를 Task 1에 넣어도 된다.
- `es.metrics.mission_success` 속성 이름이 다름 → `TickOutcome`/metrics 계약에서 확인해 맞춘다.
- `strike_all_domains` 선택지가 카드에 없음 → `sea_patrol` 보고 단계의 `auto_choices`가 `false`인지 본다(아래 주의).

주의(구현자, 확인함): `fleet_choices`(RT-11)는 보고 단계의 `report.auto_choices`가 참일 때만 선택지를 손대고, 거짓이면 카드를 그대로 돌려준다(`modules/runtime/actions/fleet_choices.py` 첫 조건). Task 1의 `sea_patrol`은 `auto_choices: False`라 `strike_all_domains`가 덮이지 않는다. 더구나 이 작전에는 교대 편성(`op.rotation`)도 멸공 전용 로직(`focus_orbit` Role)도 없어 take/join 덧붙임·알림 전환 경로가 동작하지 않는다. `refresh_strike_cards`(GW-13)도 `unknown`만 처리하므로 usv 종류 카드는 건드리지 않는다. 그래서 2막 타격은 코드 변경 없이 Role 데이터 선택지로 열린다.

- [ ] **Step 3: 통과하도록 좌표·속도·시각을 조정한다**

`scripts/make_assault_scenario.py`의 2막 좌표·`E_USV_APPEAR`·속도를 고치고 다시 만든다. 코드는 바꾸지 않는다.

- [ ] **Step 4: 통과 확인**

Run: `uv run pytest tests/test_assault_scenario.py -n 0`
Expected: PASS.

- [ ] **Step 5: 커밋**

```bash
git add tests/test_assault_scenario.py scripts/make_assault_scenario.py demo/scenarios/baengnyeong_assault.json
git commit -m "Part1-15.1: act 2 acceptance — enemy usv/ugv, one decision moves air/sea/ground, mission success"
```

---

### Task 4: 작전 고르기 목록에 등록

**Files:**
- Modify: `modules/gateway/app.py` (`DEMO_SCENARIOS`)
- Test: `modules/gateway/tests/test_app.py` 또는 `tests/test_demo_routes.py`(어느 파일이 `/scenarios` 목록을 검사하는지 확인해 그쪽에)

**Interfaces:**
- Consumes: `DEMO_SCENARIOS` 리스트, `GET /scenarios`.
- Produces: 작전 고르기 목록에 `baengnyeong_assault`가 뜬다.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

`/scenarios`를 검사하는 기존 테스트 파일을 찾아(예: `grep -rl "/scenarios" modules/gateway/tests tests`) 그 패턴에 맞춰 추가한다. 예:

```python
def test_assault_operation_is_in_the_pick_list(client):  # fixture name per the existing test file
    r = client.get("/scenarios")
    assert r.status_code == 200
    ids = [s["id"] for s in r.json()]
    assert "baengnyeong_assault" in ids
```

- [ ] **Step 2: 실패 확인**

Run: `uv run pytest modules/gateway/tests -k assault -n 0`
Expected: FAIL — 목록에 없음.

- [ ] **Step 3: DEMO_SCENARIOS에 한 줄 더한다**

```python
# modules/gateway/app.py, DEMO_SCENARIOS 리스트
DEMO_SCENARIOS = [
    DEFAULT_SCENARIO,
    str(ROOT / "demo/scenarios/baengnyeong_24h.json"),
    str(ROOT / "demo/scenarios/baengnyeong_strike.json"),
    str(ROOT / "demo/scenarios/baengnyeong_assault.json"),
]
```

- [ ] **Step 4: 통과 확인 + gateway 전체**

Run: `uv run pytest modules/gateway/tests -n 0`
Expected: PASS. 다른 테스트가 작전 개수를 세고 있으면 그 기대값을 3→4로 고친다.

- [ ] **Step 5: 커밋**

```bash
git add modules/gateway/app.py modules/gateway/tests
git commit -m "Part1-15.1: list baengnyeong_assault in the operation picker"
```

---

### Task 5: 화면 '다음 사건' 멈춤 시각 (cop-ui)

**Files:**
- Modify: `modules/cop-ui/src/features/run/runStops.ts` (ASSAULT_STOPS 추가)
- Modify: `modules/cop-ui/src/features/run/stopsFor.ts` (assault id 분기)
- Test: `modules/cop-ui/src/features/run/stopsFor.test.ts` (없으면 생성)

**Interfaces:**
- Consumes: `stopsFor(scenarioId)`, `RUN_STOPS`/`ASSAULT_STOPS`, `nextStop`.
- Produces: `stopsFor("baengnyeong_assault")`가 공격 작전 멈춤 배열을 돌려준다.

- [ ] **Step 1: 실패하는 vitest를 쓴다**

```typescript
// modules/cop-ui/src/features/run/stopsFor.test.ts
import { describe, expect, it } from "vitest";
import { stopsFor } from "./stopsFor";

describe("stopsFor", () => {
  it("night keeps its stops", () => {
    expect(stopsFor("baengnyeong_night").length).toBeGreaterThan(0);
  });
  it("assault has its own stops in ascending order", () => {
    const stops = stopsFor("baengnyeong_assault");
    expect(stops.length).toBeGreaterThan(0);
    for (let i = 1; i < stops.length; i++) {
      expect(stops[i].offsetMs).toBeGreaterThan(stops[i - 1].offsetMs);
    }
  });
  it("other operations have no stops", () => {
    expect(stopsFor("baengnyeong_24h")).toEqual([]);
  });
});
```

- [ ] **Step 2: 실패 확인**

Run: `cd modules/cop-ui && npx vitest run src/features/run/stopsFor.test.ts`
Expected: FAIL — assault가 빈 배열.

- [ ] **Step 3: ASSAULT_STOPS와 분기를 추가한다**

멈춤 시각은 Task 6에서 측정한 사건 시각에 맞춰 조정한다. 초기값(T+분):

```typescript
// runStops.ts 끝에 추가
export const ASSAULT_STOPS: RunStop[] = [
  { offsetMs: 1 * MIN, label: "RF 단서 (직접 조종)" },
  { offsetMs: 2 * MIN + 30_000, label: "거점 식별됨" },
  { offsetMs: 3 * MIN, label: "거점 무력화" },
  { offsetMs: 4 * MIN + 30_000, label: "적 수상정 접근" },
  { offsetMs: 5 * MIN + 30_000, label: "함께 타격" },
];
```

```typescript
// stopsFor.ts
import { ASSAULT_STOPS, RUN_STOPS, type RunStop } from "./runStops";

export function stopsFor(scenarioId: string | null): RunStop[] {
  if (scenarioId === "baengnyeong_night") return RUN_STOPS;
  if (scenarioId === "baengnyeong_assault") return ASSAULT_STOPS;
  return [];
}
```

- [ ] **Step 4: 통과 확인 + 타입 검사**

Run: `cd modules/cop-ui && npx vitest run src/features/run/stopsFor.test.ts && npx tsc --noEmit`
Expected: PASS, 타입 오류 없음.

- [ ] **Step 5: 커밋**

```bash
git add modules/cop-ui/src/features/run/runStops.ts modules/cop-ui/src/features/run/stopsFor.ts modules/cop-ui/src/features/run/stopsFor.test.ts
git commit -m "Part1-15.1: 다음 사건 stops for baengnyeong_assault"
```

---

### Task 6: 시각 튜닝, 발표 대본, 기록

**Files:**
- Modify: `scripts/make_assault_scenario.py` (측정값 반영), `demo/scenarios/baengnyeong_assault.json`(재생성)
- Modify: `modules/cop-ui/src/features/run/runStops.ts` (ASSAULT_STOPS를 측정 시각으로)
- Modify: `demo/RUNBOOK.md`, `demo/BUILT_HERE.md`
- Create: 발표 대본(기존 Part1-15 대본 위치에. 없으면 `demo/`에 `assault_script.md`)

**Interfaces:**
- Consumes: 실제 엔진(개발 서버 또는 인수 테스트), Task 5의 ASSAULT_STOPS.
- Produces: 배속 ×30에서 사건이 촘촘히 뜨고, '다음 사건' 멈춤 시각이 실제 장면과 맞는 시나리오. 발표 대본.

- [ ] **Step 1: 사건 시각을 측정한다**

인수 테스트에 각 사건 `t_ms`를 출력하는 보조를 넣거나(`print(es.t_ms - sc.operation.started_ms)`), 개발 서버(`scripts/dev.sh`)에서 작전을 골라 ×30으로 돌려본다. 측정: RF 단서(rf_only), 직접 조종 도착, 식별됨, 무력화, 적 usv 출현, 적 usv 발견 카드, 함께 타격 뒤 무력화. 전체가 약 6분 시뮬레이션 안인지 본다.

- [ ] **Step 2: 좌표·출현 시각을 조정해 압축한다**

흐르는 구간이 길면(사건 사이 2분 초과) USV_SPOT을 거점·순찰선에 당기거나 적 usv 속도·`E_USV_APPEAR`를 조정한다. 각 변경 뒤 `uv run python scripts/make_assault_scenario.py`로 재생성하고 `uv run pytest tests/test_assault_scenario.py -n 0`로 흐름이 안 깨졌는지 확인한다.

- [ ] **Step 3: ASSAULT_STOPS를 측정 시각으로 맞춘다**

측정한 사건 시각 + 약 5초로 `runStops.ts`의 ASSAULT_STOPS를 고치고 `npx vitest run src/features/run/stopsFor.test.ts`로 오름차순을 확인한다.

- [ ] **Step 4: 발표 대본과 기록을 쓴다**

설계 문서 7절 타임라인(A1~A3 편집기, B1~B7 실행)을 발표 대본으로 옮긴다. 각 멈춤에서 말할 한 줄과 배속 ×30·'다음 사건' 조작을 적는다. `demo/RUNBOOK.md`의 순서를 공격 작전으로 바꾸고(야간 3분 대본 대신), `demo/BUILT_HERE.md`에 한 줄 더한다:

```
| 10/11 | demo·gateway·cop-ui | Part1-15.1 발표 공격 작전 baengnyeong_assault(결정 0074~0078): 1막 RF 거점 직접 조종→식별→승인→타격, 2막 적 무인 수상정·지상로봇, 결정 한 번에 공중·해상·지상 타격. 데이터만, 엔진 코드 변경 없음. 작전 고르기·'다음 사건' 멈춤 추가 | kth9245 |
```

- [ ] **Step 5: 전체 테스트와 smoke, 커밋**

```bash
uv run pytest tests/test_assault_scenario.py modules/gateway/tests -n 0
cd modules/cop-ui && npx vitest run && npx tsc --noEmit && cd -
git add scripts/make_assault_scenario.py demo/scenarios/baengnyeong_assault.json modules/cop-ui/src/features/run/runStops.ts demo/RUNBOOK.md demo/BUILT_HERE.md demo/assault_script.md
git commit -m "Part1-15.1: tune assault timing, 다음 사건 stops, RUNBOOK and demo script"
```

---

## Self-Review

**Spec coverage:**
- 4절 아군 6대 → Task 1 `test_fleet_is_six_vehicles_air_sea_ground`. ✓
- 5절 적(RF 거점 unknown, 적 usv/ugv from_enemy) → Task 1 `test_enemies_*`. ✓
- 5.1절 두 막이 다른 기능(unknown 식별 카드 / usv·ugv Role 카드) → Task 2(식별 카드)·Task 3(Role 카드 + decision_id). ✓
- 6.1절 긴 정찰 Role → Task 1 `site_recon`(patrol→approach→report→after_strike). ✓
- 6.2절 해상 순찰 + 함께 타격 → Task 1 `sea_patrol`, Task 3. ✓
- 6.4절 AI 초안 캐시(zone·area = 야간) → Task 1 `test_zone_and_area_match_night_for_the_ai_draft_cache`. ✓
- 7절 타임라인·직접 조종 → Task 2(직접 조종), Task 6(대본·멈춤). ✓
- 8절 파일(새 JSON·DEMO_SCENARIOS·cop-ui 멈춤·RUNBOOK·BUILT_HERE) → Task 1·4·5·6. ✓
- 9절 남은 선택: 좌표·시각(Task 6), 기본 작전 여부(Task 4는 목록만 — 기본으로 두지 않음, 설계 9.2 기본값), A2 문장(기존 재사용 — Task 6 대본), ugv 함께 타격(Task 1·3이 포함). ✓

**Placeholder scan:** "구현 뒤 측정/조정"은 Task 6의 측정 루프로 구체화됨(초기 좌표·초기 멈춤 시각 제시). TBD 없음. ✓

**Type consistency:** `DirectControl`(id·vehicle_id·target·t_ms), `Decision`(id·t_ms·report_id·choice_id), `TickInputs`(decisions·direct·injections) — 계약과 일치(확인함). Role/선택지 키(`role_by_vehicle`·`target_by_vehicle`·`auto_choices`), 적 종류(`usv`·`ugv`), 기체 id(`r1·r2·a1·a2·usv·ugv`)가 Task 1~3·5에서 일관. `strike` Role domains = [air, sea]라 usv·a1·a2 모두 받음(확인함). ✓

**Review Focus:** usv/ugv에 자동 카드 없음(Task 3 Step 2 분기점으로 명시), 함께 타격 decision_id(Task 3 테스트), 직접·타격 목표 구역·배터리(Task 2·3 `not es.blocks`), 혼자 식별됨 도달(Task 2 identified), 캐시 키(Task 1 zone·area). 다섯 개 모두 소유 Task의 테스트로 고정됨. ✓

**열린 위험(실행 중 확인):** `EnemySpec.pos`의 None 허용, `watch_point` params 키, `approach_target` 출구, `metrics.mission_success` 이름 — 각 Task의 "주의(구현자)"에 확인 지점과 대체안을 적었다. `fleet_choices` 덮어쓰기 위험은 코드를 읽어 해소했다(auto_choices False면 카드 그대로, 이 작전은 rotation·focus_orbit 없음). 좌표·시각은 Task 6의 측정 루프로 맞춘다.
