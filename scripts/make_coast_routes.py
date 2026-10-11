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
from shared.land import inside, to_sea  # noqa: E402

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
             "on": [],
             "report": {"text": "미식별 선박 접근", "choices": [], "auto_choices": True},
             "ui": {}}  # fmt: skip
    return {"id": pid, "name": name, "domains": ["air"], "steps": [step, found], "entry": "patrol",
            "origin": "human", "approved": True, "template": False}  # fmt: skip


def _pt(p: GeoPoint) -> dict:
    return {"lat": round(p.lat, 6), "lon": round(p.lon, 6), "alt_m": 0.0}


def _off(p: GeoPoint, east_m: float, north_m: float) -> GeoPoint:
    lat, lon = offset_latlon(p.lat, p.lon, east_m, north_m)
    return GeoPoint(lat=lat, lon=lon)


def _step(sid: str, name: str, target: dict, then: str) -> dict:
    return {"id": sid, "name": name, "do": {"kind": "move_to", "params": {"target": target}},
            "on": [{"cond": {"kind": "arrived", "params": {}}, "go_step": then}], "report": None, "ui": {}}  # fmt: skip


def _go(
    eid: str, name: str, dom: str, target: dict, via: dict | None = None
) -> dict:  # (via a point,) go, hold
    wait = {
        "id": "wait",
        "name": "대기",
        "do": {"kind": "hold", "params": {}},
        "on": [],
        "report": None,
        "ui": {},
    }
    steps = [_step("go", name, target, "wait"), wait]
    steps = [_step("cross", "해안 경계선 통과", via, "go"), *steps] if via else steps
    return {"id": f"enemy_{eid}", "name": f"적: {name}", "domains": [dom], "steps": steps, "entry": steps[0]["id"],
            "origin": "human", "approved": True, "template": False}  # fmt: skip


EMERGENCY = {
    "battery_low_pct": 30.0,
    "link_lost_step": None,
    "battery_low_step": None,
    "operator_call_step": None,
}  # as every night role: home at 30% (user 10/11)


def _ours(rid: str, name: str, dom: str, do: dict) -> dict:
    step = {"id": "s", "name": name, "do": do, "on": [], "report": None, "ui": {}}
    return {"id": rid, "name": name, "domains": [dom], "steps": [step], "entry": "s", "origin": "human",
            "approved": True, "template": False, "emergency": EMERGENCY}  # fmt: skip


