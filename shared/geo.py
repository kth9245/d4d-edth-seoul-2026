"""Small-area WGS84 <-> local east/north meter conversions (equirectangular)."""

import math

from contracts.models import GeoPoint

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


# GeoPoint helpers for the ROLECALL engine (sim, sensing, safety, runtime share these).
def dist_m(a, b) -> float:
    """Distance in meters between two points with .lat/.lon."""
    return distance_m(a.lat, a.lon, b.lat, b.lon)


def lerp(a, b, f: float):
    """Point at fraction f (0..1) from a to b; altitude follows a."""
    return GeoPoint(lat=a.lat + (b.lat - a.lat) * f, lon=a.lon + (b.lon - a.lon) * f, alt_m=a.alt_m)


def move_toward(a, b, step_m: float):
    """Move from a toward b by step_m meters; stop at b."""
    d = dist_m(a, b)
    return b.model_copy() if d <= step_m else lerp(a, b, step_m / d)
