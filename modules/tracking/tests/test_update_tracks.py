import math

from contracts.models import Detection, Track
from modules.tracking.actions.update_tracks import update_tracks
from shared.geo import offset_latlon


def det_at(east: float, north: float) -> Detection:
    lat, lon = offset_latlon(37.5, 127.0, east, north)
    return Detection(
        id="a@1000", sensor="radar", t_ms=1000, lat=lat, lon=lon, alt_m=55, strength=0.5
    )


def test_first_update_uses_full_displacement():
    t = Track(id="T-a", t_ms=1000, lat=37.5, lon=127.0, alt_m=50, hits=1, last_seen_ms=0)
    d = det_at(20, 10)
    untouched = Track(id="T-b", t_ms=1000, lat=37.0, lon=127.0, alt_m=1, last_seen_ms=0)
    out = {x.id: x for x in update_tracks([t, untouched], {"T-a": d}, t_ms=1000)}
    a = out["T-a"]
    assert (a.lat, a.lon, a.alt_m, a.hits, a.last_seen_ms) == (d.lat, d.lon, 55, 2, 1000)
    assert math.isclose(a.vel_east_mps, 20, abs_tol=0.1)
    assert math.isclose(a.vel_north_mps, 10, abs_tol=0.1)
    assert out["T-b"] == untouched


def test_later_updates_smooth_velocity():
    t = Track(
        id="T-a", t_ms=1000, lat=37.5, lon=127.0, alt_m=50, hits=3, last_seen_ms=0, vel_east_mps=10
    )
    (a,) = update_tracks([t], {"T-a": det_at(20, 0)}, t_ms=1000)
    assert math.isclose(a.vel_east_mps, 10 + 0.3 * 20, abs_tol=0.1)
