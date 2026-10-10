import pytest

from contracts.models import (
    GeoPoint,
    Operation,
    Polygon,
    Scenario,
    ScenarioEvent,
    Target,
    VehicleState,
    VehicleStatus,
)
from modules.sim.actions.apply_events import apply_events
from shared.geo import dist_m

START = 1_791_633_600_000
DT = 200
P = GeoPoint(lat=37.985, lon=124.70)
ZONE = Polygon(points=[GeoPoint(lat=37.9, lon=124.56), GeoPoint(lat=38.0, lon=124.56),
                       GeoPoint(lat=38.0, lon=124.84)])  # fmt: skip
OP = Operation(id="op1", name="op", area=ZONE, zone=ZONE, vehicle_ids=["d1"], started_ms=START)
D1 = VehicleState(id="d1", t_ms=START, pos=P, heading_deg=0, battery_pct=100,
                  status=VehicleStatus.active)  # fmt: skip
BOAT = Target(id="boat1", kind="boat", pos=P, vel_east_mps=0, vel_north_mps=-1.0,
              first_seen_ms=0, last_seen_ms=0)  # fmt: skip


def _run(kind: str, params: dict, offset_ms: int = 60_000, t_ms: int | None = None, targets=()):
    ev = ScenarioEvent(offset_ms=offset_ms, kind=kind, params=params)
    sc = Scenario(id="s", operation=OP, vehicles=[], plays=[], events=[ev])
    t = START + offset_ms if t_ms is None else t_ms
    return apply_events(sc, [D1], list(targets), t, DT)


def test_event_fires_at_started_ms_plus_offset_ms_only():
    spawn = {"id": "boat1", "kind": "boat", "pos": P.model_dump()}
    assert _run("spawn_target", spawn, t_ms=START + 60_000 - DT)[1] == []  # tick before
    assert len(_run("spawn_target", spawn)[1]) == 1  # the tick that contains the event
    assert _run("spawn_target", spawn, t_ms=START + 60_000 + DT)[1] == []  # tick after


def test_spawn_target_adds_a_target_with_its_velocity():
    _, [tg] = _run("spawn_target", {"id": "boat1", "kind": "boat", "pos": P.model_dump(),
                                    "ve": 0, "vn": -1.0})  # fmt: skip
    assert tg.id == "boat1" and tg.kind == "boat"
    assert (tg.vel_east_mps, tg.vel_north_mps) == (0, -1.0)


def test_vehicle_battery_set_overrides_battery():
    [st], _ = _run("vehicle_battery_set", {"id": "d1", "pct": 21})
    assert st.battery_pct == 21


def test_target_move_changes_velocity():
    _, [tg] = _run("target_move", {"id": "boat1", "ve": 3.0, "vn": 0}, targets=[BOAT])
    assert (tg.vel_east_mps, tg.vel_north_mps) == (3.0, 0)


def test_split_target_adds_a_new_target_at_the_same_place():
    _, tgs = _run("split_target", {"id": "boat1", "new_id": "fast1", "kind": "fast_boat",
                                   "ve": -2.0, "vn": 6.0}, targets=[BOAT])  # fmt: skip
    src, new = tgs
    assert src.id == "boat1" and new.id == "fast1" and new.kind == "fast_boat"
    assert (new.vel_east_mps, new.vel_north_mps) == (-2.0, 6.0)
    assert dist_m(src.pos, new.pos) < 2  # split from the same position (then drifted one tick)


def test_vehicle_link_lost_marks_vehicle_lost():
    [st], _ = _run("vehicle_link_lost", {"id": "d1"})
    assert st.status == VehicleStatus.lost


def test_targets_drift_by_velocity_every_tick():
    sc = Scenario(id="s", operation=OP, vehicles=[], plays=[], events=[])
    _, [tg] = apply_events(sc, [D1], [BOAT], START + 1000, 1000)  # 1 s at vn = -1 m/s
    assert dist_m(BOAT.pos, tg.pos) == pytest.approx(1.0, abs=0.01)
    assert tg.pos.lat < BOAT.pos.lat  # moved south
