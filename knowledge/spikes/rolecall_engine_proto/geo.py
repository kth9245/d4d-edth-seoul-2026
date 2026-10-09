"""Flat-earth helpers for the spike (fine at Baengnyeong scale, a few km). sim/safety port what they need."""
import math

from contracts.models import GeoPoint, Polygon

M_PER_DEG_LAT = 111_320.0


def m_per_deg_lon(lat: float) -> float:
    return M_PER_DEG_LAT * math.cos(math.radians(lat))


def dist_m(a: GeoPoint, b: GeoPoint) -> float:
    return math.hypot((b.lon - a.lon) * m_per_deg_lon(a.lat), (b.lat - a.lat) * M_PER_DEG_LAT)


def move_toward(p: GeoPoint, q: GeoPoint, step_m: float) -> GeoPoint:
    d = dist_m(p, q)
    if d <= step_m:
        return q.model_copy()
    f = step_m / d
    return GeoPoint(lat=p.lat + (q.lat - p.lat) * f, lon=p.lon + (q.lon - p.lon) * f, alt_m=p.alt_m)


def lerp(p: GeoPoint, q: GeoPoint, f: float) -> GeoPoint:
    return GeoPoint(lat=p.lat + (q.lat - p.lat) * f, lon=p.lon + (q.lon - p.lon) * f, alt_m=p.alt_m)


def point_in_polygon(p: GeoPoint, poly: Polygon) -> bool:  # safety Part2-7
    pts, inside, j = poly.points, False, len(poly.points) - 1
    for i in range(len(pts)):
        yi, xi, yj, xj = pts[i].lat, pts[i].lon, pts[j].lat, pts[j].lon
        if (yi > p.lat) != (yj > p.lat) and p.lon < (xj - xi) * (p.lat - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside
