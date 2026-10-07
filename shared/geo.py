"""Small-area WGS84 <-> local east/north meter conversions (equirectangular)."""

import math

EARTH_RADIUS_M = 6_371_000.0


def offset_latlon(lat: float, lon: float, east_m: float, north_m: float) -> tuple[float, float]:
    if east_m == 0.0 and north_m == 0.0:
        return (lat, lon)
    dlat = math.degrees(north_m / EARTH_RADIUS_M)
    dlon = math.degrees(east_m / (EARTH_RADIUS_M * math.cos(math.radians(lat))))
    return (lat + dlat, lon + dlon)


def enu_delta_m(lat1: float, lon1: float, lat2: float, lon2: float) -> tuple[float, float]:
    mean_lat = math.radians((lat1 + lat2) / 2)
    east = math.radians(lon2 - lon1) * EARTH_RADIUS_M * math.cos(mean_lat)
    north = math.radians(lat2 - lat1) * EARTH_RADIUS_M
    return (east, north)


def distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    east, north = enu_delta_m(lat1, lon1, lat2, lon2)
    return math.hypot(east, north)
