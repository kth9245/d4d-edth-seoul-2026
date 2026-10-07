import math

from contracts.models import Track
from modules.tracking.actions.predict_tracks import predict_tracks
from shared.geo import enu_delta_m


def test_constant_velocity_prediction():
    t = Track(
        id="T-a",
        t_ms=0,
        lat=37.5,
        lon=127.0,
        alt_m=100,
        vel_east_mps=10,
        vel_north_mps=-5,
        hits=3,
        last_seen_ms=0,
    )
    (p,) = predict_tracks([t], t_ms=2000)
    east, north = enu_delta_m(37.5, 127.0, p.lat, p.lon)
    assert math.isclose(east, 20, abs_tol=0.1) and math.isclose(north, -10, abs_tol=0.1)
    assert p.t_ms == 2000 and p.last_seen_ms == 0 and p.hits == 3
