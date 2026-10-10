from contracts.models import GeoPoint, Polygon, Target
from modules.runtime.actions.target_domain import DOMAIN_LABEL, target_domain
from shared.geo import offset_latlon

C = GeoPoint(lat=37.95, lon=124.70)


def _at(east_m: float, north_m: float) -> GeoPoint:
    lat, lon = offset_latlon(C.lat, C.lon, east_m, north_m)
    return GeoPoint(lat=lat, lon=lon)


ISLAND = [Polygon(points=[_at(-500, -500), _at(500, -500), _at(500, 500), _at(-500, 500)])]


def _tg(kind: str, pos: GeoPoint) -> Target:
    return Target(
        id="e1",
        kind=kind,
        pos=pos,
        vel_east_mps=0,
        vel_north_mps=0,
        first_seen_ms=0,
        last_seen_ms=0,
    )


def test_a_drone_is_air_anywhere():
    assert target_domain(_tg("drone", C), ISLAND) == "air"
    assert target_domain(_tg("drone", _at(2000, 0)), ISLAND) == "air"


def test_domain_follows_current_position():
    assert target_domain(_tg("ugv", C), ISLAND) == "ground"
    assert target_domain(_tg("ugv", _at(2000, 0)), ISLAND) == "sea"
    assert target_domain(_tg("usv", _at(0, -2000)), ISLAND) == "sea"


def test_labels():
    assert DOMAIN_LABEL == {"air": "공중", "ground": "지상", "sea": "해상"}


def test_domain_uses_where_it_was_last_seen():  # not the truth no sensor sees
    tg = _tg("usv", C).model_copy(update={"last_seen_pos": _at(0, -2000)})
    assert target_domain(tg, ISLAND) == "sea"
