import math

from shared.geo import distance_m, enu_delta_m, offset_latlon


def test_offset_then_delta_roundtrip():
    lat, lon = 37.5665, 126.9780
    lat2, lon2 = offset_latlon(lat, lon, east_m=300.0, north_m=-400.0)
    east, north = enu_delta_m(lat, lon, lat2, lon2)
    assert math.isclose(east, 300.0, abs_tol=0.5)
    assert math.isclose(north, -400.0, abs_tol=0.5)


def test_distance_is_hypot_of_delta():
    lat, lon = 37.5665, 126.9780
    lat2, lon2 = offset_latlon(lat, lon, 300.0, 400.0)
    assert math.isclose(distance_m(lat, lon, lat2, lon2), 500.0, abs_tol=0.5)


def test_zero_offset_is_identity():
    assert offset_latlon(37.0, 127.0, 0.0, 0.0) == (37.0, 127.0)
