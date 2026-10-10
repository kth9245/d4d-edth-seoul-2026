import pytest

from contracts.models import (
    Command,
    CommandKind,
    GeoPoint,
    PassedCommand,
    VehicleSpec,
    VehicleState,
    VehicleStatus,
)
from modules.sim.actions.follow_route import follow_route
from shared.geo import dist_m, offset_latlon

HOME = GeoPoint(lat=37.95, lon=124.70)
SPEC = VehicleSpec(id="d1", name="d1", domain="air", speed_mps=10, endurance_min=40,
                   sensor_range_m=800, capabilities=["patrol_route"], home=HOME)  # fmt: skip


def _at(east_m: float = 0, north_m: float = 0) -> GeoPoint:
    lat, lon = offset_latlon(HOME.lat, HOME.lon, east_m, north_m)
    return GeoPoint(lat=lat, lon=lon)


A, B = _at(north_m=500), _at(east_m=500, north_m=500)
ROUTE = PassedCommand(
    command=Command(
        id="c1",
        vehicle_id="d1",
        kind=CommandKind.follow_route,
        params={"route": [A.model_dump(), B.model_dump()]},
    ),  # fmt: skip
    checks=[],
    passed_ms=0,
)


def _state(pos: GeoPoint, idx: int) -> VehicleState:
    return VehicleState(id="d1", t_ms=0, pos=pos, heading_deg=0, battery_pct=100,
                        status=VehicleStatus.active, waypoint_idx=idx)  # fmt: skip


def test_moves_toward_the_current_waypoint():
    st = follow_route(_state(HOME, 0), SPEC, ROUTE, 1000)
    assert dist_m(HOME, st.pos) == pytest.approx(10, abs=0.1)
    assert dist_m(st.pos, A) == pytest.approx(490, abs=0.5)
    assert st.waypoint_idx == 0


def test_reaching_a_waypoint_advances_to_the_next_one():
    st = follow_route(_state(_at(north_m=495), 0), SPEC, ROUTE, 1000)
    assert dist_m(st.pos, A) < 1
    assert st.waypoint_idx == 1


def test_after_the_last_waypoint_it_goes_back_to_the_first():
    at_b = follow_route(_state(_at(east_m=495, north_m=500), 1), SPEC, ROUTE, 1000)
    assert at_b.waypoint_idx == 2  # past the end
    nxt = follow_route(at_b, SPEC, ROUTE, 1000)
    assert dist_m(nxt.pos, A) < dist_m(at_b.pos, A)  # heading to the first waypoint again
