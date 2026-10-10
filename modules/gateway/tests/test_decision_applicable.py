from contracts.models import Choice, Decision, Report
from modules.gateway.actions.decision_applicable import decision_applicable

CARD = Report(id="rep-1", t_ms=1, kind="target_detected", vehicle_id="d1", text="x",
              choices=[Choice(id="keep", label="유지"), Choice(id="strike_d2", label="타격")])  # fmt: skip


def dec(report_id="rep-1", choice_id="keep") -> Decision:
    return Decision(id="dec-1", t_ms=2, report_id=report_id, choice_id=choice_id)


def test_a_choice_that_is_on_the_card_is_applicable():
    assert decision_applicable([CARD], dec(choice_id="strike_d2"))


def test_a_choice_that_just_vanished_is_not_applicable():
    gone = CARD.model_copy(update={"choices": [Choice(id="keep", label="유지")]})
    assert not decision_applicable([gone], dec(choice_id="strike_d2"))


def test_an_unknown_card_is_not_applicable():
    assert not decision_applicable([CARD], dec(report_id="rep-9"))
