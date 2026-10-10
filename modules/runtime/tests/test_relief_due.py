from contracts.models import GeoPoint, VehicleSpec, VehicleState
from modules.runtime.actions.relief_due import relief_due
from shared.geo import offset_latlon

HOME = GeoPoint(lat=37.95, lon=124.70)
SPEC = VehicleSpec(id="d", name="d", domain="air", speed_mps=15, endurance_min=90, sensor_range_m=800,
                   capabilities=["patrol_route"], home=HOME)  # fmt: skip


def _st(battery: float, north_m: float) -> VehicleState:
    lat, lon = offset_latlon(HOME.lat, HOME.lon, 0, north_m)
    return VehicleState(id="d", t_ms=0, pos=GeoPoint(lat=lat, lon=lon), heading_deg=0, battery_pct=battery,
                        status="active")  # fmt: skip


def test_due_at_the_battery_threshold_whatever_the_relief_flight():
    assert relief_due(_st(49, 6000), SPEC, fly_min=0)  # 49 - 2 * 7.4 <= 35


def test_due_early_when_the_relief_flight_eats_the_margin_over_the_floor():
    st = _st(55, 6000)  # 55 - 7.4 - 31 = 16.6% over the floor
    assert not relief_due(st, SPEC, fly_min=8.0)  # 8.9% + 7% spare < 16.6%
    assert relief_due(
        st, SPEC, fly_min=9.0
    )  # 10% + 7% spare >= 16.6% (user, 10/10: between 5% and 10%)
