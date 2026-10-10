"""SIM-08 advance_vehicles. Battery drain lives here, not in move_straight: SIM-05's
"배터리 선형 감소" is proven by test_move_drains_battery_linearly (the move goes through
advance_vehicles -> move_straight, then the drain is applied once per tick for every command)."""

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
from modules.sim.actions.advance_vehicles import advance_vehicles
from shared.geo import dist_m, enu_delta_m, offset_latlon

HOME = GeoPoint(lat=37.95, lon=124.70)
SPECS = {
    "d1": VehicleSpec(id="d1", name="d1", domain="air", speed_mps=10, endurance_min=40,
                      sensor_range_m=800, capabilities=["move_to", "hold"], home=HOME),
}  # fmt: skip
MIN = 60_000


def _at(east_m: float = 0, north_m: float = 0) -> GeoPoint:
    lat, lon = offset_latlon(HOME.lat, HOME.lon, east_m, north_m)
    return GeoPoint(lat=lat, lon=lon)


def _state(pos: GeoPoint = HOME, status=VehicleStatus.ready, active=None) -> VehicleState:
    return VehicleState(id="d1", t_ms=0, pos=pos, heading_deg=0, battery_pct=100,
                        status=status, active=active)  # fmt: skip


def _passed(kind: CommandKind, **params) -> PassedCommand:
    cmd = Command(id="c1", vehicle_id="d1", kind=kind, params=params)
    return PassedCommand(command=cmd, checks=[], passed_ms=0)


MOVE = _passed(CommandKind.move, target=_at(north_m=100_000).model_dump())


def test_new_command_becomes_active_and_moves_the_vehicle():
    [st] = advance_vehicles([_state()], SPECS, [MOVE], 1000, [])
    assert st.active == MOVE
    assert dist_m(HOME, st.pos) == pytest.approx(10, abs=0.1)
    assert st.t_ms == 1000
    assert st.status == VehicleStatus.active  # ready -> active once it moves


def test_tick_without_command_keeps_executing_active():
    [st] = advance_vehicles([_state()], SPECS, [MOVE], 1000, [])
    [st2] = advance_vehicles([st], SPECS, [], 1000, [])  # no new command this tick
    assert st2.active == MOVE
    assert dist_m(HOME, st2.pos) == pytest.approx(20, abs=0.1)


def test_move_drains_battery_linearly():
    # SIM-05 criterion, applied here: 100 / endurance_min percent per minute (40 min -> 2.5 %/min)
    [one] = advance_vehicles([_state()], SPECS, [MOVE], MIN, [])
    [two] = advance_vehicles([one], SPECS, [], MIN, [])
    assert one.battery_pct == pytest.approx(97.5)
    assert two.battery_pct == pytest.approx(95.0)


def test_hold_at_home_does_not_drain_and_stays_ready():
    [st] = advance_vehicles([_state()], SPECS, [_passed(CommandKind.hold)], MIN, [])
    assert st.battery_pct == 100
    assert st.status == VehicleStatus.ready


def test_lost_vehicle_does_not_move():
    start = _at(east_m=300)
    [st] = advance_vehicles([_state(start, VehicleStatus.lost, MOVE)], SPECS, [], 1000, [])
    assert st.pos == start and st.battery_pct == 100


def test_strike_flies_onto_the_target():
    tg = Target(id="fast1", kind="fast_boat", pos=_at(north_m=100), vel_east_mps=0,
                vel_north_mps=0, first_seen_ms=0, last_seen_ms=0)  # fmt: skip
    pc = _passed(CommandKind.strike, target_id="fast1", distance_m=0)
    (st,) = advance_vehicles([_state(status=VehicleStatus.active)], SPECS, [pc], 1000, [tg])
    assert dist_m(st.pos, tg.pos) == pytest.approx(90, abs=0.5)


def test_only_sea_vehicles_go_round_the_island():
    island = [Polygon(points=[_at(-500, -500), _at(500, -500), _at(500, 500), _at(-500, 500)])]
    start, goal = _at(-1000, -200), _at(1000, -200)
    usv = SPECS["d1"].model_copy(update={"id": "usv", "domain": "sea"})
    states = [_state(start, VehicleStatus.active),
              _state(start, VehicleStatus.active).model_copy(update={"id": "usv"})]  # fmt: skip
    to_goal = {"target": goal.model_dump()}
    usv_move = Command(id="c2", vehicle_id="usv", kind=CommandKind.move, params=to_goal)
    passed = [
        _passed(CommandKind.move, **to_goal),
        PassedCommand(command=usv_move, checks=[], passed_ms=0),
    ]
    air, sea = advance_vehicles(states, {**SPECS, "usv": usv}, passed, 1000, [], island)
    _, air_north = enu_delta_m(start.lat, start.lon, air.pos.lat, air.pos.lon)
    _, sea_north = enu_delta_m(start.lat, start.lon, sea.pos.lat, sea.pos.lon)
    assert air_north == pytest.approx(0, abs=0.1)  # air: straight east over the island
    assert sea_north < -1  # sea: toward the south-west corner
