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
# decision 0069: virtual infrared on the scouts, virtual hearing on the ground robot, a heat and a noise site
IR_RANGE_M, ACOUSTIC_RANGE_M = 800.0, 500.0
# the ground robot waits on land 1500 m south of site_c, outside its 500 m ears: the operator sends it there
UGV_START = {"lat": 37.95923, "lon": 124.64615, "alt_m": 0.0}
SIGNATURES = {"site_b": {"heat": True}, "site_c": {"noise": True}}
# the carrier USV waits in the sea west of the island (outside the land, inside the zone)
USV_SPOT = {"lat": 37.955, "lon": 124.585, "alt_m": 0.0}
# The three coast stretches, one recon drone each. Points are indices into the 24h operation's coast routes,
# listed clockwise (seen from above); counter-clockwise is the same list reversed. The operator picks the
# direction per drone before the start by assigning its clockwise or counter-clockwise Role.
STRETCHES = {
    "ne": (
        "r1",
        "북동 해안",
        "coast_a",
        [0, 1, 2, 3, 4, 5, 6],
    ),  # centre of the north coast -> east tip
    "nw": ("r2", "북서 해안", "coast_a", [20, 19, 18, 17, 16, 15, 14, 13, 0]),  # west tip -> centre
    # east tip -> west tip along the whole south coast, one way: a full lap would leave a scout under 30% on return
    "s": ("r3", "남쪽 해안", "coast_b", list(range(25, 10, -1))),
}
DIRECTIONS = {"cw": "시계방향", "ccw": "반시계방향"}
# before the start each scout flies one of its two directions (the others are picked in the start assignment)
DEFAULT_DIRECTION = {"r1": "cw", "r2": "ccw", "r3": "ccw"}
RECON = {d: f"site_patrol_{k}_{DEFAULT_DIRECTION[d]}" for k, (d, *_) in STRETCHES.items()}
# the clockwise north-east patrol first flies over the sea north of the island: the straight line from the USV spot
# to the centre of the north coast would pass right over site_c, which belongs to the north-west patrol
SEA_LEG = {"site_ne_cw": [{"lat": 37.996, "lon": 124.620, "alt_m": 0.0}]}


def site_hold() -> dict:
    step = {
        "id": "hold",
        "name": "대기",
        "do": {"kind": "hold", "params": {}},
        "on": [],
        "report": None,
        "ui": {},
    }
    return {"id": "site_hold", "name": "적: 거점 대기", "domains": ["ground"], "steps": [step],
            "entry": "hold", "origin": "human", "approved": True, "template": False,
            "emergency": {"battery_low_pct": 30.0, "link_lost_step": None, "battery_low_step": None,
                          "operator_call_step": None}}  # fmt: skip


def fleet(night_vehicles: list[dict]) -> list[dict]:
    """One stationary carrier USV, three recon and three attack drones that start and return at its spot."""
    by_id = {v["id"]: v for v in night_vehicles}
    usv = copy.deepcopy(by_id["usv"]) | {"name": "수상정(모선)", "kind": "sea_vehicle",
                                         "home": dict(USV_SPOT)}  # fmt: skip

    def drone(src: str, vid: str, name: str) -> dict:
        return copy.deepcopy(by_id[src]) | {"id": vid, "name": name, "home": dict(usv["home"])}

    recon = [drone("d1", f"r{i}", f"정찰 드론{i}") | {"ir_range_m": IR_RANGE_M} for i in (1, 2, 3)]
    armed = [drone("d2", f"a{i}", f"공격 드론{i}") for i in (1, 2, 3)]
    ugv = copy.deepcopy(by_id["ugv"]) | {
        "acoustic_range_m": ACOUSTIC_RANGE_M,
        "home": dict(UGV_START),
    }
    return [usv, *recon, *armed, ugv]


def after_strike(drone: str) -> dict:
    """The scout waits here for the operator: scout more (continue its stretch) or go back to the USV."""
    more = {"id": "more", "label": "더 정찰", "role_by_vehicle": {}, "target_by_vehicle": {}}
    home = {"id": "home", "label": "수상정으로 복귀", "role_by_vehicle": {drone: "go_home"},
            "target_by_vehicle": {}}  # fmt: skip
    return {
        "id": "after_strike", "name": "무력화 뒤", "do": {"kind": "hold", "params": {}},
        "on": [{"cond": {"kind": "operator_choice", "params": {"choice": "more"}}, "go_step": "patrol"}],
        "report": {"text": "거점 무력화됨. 이어서 어떻게 할까요?", "choices": [more, home],
                   "auto_choices": False},
        "ui": {},
    }  # fmt: skip


def assist() -> dict:
    """A scout that meets a site another scout already reported stops and watches it too (decision 0070)."""
    stay = {"id": "stay", "label": "계속 관측", "role_by_vehicle": {}, "target_by_vehicle": {}}
    back = {
        "id": "back",
        "label": "각자 순찰로 복귀",
        "role_by_vehicle": {},
        "target_by_vehicle": {},
    }
    return {
        "id": "assist", "name": "함께 관측",
        "do": {"kind": "watch_target", "params": {"target": "operator", "distance_m": 150}},
        "on": [
            {"cond": {"kind": "operator_choice", "params": {"choice": "back"}}, "go_step": "patrol"},
            {"cond": {"kind": "target_neutralized", "params": {}}, "go_step": "after_strike"},
        ],
        "report": {"text": "이미 보고된 거점 재탐지", "choices": [stay, back], "auto_choices": False},
        "ui": {},
    }  # fmt: skip


def coast_patrols(day: dict) -> tuple[list[dict], list[dict]]:
    """A search Role and an editor route per coast stretch and direction, cut from the 24h coast routes."""
    base_role = next(r for r in day["roles"] if r["id"] == "coast_a")
    routes_by_id = {r["id"]: r for r in day["routes"]}
    roles, routes = [], []
    for key, (drone, name, src, idx) in STRETCHES.items():
        for direction, dir_name in DIRECTIONS.items():
            order = idx if direction == "cw" else idx[::-1]
            route_id, role_id = f"site_{key}_{direction}", f"site_patrol_{key}_{direction}"
            label = f"{name} {dir_name}"
            pts = [routes_by_id[src]["points"][i] for i in order]
            points = SEA_LEG.get(route_id, []) + copy.deepcopy(pts)
            routes.append(
                copy.deepcopy(routes_by_id[src]) | {"id": route_id, "name": label, "points": points}
            )
            role = copy.deepcopy(base_role)
            role["id"], role["name"] = role_id, f"거점 탐색 순찰 · {label}"
            role["steps"][0]["do"]["params"] = {"route": points, "route_name": label}
            # the drone that raises this card may leave the site: back to its own stretch, or to another one
            # (the same way round), where it takes the other stretch's Role
            leave = [{"id": "resume", "label": "이 거점은 두고 계속 정찰", "role_by_vehicle": {},
                      "target_by_vehicle": {}}]  # fmt: skip
            leave += [
                {"id": f"go_site_{k}", "label": f"{nm} 쪽으로 이동해 정찰",
                 "role_by_vehicle": {drone: f"site_patrol_{k}_{direction}"}, "target_by_vehicle": {}}
                for k, (_, nm, _, _) in STRETCHES.items()
                if k != key
            ]  # fmt: skip
            role["steps"][1]["report"] = {
                "text": "미식별 거점 감지",
                "choices": leave,
                "auto_choices": True,
            }
            role["steps"][1]["on"] = [
                {
                    "cond": {"kind": "operator_choice", "params": {"choice": "resume"}},
                    "go_step": "patrol",
                },
                # decision 0066: once the site is struck the scout asks what next instead of hovering forever
                {"cond": {"kind": "target_neutralized", "params": {}}, "go_step": "after_strike"},
            ]  # decision 0031: the reporter not named in role_by_vehicle takes the operator_choice exit
            role["steps"][0][
                "on"
            ].append(  # decision 0070: after target_found (a new site comes first)
                {"cond": {"kind": "target_resighted", "params": {}}, "go_step": "assist"}
            )
            role["steps"] += [assist(), after_strike(drone)]
            roles.append(role)
    return roles, routes


def build() -> dict:
    night = json.loads(NIGHT.read_text(encoding="utf-8"))
    day = json.loads(DAY.read_text(encoding="utf-8"))
    roles = {r["id"]: r for r in night["roles"]}
    patrols, patrol_routes = coast_patrols(day)
    skip = ("patrol_a", "patrol_b", "coast_a", "coast_b")
    vehicles = fleet(night["vehicles"])
    op = night["operation"] | {
        "id": "op_strike",
        "name": "해안 거점 무력화",
        "purpose": "정찰 드론이 가상 해안 거점을 RF 방출로 먼저 찾고 스캔해서 식별한다. 식별된 거점에만 타격 승인을 연다(2단계). 서쪽 앞바다의 수상정 한 척에서 정찰 드론 3대(북동·북서·남쪽 해안)와 공격 드론 3대가 출발한다",
        "vehicle_ids": [v["id"] for v in vehicles],
        "assign": {v["id"]: RECON.get(v["id"], "standby") for v in vehicles},
        "reserve": {}, "switches": [], "rotation": [], "rotation_pools": {}, "rotation_roles": [],
    }  # fmt: skip
    enemies = [
        {"id": i, "kind": "unknown", "speed_mps": 0.0, "appear_offset_ms": APPEAR_MS,
         "pos": {"lat": lat, "lon": lon, "alt_m": 0.0}, "from_enemy": None, "role_id": "site_hold",
         "emit_start_offset_ms": emit} | SIGNATURES.get(i, {})
        for i, lat, lon, emit in SITES
    ]  # fmt: skip
    out = night | {
        "id": "baengnyeong_strike",
        "operation": op,
        "vehicles": vehicles,
        "roles": [*patrols, roles["standby"], roles["go_home"], roles["watch"], roles["approach"],
                  roles["strike"], site_hold()],
        "events": [],
        "enemies": enemies,
        "routes": [*patrol_routes, *(r for r in night["routes"] if r["id"] not in skip)],
        # same place and radius as night's "상륙 예상 지점" (so the scores below hold), but here it is the
        # target area the sites are measured against, not a place to guard
        "watch_points": [{**night["watch_points"][0], "id": "target_area", "name": "목표 지역 중심"}],
    }  # fmt: skip
    Scenario.model_validate(out)
    return out


def main() -> None:
    out = build()
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(
        f"{OUT.name}: {len(out['enemies'])} sites, {len(out['roles'])} roles, {len(out['routes'])} routes"
    )


if __name__ == "__main__":
    main()
