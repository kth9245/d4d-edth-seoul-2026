"""Coast patrol routes (decision 0037) and the 24h rotation scenario demo/scenarios/baengnyeong_24h.json.

The island outline (Scenario.land, decision 0034) is pushed 400 m out to sea, thinned to about 900 m
between points and split at its west and east ends into the north coast (A) and the south coast (B).
Each route runs end to end and back, so follow_route's wrap to the first point never crosses the island.
The JSON is the source afterwards (decision 0035); rerun only to rebuild the routes.
The editor's route list (decision 0044) comes from the night scenario's `routes`, with the coast routes
replaced by the ones built here, and the coast cards carry their route names.
The night `ontology` comes along and every drone is an `armed_drone` (user, 10/10), so the loader fills
their capabilities (strike_target included) and the editor's ontology view works here too (decision 0051).
Usage: uv run python scripts/make_coast_routes.py
"""

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT)]

from contracts.models import GeoPoint, Scenario  # noqa: E402
from shared.geo import dist_m, enu_delta_m, offset_latlon  # noqa: E402

NIGHT = ROOT / "demo" / "scenarios" / "baengnyeong_night.json"
OUT = ROOT / "demo" / "scenarios" / "baengnyeong_24h.json"
OFFSHORE_M, SPACING_M = 400, 900


def coast_routes(land, home: GeoPoint) -> tuple[list[dict], list[dict]]:
    pts = land[0].points
    c = GeoPoint(lat=sum(p.lat for p in pts) / len(pts), lon=sum(p.lon for p in pts) / len(pts))

    def out(p: GeoPoint) -> GeoPoint:
        e, n = enu_delta_m(c.lat, c.lon, p.lat, p.lon)
        k = math.hypot(e, n)
        lat, lon = offset_latlon(p.lat, p.lon, e / k * OFFSHORE_M, n / k * OFFSHORE_M)
        return GeoPoint(lat=lat, lon=lon)

    ring = [out(p) for p in pts]
    w = min(range(len(ring)), key=lambda i: ring[i].lon)
    e = max(range(len(ring)), key=lambda i: ring[i].lon)

    def walk(a: int, b: int) -> list[GeoPoint]:
        seq, i = [ring[a]], a
        while i != b:
            i = (i + 1) % len(ring)
            seq.append(ring[i])
        return seq

    def thin(seq: list[GeoPoint]) -> list[dict]:
        keep = [seq[0]]
        for p in seq[1:-1]:
            if dist_m(keep[-1], p) >= SPACING_M:
                keep.append(p)
        keep.append(seq[-1])
        there = [{"lat": round(p.lat, 5), "lon": round(p.lon, 5), "alt_m": 0} for p in keep]
        loop = there + there[-2:0:-1]  # end to end and back
        # start at the coast point nearest the base, so a drone reaches its coast in minutes
        k = min(range(len(there)), key=lambda i: dist_m(home, GeoPoint(**there[i])))
        return loop[k:] + loop[:k]

    one, two = walk(w, e), walk(e, w)
    mean = lambda s: sum(p.lat for p in s) / len(s)  # noqa: E731
    north, south = (one, two) if mean(one) > mean(two) else (two, one)
    return thin(north), thin(south)


COAST_NAMES = {"coast_a": "해안 A(북)", "coast_b": "해안 B(남)"}  # route names (decision 0044)


# the night cards' usv/ugv choices (patrol_a 근접 확인, patrol_b 수상정 인계), on both coasts (user, 10/10);
# the spotting drone keeps watching (근접 확인) or goes back to its patrol (수상정 인계)
USV_UGV_CHOICES = [
    {
        "id": "approach",
        "label": "근접 확인",
        "role_by_vehicle": {"usv": "approach", "ugv": "landing"},
    },
    {"id": "handoff", "label": "수상정 인계", "role_by_vehicle": {"usv": "approach"}},
]
USV_UGV_ROLES = (
    "approach",
    "landing",
    "track_fast_sea",
    "strike",
)  # copied from the night operation as they are


