"""SIM-13 sea_aim: 해상 기체·적 배가 이번 틱에 향할 점(결정 0034)
목표까지 직선이 섬(land)을 지나지 않으면 목표, 지나면 섬 모서리(바다 쪽 100 m)를 잇는 최단 경로의 첫 모서리.
목표가 육지 안이면 해안에서 50 m 바다 점으로 바꾼다. 지금 위치가 육지 안이면 돌아가지 않는다.
SPEC: modules/sim/SPEC.md#SIM-13
"""

import heapq
import math
from collections.abc import Sequence

from contracts.models import GeoPoint, Polygon
from shared.land import (
    blocked_xy,
    corners_xy,
    inside_xy,
    key,
    links_xy,
    rings,
    to_geo,
    to_sea,
    to_xy,
)


def _first_corner(p, g, cs, links, rs) -> int | None:
    """Dijkstra from p over the corners to g; the first corner of the shortest path, or None.
    A corner within 1 m of p is the one p stands on, so it is not a next step."""
    dist = {i: math.dist(p, c) for i, c in enumerate(cs)
            if math.dist(p, c) > 1 and not blocked_xy(p, c, rs)}  # fmt: skip
    first = {i: i for i in dist}
    heap = [(d, i) for i, d in dist.items()]
    heapq.heapify(heap)
    done: set[int] = set()
    best, best_first = math.inf, None
    while heap:
        d, i = heapq.heappop(heap)
        if d >= best:
            break
        if i in done:
            continue
        done.add(i)
        total = d + math.dist(cs[i], g)
        if total < best and not blocked_xy(cs[i], g, rs):
            best, best_first = total, first[i]
        for j in links[i]:
            nd = d + math.dist(cs[i], cs[j])
            if nd < dist.get(j, math.inf):
                dist[j], first[j] = nd, first[i]
                heapq.heappush(heap, (nd, j))
    return best_first


def sea_aim(pos: GeoPoint, goal: GeoPoint, land: Sequence[Polygon]) -> GeoPoint:
    k = key(land)
    if not k:
        return goal
    goal = to_sea(goal, land)
    ref, rs = k[0][0], rings(k)
    p, g = to_xy(pos.lat, pos.lon, ref), to_xy(goal.lat, goal.lon, ref)
    if inside_xy(p, rs) or not blocked_xy(p, g, rs):
        return goal
    i = _first_corner(p, g, corners_xy(k), links_xy(k), rs)
    return goal if i is None else to_geo(corners_xy(k)[i], ref)
