"""SFT-01 point_in_polygon: 점이 다각형(작전 구역) 안에 있는가 (ray casting)
SPEC: modules/safety/SPEC.md#SFT-01
"""

from contracts.models import GeoPoint, Polygon


def point_in_polygon(p: GeoPoint, poly: Polygon) -> bool:
    pts, inside, j = poly.points, False, len(poly.points) - 1
    for i in range(len(pts)):
        yi, xi, yj, xj = pts[i].lat, pts[i].lon, pts[j].lat, pts[j].lon
        crosses = (yi > p.lat) != (yj > p.lat)
        if crosses and p.lon < (xj - xi) * (p.lat - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside
