"""SIM-13 sea_aim: 해상 기체·적 배가 이번 틱에 향할 점(결정 0034)
목표까지 직선이 섬(land)을 지나지 않으면 목표, 지나면 섬 모서리(바다 쪽 100 m)를 잇는 최단 경로의 첫 모서리.
목표가 육지 안이면 해안에서 50 m 바다 점으로 바꾼다. 지금 위치가 육지 안이면 돌아가지 않는다.
SPEC: modules/sim/SPEC.md#SIM-13
"""

import heapq
import math
from collections.abc import Sequence
from functools import lru_cache

from contracts.models import GeoPoint, Polygon
from shared.land import (
    Key,
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


@lru_cache(maxsize=64)
def _via(k: Key, g: tuple[float, float]) -> tuple[float, ...]:
    """Shortest sea distance from each corner to g over the corner graph (inf if none), per goal."""
    cs, links, rs = corners_xy(k), links_xy(k), rings(k)
    dist = {i: math.dist(c, g) for i, c in enumerate(cs) if not blocked_xy(c, g, rs)}
    heap = [(d, i) for i, d in dist.items()]
    heapq.heapify(heap)
    done: set[int] = set()
    while heap:
        d, i = heapq.heappop(heap)
        if i in done:
            continue
        done.add(i)
        for j in links[i]:
            nd = d + math.dist(cs[i], cs[j])
            if nd < dist.get(j, math.inf):
                dist[j] = nd
                heapq.heappush(heap, (nd, j))
    return tuple(dist.get(i, math.inf) for i in range(len(cs)))


def sea_aim(pos: GeoPoint, goal: GeoPoint, land: Sequence[Polygon]) -> GeoPoint:
    k = key(land)
    if not k:
        return goal
    goal = to_sea(goal, land)
    ref, rs = k[0][0], rings(k)
    p, g = to_xy(pos.lat, pos.lon, ref), to_xy(goal.lat, goal.lon, ref)
    if inside_xy(p, rs) or not blocked_xy(p, g, rs):
        return goal
    # The first corner is the visible one with the least |p-c| + via[c]. Trying candidates in that
    # order tests a line or two per tick ('다음 사건' jumps run thousands). A corner within 1 m is
    # the one p stands on, so it is not a next step.
    cs, via = corners_xy(k), _via(k, g)
    order = sorted((math.dist(p, c) + via[i], i) for i, c in enumerate(cs)
                   if via[i] < math.inf and math.dist(p, c) > 1)  # fmt: skip
    i = next((i for _, i in order if not blocked_xy(p, cs[i], rs)), None)
    return goal if i is None else to_geo(cs[i], ref)
