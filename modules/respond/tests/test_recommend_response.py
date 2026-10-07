from contracts.models import Assessment, ResponseKind
from modules.respond.actions.recommend_response import recommend_response


def a(cls: str, threat: float) -> Assessment:
    return Assessment(track_id="T-x", object_class=cls, threat=threat, reason="r")


def test_thresholds():
    assert recommend_response(a("drone", 0.95)).kind == ResponseKind.HARD_KILL
    assert recommend_response(a("drone", 0.75)).kind == ResponseKind.SOFT_KILL
    assert recommend_response(a("drone", 0.5)).kind == ResponseKind.OBSERVE
    assert recommend_response(a("balloon", 0.95)).kind == ResponseKind.OBSERVE
    r = recommend_response(a("drone", 0.75))
    assert r.track_id == "T-x" and "0.75" in r.reason
