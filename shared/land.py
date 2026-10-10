"""Island (land) geometry for routing sea vehicles and enemy boats round islands (decision 0034).

Math runs in local meters (x east, y north) from one reference point per land list (the first point
of the first polygon), equirectangular: well under a meter off at island size (~10 km).
Rings, corners and the corner graph are cached by the polygon coordinates, so they are built once.
"""

import math
from collections.abc import Sequence
from functools import lru_cache

from contracts.models import GeoPoint, Polygon

EARTH_RADIUS_M = 6_371_000.0
XY = tuple[float, float]
Key = tuple[tuple[tuple[float, float], ...], ...]


def key(land: Sequence[Polygon]) -> Key:
    return tuple(tuple((p.lat, p.lon) for p in poly.points) for poly in land)


def to_xy(lat: float, lon: float, ref: tuple[float, float]) -> XY:
    x = math.radians(lon - ref[1]) * EARTH_RADIUS_M * math.cos(math.radians(ref[0]))
    return (x, math.radians(lat - ref[0]) * EARTH_RADIUS_M)


def to_geo(xy: XY, ref: tuple[float, float]) -> GeoPoint:
    lat = ref[0] + math.degrees(xy[1] / EARTH_RADIUS_M)
    lon = ref[1] + math.degrees(xy[0] / (EARTH_RADIUS_M * math.cos(math.radians(ref[0]))))
    return GeoPoint(lat=lat, lon=lon)


@lru_cache(maxsize=16)
def rings(k: Key) -> tuple[tuple[XY, ...], ...]:
    ref = k[0][0]
    return tuple(tuple(to_xy(lat, lon, ref) for lat, lon in poly) for poly in k)


def _sides(ring):
    return zip(ring, ring[1:] + ring[:1], strict=True)


def _cross(o: XY, a: XY, b: XY) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _unit(x: float, y: float) -> XY:
    n = math.hypot(x, y) or 1.0
    return (x / n, y / n)


def _in_ring(p: XY, ring) -> bool:
    hit = False
    for (x1, y1), (x2, y2) in _sides(ring):
        if (y1 > p[1]) != (y2 > p[1]) and p[0] < x1 + (p[1] - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def inside_xy(p: XY, rs) -> bool:
    return any(_in_ring(p, r) for r in rs)


@lru_cache(maxsize=16)
def _boxed_sides(rs) -> tuple[tuple[XY, XY, float, float, float, float], ...]:
    return tuple((c, d, min(c[0], d[0]), max(c[0], d[0]), min(c[1], d[1]), max(c[1], d[1]))
                 for r in rs for c, d in _sides(r))  # fmt: skip


def blocked_xy(a: XY, b: XY, rs) -> bool:
    """The segment a-b goes over land: it crosses a coast side, or its middle is on land.
    Sides whose bounding box misses the segment's are skipped (most of them, on a long coast)."""
    if inside_xy(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), rs):
        return True
    x0, x1, y0, y1 = min(a[0], b[0]), max(a[0], b[0]), min(a[1], b[1]), max(a[1], b[1])
    for c, d, cx0, cx1, cy0, cy1 in _boxed_sides(rs):
        if cx1 < x0 or cx0 > x1 or cy1 < y0 or cy0 > y1:
            continue
        if _cross(c, d, a) * _cross(c, d, b) < 0 and _cross(a, b, c) * _cross(a, b, d) < 0:
            return True
    return False


@lru_cache(maxsize=16)
def corners_xy(k: Key) -> tuple[XY, ...]:
    """Convex coast corners pushed 100 m out to sea along the outer bisector (a shortest path round
    an island bends only there). A pushed corner that lands on land is dropped."""
    rs, out = rings(k), []
    for r in rs:
        ccw = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in _sides(r)) > 0
        s = 1.0 if ccw else -1.0
        for prev, v, nxt in zip(r[-1:] + r[:-1], r, r[1:] + r[:1], strict=True):
            turn = _cross(prev, v, nxt)
            if turn == 0 or (turn > 0) != ccw:  # straight or reflex corner
                continue
            e1, e2 = _unit(v[0] - prev[0], v[1] - prev[1]), _unit(nxt[0] - v[0], nxt[1] - v[1])
            b = _unit(s * (e1[1] + e2[1]), -s * (e1[0] + e2[0]))  # sum of the two outward normals
            c = (v[0] + b[0] * 100.0, v[1] + b[1] * 100.0)
            if not inside_xy(c, rs):
                out.append(c)
    return tuple(out)


@lru_cache(maxsize=16)
def links_xy(k: Key) -> tuple[tuple[int, ...], ...]:
    """For each corner, the other corners it sees across open sea."""
    cs, rs = corners_xy(k), rings(k)
    return tuple(
        tuple(j for j in range(len(cs)) if j != i and not blocked_xy(cs[i], cs[j], rs))
        for i in range(len(cs))
    )


def inside(p: GeoPoint, land: Sequence[Polygon]) -> bool:
    k = key(land)
    return bool(k) and inside_xy(to_xy(p.lat, p.lon, k[0][0]), rings(k))


def blocked(a: GeoPoint, b: GeoPoint, land: Sequence[Polygon]) -> bool:
    k = key(land)
    if not k:
        return False
    ref = k[0][0]
    return blocked_xy(to_xy(a.lat, a.lon, ref), to_xy(b.lat, b.lon, ref), rings(k))


def _nearest_on(p: XY, c: XY, d: XY) -> XY:
    dx, dy = d[0] - c[0], d[1] - c[1]
    t = ((p[0] - c[0]) * dx + (p[1] - c[1]) * dy) / ((dx * dx + dy * dy) or 1.0)
    t = max(0.0, min(1.0, t))
    return (c[0] + t * dx, c[1] + t * dy)


def to_sea(p: GeoPoint, land: Sequence[Polygon], margin_m: float = 50.0) -> GeoPoint:
    """p itself when at sea; on land, the nearest coast point pushed margin_m out to sea (doubled up
    to 16x when a narrow inlet puts the pushed point on the opposite shore)."""
    k = key(land)
    if not k:
        return p
    ref, rs = k[0][0], rings(k)
    q = to_xy(p.lat, p.lon, ref)
    if not inside_xy(q, rs):
        return p
    sides = [(c, d) for r in rs for c, d in _sides(r)]
    shore = min((_nearest_on(q, c, d) for c, d in sides), key=lambda s: math.dist(q, s))
    u = _unit(shore[0] - q[0], shore[1] - q[1])
    for m in (margin_m * 2**i for i in range(5)):
        out = (shore[0] + u[0] * m, shore[1] + u[1] * m)
        if not inside_xy(out, rs):
            return to_geo(out, ref).model_copy(update={"alt_m": p.alt_m})
    return p
