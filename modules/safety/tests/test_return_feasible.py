from contracts.models import GeoPoint, VehicleSpec, VehicleState
from modules.safety.actions.return_feasible import return_feasible
from shared.geo import dist_m

HOME = GeoPoint(lat=37.0, lon=126.0)
# 10 m/s, 10 min: full battery gives 600 s * 0.8 = 480 s of round trip = 4800 m
SPEC = VehicleSpec(id="d1", name="d1", domain="air", speed_mps=10, endurance_min=10,
                   sensor_range_m=500, capabilities=[], home=HOME)  # fmt: skip


def state(pos: GeoPoint, battery: float) -> VehicleState:
    return VehicleState(id="d1", t_ms=0, pos=pos, heading_deg=0, battery_pct=battery,
                        status="active")  # fmt: skip


def north(m: float) -> GeoPoint:
    return GeoPoint(lat=HOME.lat + m / 111_195, lon=HOME.lon)


def test_feasible_round_trip():
    assert return_feasible(state(HOME, 100), SPEC, north(2000)) == (True, None)


def test_too_far_gives_farthest_feasible_point_on_the_segment():
    ok, alt = return_feasible(state(HOME, 100), SPEC, north(5000))
    assert not ok and alt is not None
    d = dist_m(HOME, alt)
    assert 2400 - 30 <= d <= 2400  # 200 slices of 5000 m = 25 m steps


def test_battery_is_scaled_by_percentage():
    assert return_feasible(state(HOME, 50), SPEC, north(1000)) == (True, None)
    assert not return_feasible(state(HOME, 50), SPEC, north(1300))[0]


def test_no_alternative_when_nothing_on_the_segment_fits():
    assert return_feasible(state(north(5000), 1), SPEC, north(6000)) == (False, None)
