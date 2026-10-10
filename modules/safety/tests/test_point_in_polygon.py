from contracts.models import GeoPoint, Polygon
from modules.safety.actions.point_in_polygon import point_in_polygon


def P(lat: float, lon: float) -> GeoPoint:
    return GeoPoint(lat=lat, lon=lon)


SQUARE = Polygon(points=[P(37.0, 126.0), P(37.0, 126.1), P(37.1, 126.1), P(37.1, 126.0)])
# L shape: the square minus its north-east quarter
ELL = Polygon(
    points=[P(37.0, 126.0), P(37.0, 126.1), P(37.05, 126.1), P(37.05, 126.05),
            P(37.1, 126.05), P(37.1, 126.0)]
)  # fmt: skip


def test_inside():
    assert point_in_polygon(P(37.05, 126.05), SQUARE)


def test_outside():
    assert not point_in_polygon(P(37.2, 126.05), SQUARE)
    assert not point_in_polygon(P(37.05, 125.9), SQUARE)


def test_just_inside_and_just_outside_the_edge():
    assert point_in_polygon(P(37.0001, 126.05), SQUARE)
    assert not point_in_polygon(P(36.9999, 126.05), SQUARE)
    assert point_in_polygon(P(37.05, 126.0999), SQUARE)
    assert not point_in_polygon(P(37.05, 126.1001), SQUARE)


def test_concave_notch_is_outside():
    assert point_in_polygon(P(37.02, 126.08), ELL)
    assert point_in_polygon(P(37.08, 126.02), ELL)
    assert not point_in_polygon(P(37.08, 126.08), ELL)
