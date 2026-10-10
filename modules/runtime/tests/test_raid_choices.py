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


def test_24h_card_is_an_alert_and_the_step_cards_ask():  # RT-19 asks one question at a time
    rep = run(base(), [SEA])
    assert rep.choices == [] and rep.resolved_ms == CARD.t_ms


def test_a_card_from_outside_a_patrol_is_an_alert_too():  # decision 0057 card in the 24h raid
    from modules.runtime.actions.raid_choices import raid_spot

    spot = CARD.model_copy(update={"vehicle_id": "usv"})
    rep = raid_spot(spot, base(), OPX, RAID, [SEA], LAND, SPECS)
    assert rep.choices == [] and rep.resolved_ms == spot.t_ms
    assert raid_spot(spot, base(), OPX, ROLES, [SEA], LAND, SPECS) == spot  # night: untouched


def test_a_drone_waiting_on_an_alert_card_is_released():  # user 10/11: never frozen while its enemy waits
    from modules.runtime.actions.raid_choices import release

    alert = run(base(), [SEA])
    states = [
        s.model_copy(update={"pending_report_id": CARD.id}) if s.id == "d1" else s for s in base()
    ]
    out = release(states, [alert], RAID)
    assert out[0].pending_report_id is None and out[1:] == states[1:]
    assert release(states, [alert], ROLES) == states  # night: untouched
    assert release(states, [CARD], RAID) == states  # an open card keeps its drone waiting
