from contracts.models import GeoPoint, Target, VehicleSpec, VehicleState, VehicleStatus
from modules.sensing.actions.observe_targets import observe_targets
from shared.geo import offset_latlon

T = 1_791_633_600_000
P = GeoPoint(lat=37.985, lon=124.70)
SPEC = VehicleSpec(id="d1", name="d1", domain="air", speed_mps=15, endurance_min=30,
                   sensor_range_m=1000, capabilities=[], home=P)  # fmt: skip
D1 = VehicleState(id="d1", t_ms=T, pos=P, heading_deg=0, battery_pct=100,
                  status=VehicleStatus.active)  # fmt: skip


def _target(east_m: float, seen_by=()) -> Target:
    lat, lon = offset_latlon(P.lat, P.lon, east_m, 0)
    return Target(id="boat1", kind="boat", pos=GeoPoint(lat=lat, lon=lon), vel_east_mps=0,
                  vel_north_mps=0, first_seen_ms=0, last_seen_ms=0, seen_by=list(seen_by))  # fmt: skip


def test_target_in_range_gets_vehicle_in_seen_by_and_last_seen_now():
    (t,) = observe_targets([D1], {"d1": SPEC}, [_target(900)], T)
    assert t.seen_by == ["d1"]
    assert t.last_seen_ms == T


def test_target_out_of_range_drops_vehicle_from_seen_by_and_keeps_last_seen():
    (t,) = observe_targets([D1], {"d1": SPEC}, [_target(1100, seen_by=["d1"])], T)
    assert t.seen_by == []
    assert t.last_seen_ms == 0


def test_vehicle_already_in_seen_by_is_not_duplicated():
    (t,) = observe_targets([D1], {"d1": SPEC}, [_target(100, seen_by=["d1"])], T)
    assert t.seen_by == ["d1"]
