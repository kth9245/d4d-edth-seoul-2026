import math

import pytest

from contracts.models import GeoPoint, Polygon
from shared.geo import dist_m, offset_latlon
from shared.land import blocked, corners_xy, inside, key, to_sea, to_xy

C = GeoPoint(lat=37.95, lon=124.70)


def _at(east_m: float, north_m: float) -> GeoPoint:
    lat, lon = offset_latlon(C.lat, C.lon, east_m, north_m)
    return GeoPoint(lat=lat, lon=lon)


def _poly(*pts) -> Polygon:
    return Polygon(points=[_at(e, n) for e, n in pts])


SQUARE = [_poly((-500, -500), (500, -500), (500, 500), (-500, 500))]  # counter-clockwise
SQUARE_CW = [_poly((-500, -500), (-500, 500), (500, 500), (500, -500))]
L_SHAPE = [_poly((0, 0), (1000, 0), (1000, 400), (400, 400), (400, 1000), (0, 1000))]
# Two 200 m arms with a 40 m slot between them (x -20..20, y 100..600).
U_SHAPE = [_poly((-220, 0), (220, 0), (220, 600), (20, 600), (20, 100), (-20, 100), (-20, 600),
                 (-220, 600))]  # fmt: skip


def test_inside_is_true_on_the_island_and_false_at_sea():
    assert inside(C, SQUARE)
    assert not inside(_at(-1000, 0), SQUARE)
    assert not inside(C, [])


def test_blocked_when_the_straight_line_crosses_the_island():
    assert blocked(_at(-1000, -200), _at(1000, -200), SQUARE)
    assert not blocked(_at(-1000, 800), _at(1000, 800), SQUARE)
    assert not blocked(_at(-1000, -200), _at(1000, -200), [])


def test_to_sea_moves_a_land_point_50_m_off_the_nearest_coast():
    assert dist_m(to_sea(_at(0, 400), SQUARE), _at(0, 550)) < 1
    sea = _at(-1000, 0)
    assert to_sea(sea, SQUARE) == sea
    assert to_sea(C, []) == C


def test_to_sea_pushes_past_a_narrow_inlet():
    # 10 m from the slot wall: pushes of 50, 100 and 200 m land on the other arm, 400 m is at sea
    assert not inside(to_sea(_at(-30, 300), U_SHAPE), U_SHAPE)


@pytest.mark.parametrize("land", [SQUARE, SQUARE_CW])
def test_corners_are_the_four_corners_pushed_100_m_out_either_way_round(land):
    k = key(land)
    centre = to_xy(C.lat, C.lon, k[0][0])
    cs = corners_xy(k)
    assert len(cs) == 4
    for c in cs:
        assert math.dist(c, centre) == pytest.approx(500 * math.sqrt(2) + 100, abs=1)


def test_reflex_corner_is_not_a_turning_point():
    assert len(corners_xy(key(L_SHAPE))) == 5  # six corners, one bends inward
