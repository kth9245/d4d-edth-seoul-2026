import modules.sim.actions.sea_aim as sea_aim_module
from contracts.models import GeoPoint, Polygon
from modules.sim.actions.sea_aim import sea_aim
from shared.geo import dist_m, offset_latlon

C = GeoPoint(lat=37.95, lon=124.70)


def _at(east_m: float, north_m: float) -> GeoPoint:
    lat, lon = offset_latlon(C.lat, C.lon, east_m, north_m)
    return GeoPoint(lat=lat, lon=lon)


ISLAND = [Polygon(points=[_at(-500, -500), _at(500, -500), _at(500, 500), _at(-500, 500)])]
SW, SE = _at(-570.71, -570.71), _at(570.71, -570.71)  # corners pushed 100 m out to sea
WEST, EAST = _at(-1000, -200), _at(1000, -200)


def test_no_land_or_open_water_goes_straight_to_the_goal():
    assert sea_aim(WEST, EAST, []) == EAST
    north = _at(1000, 800)
    assert sea_aim(_at(-1000, 800), north, ISLAND) == north


def test_blocked_line_turns_at_the_corner_on_the_shorter_side():
    assert dist_m(sea_aim(WEST, EAST, ISLAND), SW) < 1


def test_on_a_corner_it_heads_for_the_next_corner():
    assert dist_m(sea_aim(SW, EAST, ISLAND), SE) < 1


def test_goal_on_land_becomes_the_sea_point_off_the_coast():
    assert dist_m(sea_aim(_at(0, 1000), _at(0, 400), ISLAND), _at(0, 550)) < 1


def test_start_on_land_goes_straight():
    assert sea_aim(C, EAST, ISLAND) == EAST


def test_next_tick_toward_the_same_goal_checks_only_a_line_or_two(monkeypatch):
    # '다음 사건' jumps run thousands of ticks; a mover going round must not re-check every corner
    calls = []
    real = sea_aim_module.blocked_xy
    monkeypatch.setattr(sea_aim_module, "blocked_xy", lambda *a: calls.append(a) or real(*a))
    sea_aim(WEST, EAST, ISLAND)  # the first tick toward this goal may build its table
    calls.clear()
    assert dist_m(sea_aim(_at(-990, -210), EAST, ISLAND), SW) < 1
    assert len(calls) <= 3
