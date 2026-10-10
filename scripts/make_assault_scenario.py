"""Assault operation "해안 거점·무인장비 무력화" (virtual): demo/scenarios/baengnyeong_assault.json.
발표 라이브 시연의 유일한 작전(결정 0074). 1막: RF 거점(site_rf, unknown)을 직접 조종으로 보고 식별·타격.
2막: 적 무인 수상정(e_usv)이 상륙 지점으로 가며 지상 로봇 둘(e_ugv1/2)을 내리고, 우리 수상정의 발견 카드
'함께 타격'으로 공격 드론·수상정이 타격하고 지상 로봇이 상륙 지점으로 이동해 관측한다(결정 0075·0078). 엔진 코드 변경 없음.
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
SITE_RF = {"lat": 37.969, "lon": 124.655, "alt_m": 0.0}
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

EMERGENCY = {"battery_low_pct": 30.0, "link_lost_step": None,
             "battery_low_step": None, "operator_call_step": None}  # fmt: skip


def _role(rid, name, domains, steps, entry, **extra):
    base = {"id": rid, "name": name, "domains": domains, "steps": steps, "entry": entry,
            "origin": "human", "approved": True, "template": False}  # fmt: skip
    return base | extra


def _step(sid, name, kind, params, on, report=None):
    return {"id": sid, "name": name, "do": {"kind": kind, "params": params},
            "on": on, "report": report, "ui": {}}  # fmt: skip


def site_recon():
    """1막 정찰 Role (r1·r2). 순찰 → 발견·보고(식별 줄·타격 카드는 GW-13) → 무력화 뒤.
    approach 단계는 두지 않는다(condition_true가 time_elapsed를 처리하지 않아 멈춘다, 진행 기록 Ruling)."""
    patrol = _step("patrol", "해안 순찰", "patrol_route",
                   {"route": RECON_ROUTE, "route_name": "서·북 해안"},
                   [{"cond": {"kind": "target_found", "params": {}}, "go_step": "report"}])  # fmt: skip
    report = _step("report", "발견·감시·보고", "watch_target", {"target": "nearest", "distance_m": 150},
                   [{"cond": {"kind": "operator_choice", "params": {"choice": "resume"}}, "go_step": "patrol"},
                    {"cond": {"kind": "target_neutralized", "params": {}}, "go_step": "after_strike"}],
                   report={"text": "미식별 거점 감지",
                           "choices": [{"id": "resume", "label": "이 거점은 두고 계속 정찰",
                                        "role_by_vehicle": {}, "target_by_vehicle": {}}],
                           "auto_choices": True})  # fmt: skip
    after = _step("after_strike", "무력화 뒤", "hold", {},
                  [{"cond": {"kind": "operator_choice", "params": {"choice": "more"}}, "go_step": "patrol"}],
                  report={"text": "거점 무력화됨. 이어서 어떻게 할까요?",
                          "choices": [{"id": "more", "label": "더 정찰", "role_by_vehicle": {}, "target_by_vehicle": {}},
                                      {"id": "home", "label": "수상정으로 복귀",
                                       "role_by_vehicle": {"r1": "go_home", "r2": "go_home"}, "target_by_vehicle": {}}],
                          "auto_choices": False})  # fmt: skip
    return _role(
        "site_recon",
        "거점 탐색 순찰",
        ["air"],
        [patrol, report, after],
        "patrol",
        emergency=EMERGENCY,
    )


def sea_patrol():
    """2막 해상 순찰 Role (usv). 발견 카드의 '함께 타격'이 공중·해상·지상을 한 번에 옮긴다(결정 0075).
    auto_choices False라 fleet_choices가 선택지를 덮지 않는다(진행 기록 확인)."""
    together = {"id": "strike_all_domains", "label": "함께 타격(공격 드론·수상정) · 지상 로봇 상륙 지점으로",
                "role_by_vehicle": {"a1": "strike", "a2": "strike", "usv": "strike", "ugv": "watch_landing"},
                "target_by_vehicle": {"a1": "e_usv", "a2": "e_usv", "usv": "e_usv"}}  # fmt: skip
    watch_only = {"id": "watch_usv", "label": "수상정만 계속 감시",
                  "role_by_vehicle": {}, "target_by_vehicle": {}}  # fmt: skip
    patrol = _step("patrol", "서쪽 항로 순찰", "patrol_route", {"route": SEA_ROUTE, "route_name": "서쪽 항로"},
                   [{"cond": {"kind": "target_found", "params": {}}, "go_step": "report"}])  # fmt: skip
    report = _step("report", "발견·보고", "watch_target", {"target": "nearest", "distance_m": 200},
                   [{"cond": {"kind": "operator_choice", "params": {"choice": "watch_usv"}}, "go_step": "patrol"}],
                   report={"text": "미식별 수상정 접근", "choices": [together, watch_only], "auto_choices": False})  # fmt: skip
    return _role(
        "sea_patrol", "해상 순찰", ["sea"], [patrol, report], "patrol", emergency=EMERGENCY
    )


def watch_landing():
    """ugv가 상륙 지점으로 이동해 관측한다(move_to, 진행 기록 Ruling: watch_point 미검증)."""
    step = _step("move", "상륙 지점으로", "move_to", {"target": E_LANDING}, [])
    return _role("watch_landing", "상륙 지점 관측", ["ground"], [step], "move", emergency=EMERGENCY)


def site_hold():
    step = _step("hold", "대기", "hold", {}, [])
    return _role("site_hold", "적: 거점 대기", ["ground"], [step], "hold", emergency=EMERGENCY)


def enemy_usv_run():
    """적 수상정: 기지에서 상륙 지점으로 간 뒤 멈춘다(결정 0032, sim이 검사 없이 움직임)."""
    go = _step("go", "상륙 지점으로", "move_to", {"target": E_LANDING},
               [{"cond": {"kind": "arrived", "params": {}}, "go_step": "land"}])  # fmt: skip
    land = _step("land", "하선 대기", "hold", {}, [])
    return _role("enemy_usv_run", "적: 상륙 침투", ["sea"], [go, land], "go", emergency=EMERGENCY)


def enemy_hold():
    step = _step("hold", "대기", "hold", {}, [])
    return _role("enemy_hold", "적: 지상 대기", ["ground"], [step], "hold", emergency=EMERGENCY)


def fleet(night_vehicles):
    by_id = {v["id"]: v for v in night_vehicles}
    usv = copy.deepcopy(by_id["usv"]) | {"id": "usv", "name": "무장 수상정", "home": dict(USV_SPOT)}
    recon = [copy.deepcopy(by_id["d1"]) | {"id": f"r{i}", "name": f"정찰 드론{i}", "home": dict(USV_SPOT)}
             for i in (1, 2)]  # fmt: skip
    armed = [copy.deepcopy(by_id["d2"]) | {"id": f"a{i}", "name": f"공격 드론{i}", "home": dict(USV_SPOT)}
             for i in (1, 2)]  # fmt: skip
    ugv = copy.deepcopy(by_id["ugv"]) | {"home": dict(UGV_SPOT)}
    return [usv, *recon, *armed, ugv]


def build():
    night = json.loads(NIGHT.read_text(encoding="utf-8"))
    nr = {r["id"]: r for r in night["roles"]}
    vehicles = fleet(night["vehicles"])
    op = night["operation"] | {
        "id": "op_assault", "name": "해안 거점·무인장비 무력화",
        "purpose": "정찰 드론이 RF 거점을 직접 조종으로 보고 식별·타격하고, 적 무인 수상정이 지상 로봇을 내리면 결정 한 번에 공격 드론·수상정이 타격하고 지상 로봇이 상륙 지점으로 이동해 관측한다(가상 상황).",
        "vehicle_ids": [v["id"] for v in vehicles],
        "assign": {"usv": "sea_patrol", "r1": "site_recon", "r2": "site_recon",
                   "a1": "standby", "a2": "standby", "ugv": "standby"},  # ugv idle until the B6 decision
        "reserve": {}, "switches": [], "rotation": [], "rotation_pools": {}, "rotation_roles": [],
    }  # fmt: skip
    enemies = [
        {"id": "site_rf", "kind": "unknown", "speed_mps": 0.0, "appear_offset_ms": APPEAR_MS,
         "pos": dict(SITE_RF), "from_enemy": None, "role_id": "site_hold", "emit_start_offset_ms": 0},
        {"id": "e_usv", "kind": "usv", "speed_mps": 6.0, "appear_offset_ms": E_USV_APPEAR,
         "pos": dict(E_USV_BASE), "from_enemy": None, "role_id": "enemy_usv_run", "emit_start_offset_ms": None},
        {"id": "e_ugv1", "kind": "ugv", "speed_mps": 0.0, "appear_offset_ms": E_UGV_APPEAR,
         "pos": None, "from_enemy": "e_usv", "role_id": "enemy_hold", "emit_start_offset_ms": None},
        {"id": "e_ugv2", "kind": "ugv", "speed_mps": 0.0, "appear_offset_ms": E_UGV_APPEAR + APPEAR_MS,
         "pos": None, "from_enemy": "e_usv", "role_id": "enemy_hold", "emit_start_offset_ms": None},
    ]  # fmt: skip
    out = night | {
        "id": "baengnyeong_assault", "operation": op, "vehicles": vehicles,
        "roles": [site_recon(), sea_patrol(), watch_landing(), nr["standby"], nr["go_home"],
                  nr["watch"], nr["approach"], nr["strike"], site_hold(), enemy_usv_run(), enemy_hold()],
        "events": [],
        "enemies": enemies,
        "routes": [r for r in night["routes"] if r["id"] not in ("coast_a", "coast_b")],
        "watch_points": [{**night["watch_points"][0], "id": "target_area", "name": "목표 지역 중심"}],
    }  # fmt: skip
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
