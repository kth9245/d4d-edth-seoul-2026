import pytest

from contracts.models import (
    Command,
    CommandKind,
    GeoPoint,
    PassedCommand,
    Polygon,
    Target,
    VehicleSpec,
    VehicleState,
    VehicleStatus,
)
from modules.sim.actions.orbit_or_keep import orbit_or_keep
from shared.geo import dist_m, offset_latlon
from shared.land import inside

HOME = GeoPoint(lat=37.95, lon=124.70)
SPEC = VehicleSpec(id="d1", name="d1", domain="air", speed_mps=10, endurance_min=40,
                   sensor_range_m=800, capabilities=["watch_target"], home=HOME)  # fmt: skip
BOAT = Target(id="boat1", kind="boat", pos=HOME, vel_east_mps=0, vel_north_mps=0,
              first_seen_ms=0, last_seen_ms=0)  # fmt: skip
R = 150


def _at(east_m: float = 0, north_m: float = 0) -> GeoPoint:
    lat, lon = offset_latlon(HOME.lat, HOME.lon, east_m, north_m)
    return GeoPoint(lat=lat, lon=lon)


def _state(pos: GeoPoint) -> VehicleState:
    return VehicleState(id="d1", t_ms=0, pos=pos, heading_deg=0, battery_pct=100,
                        status=VehicleStatus.active)  # fmt: skip


def _passed(kind: CommandKind) -> PassedCommand:
    cmd = Command(id="c1", vehicle_id="d1", kind=kind,
                  params={"target_id": "boat1", "distance_m": R})  # fmt: skip
    return PassedCommand(command=cmd, checks=[], passed_ms=0)


def test_orbit_keeps_the_radius_and_moves_along_the_circle():
    start = _at(north_m=R)
    st = orbit_or_keep(_state(start), SPEC, _passed(CommandKind.orbit), [BOAT], 1000)
    assert dist_m(st.pos, BOAT.pos) == pytest.approx(R, abs=1)
    assert dist_m(st.pos, start) > 5  # it actually moved


def test_orbit_flies_toward_a_far_target_instead_of_jumping_onto_the_circle():
    start = _at(north_m=2000)
    st = orbit_or_keep(_state(start), SPEC, _passed(CommandKind.orbit), [BOAT], 1000)
    assert dist_m(start, st.pos) == pytest.approx(10, abs=0.1)
    assert dist_m(st.pos, BOAT.pos) == pytest.approx(1990, abs=0.5)


def test_keep_distance_approaches_but_stops_at_the_distance():
    far = orbit_or_keep(_state(_at(north_m=1000)), SPEC, _passed(CommandKind.keep_distance),
                        [BOAT], 1000)  # fmt: skip
    assert dist_m(far.pos, BOAT.pos) == pytest.approx(990, abs=0.5)
    near = orbit_or_keep(_state(_at(north_m=R + 5)), SPEC, _passed(CommandKind.keep_distance),
                         [BOAT], 1000)  # fmt: skip
    assert dist_m(near.pos, BOAT.pos) == pytest.approx(R, abs=0.5)


def test_keep_distance_inside_the_distance_stays_put():
    start = _at(north_m=R - 50)
    st = orbit_or_keep(_state(start), SPEC, _passed(CommandKind.keep_distance), [BOAT], 1000)
    assert dist_m(st.pos, start) < 0.01


ISLAND = [Polygon(points=[_at(-500, -500), _at(500, -500), _at(500, 500), _at(-500, 500)])]


def test_sea_keep_distance_goes_round_the_island_first():
    boat = BOAT.model_copy(update={"pos": _at(1000, -200)})
    pc = PassedCommand(command=Command(id="c3", vehicle_id="d1", kind=CommandKind.keep_distance,
                                       params={"target_id": "boat1", "distance_m": 200}),
                       checks=[], passed_ms=0)  # fmt: skip
    st = _state(_at(-1000, -200))
    for _ in range(400):
        st = orbit_or_keep(st, SPEC, pc, [boat], 1000, ISLAND)
        assert not inside(st.pos, ISLAND)
    assert dist_m(st.pos, boat.pos) == pytest.approx(200, abs=1)
