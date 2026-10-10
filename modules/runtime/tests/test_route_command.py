from contracts.models import Action, CommandKind, GeoPoint
from modules.runtime.actions.route_command import route_command
from shared.geo import dist_m, offset_latlon

HERE = GeoPoint(lat=37.97, lon=124.70)
FIXED = [{"lat": 37.98, "lon": 124.66, "alt_m": 0}, {"lat": 37.98, "lon": 124.74, "alt_m": 0}]
SQUARE = [{"north_m": 300, "east_m": 0}, {"north_m": 300, "east_m": 300}]


def test_offsets_are_measured_from_where_the_vehicle_is():
    params = {"offsets": SQUARE, "route_name": "sq"}
    kind, p = route_command(Action(kind="patrol_route"), "air", HERE, params)
    assert kind == CommandKind.follow_route
    assert "offsets" not in p and p["route_name"] == "sq"
    lat, lon = offset_latlon(HERE.lat, HERE.lon, 300, 300)
    assert dist_m(GeoPoint(**p["route"][1]), GeoPoint(lat=lat, lon=lon)) < 0.5
    assert dist_m(GeoPoint(**p["route"][0]), HERE) > 299


def test_patrol_keeps_looping():
    kind, p = route_command(Action(kind="patrol_route"), "air", HERE, {"route": FIXED})
    assert kind == CommandKind.follow_route and "loop" not in p


def test_a_move_with_a_route_follows_it_once():
    params = {"route": FIXED, "route_name": "n"}
    kind, p = route_command(Action(kind="move_to"), "air", HERE, params)
    assert kind == CommandKind.follow_route and p["loop"] is False and p["route"] == FIXED


def test_a_relative_move_follows_once_from_here():
    params = {"offsets": [{"north_m": 1000, "east_m": 0}]}
    kind, p = route_command(Action(kind="move_to"), "air", HERE, params)
    assert kind == CommandKind.follow_route and p["loop"] is False
    assert dist_m(GeoPoint(**p["route"][0]), HERE) > 999


def test_a_point_move_and_other_actions_are_unchanged():
    target = {"lat": 37.99, "lon": 124.70, "alt_m": 0}
    move = route_command(Action(kind="move_to"), "air", HERE, {"target": target})
    assert move == (CommandKind.move, {"target": target})
    assert route_command(Action(kind="hold"), "air", HERE, {}) == (CommandKind.hold, {})
