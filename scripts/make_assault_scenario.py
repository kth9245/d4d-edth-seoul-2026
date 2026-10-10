"""Assault operation "해안 거점·무인장비 무력화" (virtual): demo/scenarios/baengnyeong_assault.json.
발표 라이브 시연의 유일한 작전(결정 0074), 흐름은 결정 0080. 정찰 드론 r1·r2가 편대로 서쪽 해변 위를 한 번 지나고
(해변 안전은 발표자가 말로), 발표자가 수상정을 직접 조종으로 해변에 상륙시킨다(지상 로봇은 처음부터 육지에).
편대가 끝나면 r1은 북쪽, r2는 남쪽 거점을 찾아 그 위에서 감시하며 버튼 없는 알림을 올리고, 발표자가 공격 드론
a1·a2를 기체 메뉴 '표적 타격'으로 보낸다(결정 0058). 북쪽이 무력화되면 r1이 이어서 숲속 거점을 찾고 a1이 두 번째로 친다.
엔진 코드 변경 없음. JSON이 그 뒤로 정본(결정 0035); 다시 만들 때만 실행.
Usage: uv run python scripts/make_assault_scenario.py
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


def _p(lat, lon):
    return {"lat": lat, "lon": lon, "alt_m": 0.0}


# virtual positions, all inside the zone. Drones and the usv wait in the sea west of the island; the ground robot
# is already ashore behind the west beach. The three sites are inland (north, south, forest in the middle).
HOME = _p(37.955, 124.592)
USV_HOME = _p(37.950, 124.588)
UGV_HOME = _p(37.957, 124.630)
SITES = [("site_n", 37.972, 124.655), ("site_s", 37.932, 124.655), ("site_f", 37.952, 124.690)]
# the formation: r1 and r2 fly the west beach side by side, about 450 m apart, once (move_to along a route, 0045)
FORMATION = {
    "r1": [_p(37.957, 124.600), _p(37.957, 124.615), _p(37.957, 124.630)],
    "r2": [_p(37.953, 124.600), _p(37.953, 124.615), _p(37.953, 124.630)],
}
# each search leg passes within the 800 m camera of its site and far from the others
SEARCH = {
    "search_n": [_p(37.967, 124.640), _p(37.975, 124.652)],
    "search_s": [_p(37.943, 124.640), _p(37.934, 124.652)],
    "search_f": [_p(37.965, 124.672), _p(37.955, 124.688)],
}
# the objective area: every site lies within three radii (near step +0.15), so a silent site scores 0.45 and
# the finder's card goes up (decision 0043)
TARGET_AREA = {"id": "target_area", "name": "목표 지역 중심", "pos": _p(37.955, 124.665), "radius_m": 2000.0}
ATTACK_SPEED_MPS = 30.0  # virtual: the attack drones cross 6 km from the sea home in about 3 minutes

EMERGENCY = {"battery_low_pct": 30.0, "link_lost_step": None,
             "battery_low_step": None, "operator_call_step": None}  # fmt: skip


def _role(rid, name, domains, steps, entry):
    return {"id": rid, "name": name, "domains": domains, "steps": steps, "entry": entry,
            "origin": "human", "approved": True, "template": False, "emergency": EMERGENCY}  # fmt: skip


def _step(sid, name, kind, params, on, report=None):
    return {"id": sid, "name": name, "do": {"kind": kind, "params": params},
            "on": on, "report": report, "ui": {}}  # fmt: skip


def _go(cond, step):
    return {"cond": {"kind": cond, "params": {}}, "go_step": step}


def _search(sid, name, area):
    return _step(sid, name, "patrol_route", {"route": SEARCH[sid], "route_name": area},
                 [_go("target_found", sid.replace("search", "watch"))])  # fmt: skip


def _watch(sid, name, after):
    """Hover over the site the drone found and keep it seen (so the vehicle menu can point a strike at it).
    The card is a plain alert: no choices, the drone does not wait on it, the strike goes through the menu."""
    alert = {"text": "거점 발견", "choices": [], "auto_choices": False}
    return _step(sid, name, "watch_target", {"target": "nearest", "distance_m": 150},
                 [_go("target_neutralized", after)], report=alert)  # fmt: skip


def recon(vid, legs):
    """Formation over the beach, then the search legs one after another, then home."""
    form = _step("formation", "편대 · 서쪽 해변", "move_to",
                 {"route": FORMATION[vid], "route_name": "편대 · 서쪽 해변"},
                 [_go("arrived", legs[0][0])])  # fmt: skip
    steps = [form]
    for i, (search_id, area) in enumerate(legs):
        watch_id = search_id.replace("search", "watch")
        after = legs[i + 1][0] if i + 1 < len(legs) else "home"
        steps += [_search(search_id, f"거점 탐색 · {area}", area), _watch(watch_id, f"감시 · {area}", after)]
    steps.append(_step("home", "귀환", "return_home", {}, []))
    return _role(f"recon_{vid}", f"정찰 · {vid}", ["air"], steps, "formation")


def point_strike(night_strike):
    """The night 'strike' Role under another id. With no role named "strike" the engine never puts strike buttons
    on the site cards (GW-13 refresh_strike_cards), which would otherwise appear once two drones see a site and
    stay on the card after the site is down; the vehicle menu still offers it, by its strike_target step."""
    return copy.deepcopy(night_strike) | {"id": "point_strike"}


def site_hold():
    return _role("site_hold", "적: 거점 대기", ["ground"], [_step("hold", "대기", "hold", {}, [])], "hold")


def fleet(night_vehicles):
    by_id = {v["id"]: v for v in night_vehicles}
    usv = copy.deepcopy(by_id["usv"]) | {"id": "usv", "name": "수상정", "kind": "sea_vehicle",
                                         "home": dict(USV_HOME)}  # fmt: skip
    recon_ = [copy.deepcopy(by_id["d1"]) | {"id": f"r{i}", "name": f"정찰 드론{i}", "home": dict(HOME)}
              for i in (1, 2)]  # fmt: skip
    armed = [copy.deepcopy(by_id["d2"]) | {"id": f"a{i}", "name": f"공격 드론{i}", "home": dict(HOME),
                                           "speed_mps": ATTACK_SPEED_MPS} for i in (1, 2)]  # fmt: skip
    ugv = copy.deepcopy(by_id["ugv"]) | {"home": dict(UGV_HOME)}
    return [usv, *recon_, *armed, ugv]


def build():
    night = json.loads(NIGHT.read_text(encoding="utf-8"))
    nr = {r["id"]: r for r in night["roles"]}
    vehicles = fleet(night["vehicles"])
    op = night["operation"] | {
        "id": "op_assault", "name": "해안 거점·무인장비 무력화",
        "purpose": "정찰 드론 편대가 서쪽 해변을 지나고 수상정이 해변에 상륙한다. 정찰 드론이 북쪽·남쪽·숲속 거점을 차례로 찾고, 운용자가 공격 드론 2대를 표적 타격으로 보내 거점 3곳을 파괴한다(가상 상황).",
        "vehicle_ids": [v["id"] for v in vehicles],
        "assign": {"usv": "standby", "r1": "recon_r1", "r2": "recon_r2",
                   "a1": "standby", "a2": "standby", "ugv": "standby"},
        "reserve": {}, "switches": [], "rotation": [], "rotation_pools": {}, "rotation_roles": [],
    }  # fmt: skip
    enemies = [{"id": i, "kind": "unknown", "speed_mps": 0.0, "appear_offset_ms": APPEAR_MS,
                "pos": _p(lat, lon), "from_enemy": None, "role_id": "site_hold", "emit_start_offset_ms": None}
               for i, lat, lon in SITES]  # fmt: skip
    roles = [recon("r1", [("search_n", "북쪽"), ("search_f", "숲속")]), recon("r2", [("search_s", "남쪽")]),
             nr["standby"], nr["go_home"], nr["watch"], nr["approach"], point_strike(nr["strike"]), site_hold()]  # fmt: skip
    out = night | {
        "id": "baengnyeong_assault", "operation": op, "vehicles": vehicles, "roles": roles,
        "events": [], "enemies": enemies,
        "routes": [r for r in night["routes"] if r["id"] not in ("coast_a", "coast_b")],
        "watch_points": [TARGET_AREA],
    }  # fmt: skip
    Scenario.model_validate(out)
    return out


def main():
    out = build()
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{OUT.name}: {len(out['vehicles'])} vehicles, {len(out['enemies'])} sites, {len(out['roles'])} roles")


if __name__ == "__main__":
    main()