def _on_land(a: GeoPoint, b: GeoPoint, land) -> bool:  # a straight leg that never leaves the island
    n = max(
        1, int(dist_m(a, b) // 20)
    )  # every 20 m: 11 samples let a long leg cut 90 m out over a bay (user 10/11)
    return all(inside(GeoPoint(lat=a.lat + (b.lat - a.lat) * k / n, lon=a.lon + (b.lon - a.lon) * k / n), land)
               for k in range(n + 1))  # fmt: skip


def scout_route(land, landing: GeoPoint) -> list[dict]:
    """Enemy ugv2: the island outline 200 m inland, clockwise from the landing (user, 10/10). Points are kept up to
    about 900 m apart only while the straight leg stays on land, so it never cuts across a bay."""
    pts = land[0].points
    c = GeoPoint(lat=sum(p.lat for p in pts) / len(pts), lon=sum(p.lon for p in pts) / len(pts))
    ring = []
    for p in pts:
        e, n = enu_delta_m(p.lat, p.lon, c.lat, c.lon)
        k = math.hypot(e, n) or 1.0
        q = _off(p, e / k * 200, n / k * 200)
        if inside(q, land):
            ring.append(q)
    area = sum(
        a.lon * b.lat - b.lon * a.lat for a, b in zip(ring, ring[1:] + ring[:1], strict=True)
    )
    ring = ring[::-1] if area > 0 else ring  # shoelace > 0 is counter-clockwise
    k = min(range(len(ring)), key=lambda i: dist_m(ring[i], landing))
    ring = ring[k:] + ring[:k]

    def ok(
        i: int, j: int
    ) -> bool:  # on land, and not a pocket of the outline no straight leg leaves (user 10/11)
        return _on_land(ring[i], ring[j], land) and (
            j == len(ring) - 1
            or any(_on_land(ring[j], ring[m], land) for m in range(j + 1, len(ring)))
        )

    keep, i = [ring[0]], 0
    while i < len(ring) - 1:
        j = next((j for j in range(i + 1, len(ring)) if ok(i, j)), i + 1)
        while j + 1 < len(ring) and dist_m(ring[i], ring[j + 1]) <= SPACING_M and ok(i, j + 1):
            j += 1  # skip points a straight leg cannot reach, then go up to 900 m along the outline
        i = j
        keep.append(ring[i])
    while len(keep) > 2 and not _on_land(keep[-1], keep[0], land):
        keep.pop()  # the loop closes on land
    return [_pt(p) for p in keep]


CROSS_MS = 17 * 60_000  # the raiders cross the coast patrol at T+17:00 (user 10/10, plan A)
LEAD_S = (CROSS_MS - 660_000) / 1000  # from appearing at T+11:00


def _outward(c: GeoPoint, p: GeoPoint, m: float) -> GeoPoint:  # m metres further from c, through p
    e, n = enu_delta_m(c.lat, c.lon, p.lat, p.lon)
    k = math.hypot(e, n) or 1.0
    return _off(p, e / k * m, n / k * m)


def patrol_spots(out: dict) -> dict[str, GeoPoint]:
    """Where the active coast_a / coast_b patrol drones are at T+17:00 with no enemies (the tick loop is deterministic)."""
    from contracts.models import TickInputs
    from modules.gateway.engine import init_engine, tick
    from modules.ontology import fill_vehicle_kinds

    sc = fill_vehicle_kinds(Scenario.model_validate(out | {"enemies": []}))
    es, f = init_engine(sc), None
    while es.t_ms < sc.operation.started_ms + CROSS_MS:
        es, f = tick(es, TickInputs())
    return {
        v.role_id: v.pos
        for v in f.vehicles
        if v.role_id in ("coast_a", "coast_b") and v.status.value == "active"
    }


def raid(
    land, base: GeoPoint, spots: dict[str, GeoPoint] | None = None
) -> tuple[list[dict], list[dict]]:
    """The 24h two-pronged raid (decision 0055): a suicide drone from the north at T+11:00 to the drone base,
    an enemy usv from the south at T+11:00 that stops at the coast, and its two ugvs at T+23:00 (one to the
    base, one scouting the coast clockwise). Returns (enemies, enemy roles + our response roles)."""
    pts = land[0].points
    c = GeoPoint(lat=sum(p.lat for p in pts) / len(pts), lon=sum(p.lon for p in pts) / len(pts))
    spots = spots or {
        "coast_a": max(pts, key=lambda p: p.lat),
        "coast_b": min(pts, key=lambda p: p.lat),
    }
    cross_a, cross_b = (
        spots["coast_a"],
        spots["coast_b"],
    )  # where each coast's patrol drone is at T+17:00
    shore = min(pts, key=lambda p: dist_m(p, cross_b))
    landing = to_sea(
        _outward(c, shore, -100), land
    )  # from 100 m inland: on the outline to_sea has no way out
    drone0 = _outward(
        base, cross_a, 8.0 * LEAD_S
    )  # straight in from the north, over the patrol at T+17:00
    usv0 = _outward(c, cross_b, 5.0 * LEAD_S)
    enemies = [
        {"id": "e_drone", "kind": "drone", "speed_mps": 8.0, "appear_offset_ms": 660_000, "pos": _pt(drone0), "role_id": "enemy_e_drone"},
        {"id": "e_usv", "kind": "usv", "speed_mps": 5.0, "appear_offset_ms": 660_000, "pos": _pt(usv0), "role_id": "enemy_e_usv"},
        {"id": "e_ugv1", "kind": "ugv", "speed_mps": 3.0, "appear_offset_ms": 1_380_000, "from_enemy": "e_usv", "role_id": "enemy_e_ugv1"},
        {"id": "e_ugv2", "kind": "ugv", "speed_mps": 3.0, "appear_offset_ms": 1_380_000, "from_enemy": "e_usv", "role_id": "enemy_e_ugv2"},
    ]  # fmt: skip
    scout = _go("e_ugv2", "해안선 시계 방향 정찰", "ground", _pt(landing))
    scout["steps"] = [{"id": "go", "name": "해안선 시계 방향 정찰", "on": [], "report": None, "ui": {},
                       "do": {"kind": "patrol_route", "params": {"route": scout_route(land, landing)}}}]  # fmt: skip
    circle = [{"east_m": round(800 * math.sin(i * math.pi / 6), 1), "north_m": round(800 * math.cos(i * math.pi / 6), 1)}
              for i in range(12)]  # fmt: skip
    watch = {"kind": "watch_target", "params": {"target": "operator", "distance_m": 200}}
    roles = [
        _go("e_drone", "드론 기지로 자폭 돌진", "air", _pt(base), _pt(cross_a)),
        _go("e_usv", "남쪽 해안 상륙", "sea", _pt(landing), _pt(cross_b)),
        _go("e_ugv1", "드론 기지로", "ground", _pt(base)),
        scout,
        _ours("focus_orbit", "발견 지점 집중 순찰", "air", {"kind": "patrol_route", "params": {
            "offsets": circle, "anchor": "target", "route_name": FOCUS_ROUTE}}),
        _ours("track_sea", "적기 추적(해상)", "sea", watch),
        _ours("track_ground", "적기 추적(지상)", "ground", watch),
    ]  # fmt: skip
    return enemies, roles


FOCUS_ROUTE = "발견 지점 집중 순찰(800 m)"


def build(spots: dict[str, GeoPoint] | None = None) -> dict:
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
    enemies, raid_roles = raid(sc.land, base, spots)
    ontology = json.loads(
        json.dumps(night["ontology"])
    )  # 24h only: ground robots can track (decision 0055)
    next(k for k in ontology["kinds"] if k["id"] == "ground_robot")["provides"].append(
        "watch_target"
    )
    op = night["operation"] | {
        "name": "24시간 침투 대응",
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
        # only the all-vehicle return (user, 10/10); tracking is pointed from the vehicle menu (decision 0060)
        "switches": [sw for sw in night["operation"]["switches"] if sw["id"] == "all_home"],
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
            *raid_roles,
        ],  # fmt: skip
        "events": [],
        "enemies": enemies,
        "routes": [
            {"id": "coast_a", "name": COAST_NAMES["coast_a"], "points": a},
            {"id": "coast_b", "name": COAST_NAMES["coast_b"], "points": b},
            {
                "id": "focus_800",
                "name": FOCUS_ROUTE,
                "offsets": next(r for r in raid_roles if r["id"] == "focus_orbit")["steps"][0][
                    "do"
                ]["params"]["offsets"],
            },
            *(
                r
                for r in night["routes"]
                if r["id"] not in ("patrol_a", "patrol_b", "coast_a", "coast_b")
            ),
        ],  # decision 0044: the night list without the night-only patrols
        "land": night["land"],
        "ontology": ontology,  # decision 0051: same drones, same kinds
        "seed": 0,
        "tick_ms": 200,
        "speed": 1.0,
    }
    Scenario.model_validate(out)
    return out if spots else build(patrol_spots(out))  # second pass aims the raiders at the patrols


def main() -> None:
    out = build()
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    coast = {r["id"]: len(r.get("points", [])) for r in out["routes"]}
    print(f"{OUT.name}: coast_a {coast['coast_a']} points, coast_b {coast['coast_b']} points")


if __name__ == "__main__":
    main()
