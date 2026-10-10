"""24h raid card choices (decision 0055) through fleet_choices: on only when the roles have focus_orbit."""

from contracts.models import Action, GeoPoint, Polygon, Role, Step, Target, VehicleSpec
from modules.runtime.actions.fleet_choices import fleet_choices
from modules.runtime.tests.test_fleet_choices import CARD, HOME, OP, ROLES, vs
from shared.geo import offset_latlon


def _at(east_m: float, north_m: float) -> GeoPoint:
    lat, lon = offset_latlon(HOME.lat, HOME.lon, east_m, north_m)
    return GeoPoint(lat=lat, lon=lon)


LAND = [Polygon(points=[_at(-500, -500), _at(500, -500), _at(500, 500), _at(-500, 500)])]


def _role(pid: str, dom: str) -> Role:
    return Role(id=pid, name=pid, domains=[dom], entry="s", approved=True,
                steps=[Step(id="s", name="s", do=Action(kind="hold"))])  # fmt: skip


RAID = ROLES | {"focus_orbit": _role("focus_orbit", "air"), "track_sea": _role("track_sea", "sea"),
                "track_ground": _role("track_ground", "ground")}  # fmt: skip
OPX = OP.model_copy(update={"vehicle_ids": [*OP.vehicle_ids, "usv", "ugv"]})


def spec(vid: str, dom: str) -> VehicleSpec:
    return VehicleSpec(id=vid, name=vid, domain=dom, speed_mps=10, endurance_min=60, sensor_range_m=500,
                       home=HOME)  # fmt: skip


SPECS = {v: spec(v, "air") for v in ("d1", "d2", "d3", "d4")} | {
    "usv": spec("usv", "sea"),
    "ugv": spec("ugv", "ground"),
}


def tg(tid: str, kind: str, pos: GeoPoint, first: int, seen=("d1",), **kw) -> Target:
    return Target(id=tid, kind=kind, pos=pos, vel_east_mps=0, vel_north_mps=0, first_seen_ms=first,
                  last_seen_ms=first, seen_by=list(seen), **kw)  # fmt: skip


def run(states, targets, roles=RAID):
    return fleet_choices(CARD, states, OPX, roles, targets, LAND, SPECS)


def ids(rep) -> list[str]:
    return [c.id for c in rep.choices]


def base(*extra):
    return [vs("d1", "coast_a", "report", target="boat1"), vs("d2", "coast_b", "patrol"),
            vs("d3", None, None, "ready"), vs("d4", None, None, "ready", battery=40),
            vs("usv", None, None, "ready"), vs("ugv", None, None, "ready"), *extra]  # fmt: skip


SEA = tg("boat1", "usv", _at(0, -2000), 10)


def test_without_targets_choices_are_unchanged():
    states = base()
    assert ids(fleet_choices(CARD, states, OPX, RAID)) == ids(
        fleet_choices(CARD, states, OPX, ROLES)
    )
    assert (
        ids(fleet_choices(CARD, states, OPX, ROLES, [SEA], LAND, SPECS))[-1] == "keep"
    )  # night: no focus_orbit


def test_other_drones_get_relief_and_focus_choices():
    rep = run(base(), [SEA])
    labels = [c.label for c in rep.choices]
    assert "d3 → 이탈 지역 순찰(해안 순찰 A · 북)" in labels
    assert "d3 → 적기 1 발견 지점 집중 순찰" in labels and labels[-1] == "대기"
    focus = next(c for c in rep.choices if c.id == "focus_d3_boat1")
    assert focus.role_by_vehicle == {"d3": "focus_orbit"} and focus.target_by_vehicle == {
        "d3": "boat1"
    }
    assert not any(c.id.startswith(("join_", "keep")) for c in rep.choices)


def test_a_focused_target_gets_no_more_focus_choices():
    d2 = vs("d2", "focus_orbit", "s", target="boat1")
    rep = run([s for s in base() if s.id != "d2"] + [d2], [SEA])
    assert not any(c.id.startswith("focus_") for c in rep.choices)


def test_usv_tracks_sea_and_ugv_tracks_ground_only():
    d2 = vs("d2", "coast_b", "report", target="e_ugv1")
    d3 = vs("d3", "coast_a", "report", target="e_drone")
    states = [s for s in base() if s.id not in ("d2", "d3")] + [d2, d3]
    targets = [
        SEA,
        tg("e_ugv1", "ugv", _at(100, 100), 20, ("d2",)),
        tg("e_drone", "drone", _at(0, 0), 30, ("d3",)),
    ]
    labels = [c.label for c in run(states, targets).choices]
    assert "usv → 적기 1 추적(해상)" in labels and "ugv → 적기 2 추적(지상)" in labels
    assert not [x for x in labels if "적기 3 추적" in x]
    assert not [x for x in labels if x.startswith("usv → 적기 2") or x.startswith("ugv → 적기 1")]
    track = next(c for c in run(states, targets).choices if c.id == "track_usv_boat1")
    assert track.role_by_vehicle == {"usv": "track_sea"} and track.target_by_vehicle == {
        "usv": "boat1"
    }


def test_unseen_and_neutralized_targets_get_no_number():
    targets = [
        tg("ghost", "usv", _at(0, -3000), 1, ()),
        tg("dead", "usv", _at(0, -3000), 2, neutralized_ms=5),
        SEA,
    ]
    labels = [c.label for c in run(base(), targets).choices]
    assert "usv → 적기 1 추적(해상)" in labels and not [x for x in labels if "적기 2" in x]


def test_a_ugv_still_at_sea_gets_no_usv_track():  # just landed from the enemy usv: a ugv never needs chasing at sea
    d2 = vs("d2", "coast_b", "report", target="e_ugv1")
    states = [s for s in base() if s.id != "d2"] + [d2]
    labels = [
        c.label for c in run(states, [tg("e_ugv1", "ugv", _at(0, -2000), 20, ("d2",))]).choices
    ]
    assert not [x for x in labels if x.startswith("usv →")]
