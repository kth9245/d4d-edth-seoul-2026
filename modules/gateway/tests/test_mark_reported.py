from contracts.models import GeoPoint, Report, Target
from modules.gateway.actions.mark_reported import mark_reported

P = GeoPoint(lat=37.98, lon=124.7)


def tg(tid: str, **kw) -> Target:
    return Target(id=tid, kind="boat", pos=P, vel_east_mps=0, vel_north_mps=0,
                  first_seen_ms=0, last_seen_ms=0, **kw)  # fmt: skip


def card(kind: str, vid: str, tid: str | None) -> Report:
    return Report(id=f"rep-{vid}", t_ms=1000, kind=kind, vehicle_id=vid, target_id=tid, text="")


def test_a_detection_card_marks_its_target_with_the_vehicle():
    out = mark_reported([tg("boat1"), tg("boat2")], [card("target_detected", "d2", "boat2")])
    assert [t.reported_by for t in out] == [None, "d2"]


def test_first_reporter_stays_and_other_cards_mark_nothing():
    targets = [tg("boat1", reported_by="d1"), tg("boat2")]
    cards = [card("target_detected", "d3", "boat1"), card("vehicle_gap", "d3", "boat2"),
             card("target_detected", "d2", None)]  # fmt: skip
    assert mark_reported(targets, cards) == targets
    assert mark_reported(targets, []) == targets
