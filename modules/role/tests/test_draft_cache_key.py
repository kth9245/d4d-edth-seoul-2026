from contracts.models import GeoPoint, Operation, Polygon
from modules.role.actions.draft_cache_key import draft_cache_key

TEXT = "드론으로 북쪽 해안을 순찰하다가 고속정을 발견하면 바로 접근해."


def box(lat: float, lon: float, d: float) -> Polygon:
    pts = [(lat, lon), (lat, lon + d), (lat + d, lon + d), (lat + d, lon)]
    return Polygon(points=[GeoPoint(lat=a, lon=b) for a, b in pts])


def op(**kw) -> Operation:
    base = dict(
        id="op",
        name="백령도 야간 해안 경계",
        purpose="해안 경계",
        area=box(37.9, 124.6, 0.1),
        zone=box(37.9, 124.56, 0.28),
        vehicle_ids=["d1"],
        started_ms=1,
    )
    return Operation(**(base | kw))


def test_a_new_operation_on_the_same_zone_shares_the_key():  # decision 0062
    key = draft_cache_key(TEXT, op())
    assert len(key) == 64 and all(c in "0123456789abcdef" for c in key)
    renamed = op(id="new_op_1", name="QA 새 작전", purpose="", assign={"d1": "x"}, started_ms=99)
    assert draft_cache_key(TEXT, renamed) == key
    assert draft_cache_key(f"  {TEXT} ", op()) == key  # the operator's spacing at the ends


def test_the_text_area_and_zone_change_the_key():
    key = draft_cache_key(TEXT, op())
    assert draft_cache_key(TEXT + " 귀환해.", op()) != key
    assert draft_cache_key(TEXT, op(area=box(37.95, 124.6, 0.1))) != key
    assert draft_cache_key(TEXT, op(zone=box(37.9, 124.5, 0.3))) != key