def patrol(pid: str, name: str, route: list[dict]) -> dict:
    params = {"route": route, "route_name": COAST_NAMES[pid]}
    step = {"id": "patrol", "name": "해안 순찰", "do": {"kind": "patrol_route", "params": params},
            "on": [{"cond": {"kind": "target_found", "params": {}}, "go_step": "report"}],
            "report": None, "ui": {}}  # fmt: skip
    found = {"id": "report", "name": "발견·감시·보고",
             "do": {"kind": "watch_target", "params": {"target": "nearest", "distance_m": 150}},
             "on": [{"cond": {"kind": "operator_choice", "params": {"choice": "handoff"}}, "go_step": "patrol"}],
             "report": {"text": "미식별 선박 접근", "choices": USV_UGV_CHOICES, "auto_choices": True},
             "ui": {}}  # fmt: skip
    return {"id": pid, "name": name, "domains": ["air"], "steps": [step, found], "entry": "patrol",
            "origin": "human", "approved": True, "template": False}  # fmt: skip


def build() -> dict:
    night = json.loads(NIGHT.read_text(encoding="utf-8"))
    sc = Scenario.model_validate(night)
    a, b = coast_routes(sc.land, sc.vehicles[0].home)
    base = sc.vehicles[
        0
    ].home  # pads: a 600 m square (user: a quarter of 2.4 km) around the night base, d1 NW d2 NE d3 SW d4 SE (user, 10/10)
    pads = {"d1": (-300, 300), "d2": (300, 300), "d3": (-300, -300), "d4": (300, -300)}
    home = {}
    for k, (e, n) in pads.items():
        lat, lon = offset_latlon(base.lat, base.lon, e, n)
        home[k] = {"lat": round(lat, 7), "lon": round(lon, 7), "alt_m": 0.0}
    drones = [
        v
        | {
            "recharge_min": 5,
            "home": home[v["id"]],
            "kind": "armed_drone",
        }  # all armed (user, 10/10)
        for v in night["vehicles"]
        if v["domain"] == "air"
    ]
    ground_sea = [
        v for v in night["vehicles"] if v["domain"] != "air"
    ]  # usv, ugv at their night spots (user, 10/10)
    roles = {p["id"]: p for p in night["roles"]}
    op = night["operation"] | {
        "name": "멸공",
        "purpose": "드론 4대가 북(A: d1·d3)·남(B: d2·d4) 해안을 짝끼리 교대로 늘 1대씩 순찰(결정 0037, 0041)",
        "vehicle_ids": [v["id"] for v in drones + ground_sea],
        "assign": {
            "d1": "coast_a",
            "d2": "coast_b",
            "d3": "standby",
            "d4": "standby",
            "usv": "standby",
            "ugv": "standby",
        },
        "reserve": {},
        "switches": [
            *(sw for sw in night["operation"]["switches"] if sw["id"] == "all_home"),  # user, 10/10
            {
                "id": "track_fast",
                "label": "고속 보트 추적",
                "role_by_vehicle": {"usv": "track_fast_sea"},
            },
        ],  # track_fast: usv only, d2 stays on its coast
        "rotation": ["d1", "d2", "d3", "d4"],
        "rotation_pools": {"coast_a": ["d1", "d3"], "coast_b": ["d2", "d4"]},
        "rotation_roles": ["coast_a", "coast_b"],
    }
    out = {
        "id": "baengnyeong_24h",
        "operation": op,
        "vehicles": drones + ground_sea,
        "roles": [
            patrol("coast_a", "해안 순찰 A · 북", a),
            patrol("coast_b", "해안 순찰 B · 남", b),
            roles["standby"],
            roles["go_home"],
            roles["watch"],
            *(roles[r] for r in USV_UGV_ROLES),
        ],  # fmt: skip
        "events": [],
        "enemies": [],
        "routes": [
            {"id": "coast_a", "name": COAST_NAMES["coast_a"], "points": a},
            {"id": "coast_b", "name": COAST_NAMES["coast_b"], "points": b},
            *(
                r
                for r in night["routes"]
                if r["id"] not in ("patrol_a", "patrol_b", "coast_a", "coast_b")
            ),
        ],  # decision 0044: the night list without the night-only patrols
        "land": night["land"],
        "ontology": night["ontology"],  # decision 0051: same drones, same kinds
        "seed": 0,
        "tick_ms": 200,
        "speed": 1.0,
    }
    Scenario.model_validate(out)
    return out


def main() -> None:
    out = build()
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    coast = {r["id"]: len(r.get("points", [])) for r in out["routes"]}
    print(f"{OUT.name}: coast_a {coast['coast_a']} points, coast_b {coast['coast_b']} points")


if __name__ == "__main__":
    main()
