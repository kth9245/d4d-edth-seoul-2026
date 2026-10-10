from contracts.models import Injection, Report
from modules.gateway.actions.record_injections import record_injections

REQ = Injection(
    id="inj-1", t_ms=1000, label="고속 보트 추적: d2", play_by_vehicle={"d2": "track_fast"}
)


def test_new_request_makes_a_pending_card():
    injections, reports, cards, approved = record_injections([], [], [REQ], 1000)
    (card,) = cards
    assert (card.kind, card.vehicle_id, card.t_ms) == ("injection_pending", "d2", 1000)
    assert card.text.endswith(REQ.label) and not card.resolved_ms
    assert injections == [REQ] and reports == [] and approved == []


def test_approval_closes_the_card_and_is_returned():
    injections, _, cards, _ = record_injections([], [], [REQ], 1000)
    ok = REQ.model_copy(update={"status": "approved"})
    injections, reports, new, approved = record_injections(injections, cards, [ok], 2000)
    assert approved == [ok] and new == []
    assert injections == [ok]  # replaced, not duplicated
    assert reports[0].resolved_ms == 2000


def test_rejection_closes_the_card_without_approving():
    other = Report(id="r9", t_ms=0, kind="target_detected", text="보트")
    cards = record_injections([], [], [REQ], 1000)[2]
    no = REQ.model_copy(update={"status": "rejected"})
    injections, reports, _, approved = record_injections([REQ], [other, *cards], [no], 2000)
    assert approved == [] and injections == [no]
    assert reports[0].resolved_ms is None and reports[1].resolved_ms == 2000
