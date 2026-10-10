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
from modules.sim.actions.move_straight import move_straight
from shared.geo import dist_m, offset_latlon

HOME = GeoPoint(lat=37.95, lon=124.70)
SPEC = VehicleSpec(id="d1", name="d1", domain="air", speed_mps=10, endurance_min=40,
                   sensor_range_m=800, capabilities=["move_to", "return_home", "hold"], home=HOME)  # fmt: skip


def _at(east_m: float = 0, north_m: float = 0) -> GeoPoint:
    lat, lon = offset_latlon(HOME.lat, HOME.lon, east_m, north_m)
    return GeoPoint(lat=lat, lon=lon)


def _state(pos: GeoPoint) -> VehicleState:
    return VehicleState(id="d1", t_ms=0, pos=pos, heading_deg=0, battery_pct=100,
                        status=VehicleStatus.active, waypoint_idx=0)  # fmt: skip


def _passed(kind: CommandKind, **params) -> PassedCommand:
    cmd = Command(id="c1", vehicle_id="d1", kind=kind, params=params)
    return PassedCommand(command=cmd, checks=[], passed_ms=0)


def test_move_goes_speed_times_dt_toward_the_target():
    target = _at(north_m=1000)
    st = move_straight(
        _state(HOME), SPEC, _passed(CommandKind.move, target=target.model_dump()), 1000
    )
    assert dist_m(HOME, st.pos) == pytest.approx(10, abs=0.1)
    assert dist_m(st.pos, target) == pytest.approx(990, abs=0.5)
    assert st.waypoint_idx == 0  # not arrived yet


def test_move_arrival_marks_waypoint_idx_minus_one():
    target = _at(north_m=5)
    st = move_straight(
        _state(HOME), SPEC, _passed(CommandKind.move, target=target.model_dump()), 1000
    )
    assert dist_m(st.pos, target) < 1
    assert st.waypoint_idx == -1
    assert st.status == VehicleStatus.active


def test_return_home_heads_to_home_and_becomes_maintenance_on_arrival():
    far = _at(east_m=500)
    st = move_straight(_state(far), SPEC, _passed(CommandKind.return_home), 1000)
    assert dist_m(st.pos, HOME) == pytest.approx(490, abs=0.5)
    assert st.status == VehicleStatus.active
    near = move_straight(_state(_at(east_m=5)), SPEC, _passed(CommandKind.return_home), 1000)
    assert near.waypoint_idx == -1 and near.status == VehicleStatus.maintenance


def test_hold_does_not_move():
    start = _at(east_m=100)
    st = move_straight(_state(start), SPEC, _passed(CommandKind.hold), 1000)
    assert st.pos == start
