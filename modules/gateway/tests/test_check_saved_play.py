from contracts.models import Choice, ReportSpec
from modules.gateway.actions.check_saved_play import check_saved_play
from modules.gateway.tests.test_live import SCENARIO
from modules.gateway.tests.test_live_plays import PATROL_A, no_report_play

PLAYS = {p.id: p for p in SCENARIO.plays}


def with_choice(play_by_vehicle: dict[str, str]):
    """patrol_a whose report choice sends vehicles to the given plays."""
    report = ReportSpec(
        text="t", choices=[Choice(id="c", label="c", play_by_vehicle=play_by_vehicle)]
    )
    step = PATROL_A.steps[1].model_copy(update={"report": report})
    return PATROL_A.model_copy(update={"steps": [PATROL_A.steps[0], step]})


def codes(chk):
    return [(i.code, i.step_id) for i in chk.issues]


def test_every_demo_play_passes():
    for p in SCENARIO.plays:
        assert check_saved_play(p, SCENARIO).ok, p.id


def test_a_choice_to_a_missing_play_fails():
    chk = check_saved_play(with_choice({"d1": "nope"}), SCENARIO)
    assert not chk.ok
    assert ("missing_play", None) in codes(chk)


def test_a_play_reached_by_a_choice_is_checked_for_that_vehicle():
    approach_air = PLAYS["approach"].model_copy(
        update={"domains": ["air"]}
    )  # usv gets it via the choice
    chk = check_saved_play(approach_air, SCENARIO)
    assert not chk.ok
    assert "domain_mismatch" in [c for c, _ in codes(chk)]


def test_the_plays_own_issue_is_listed_once():
    chk = check_saved_play(no_report_play(), SCENARIO)
    assert codes(chk).count(("missing_report_point", "rush")) == 1


def test_battery_comes_from_the_plays_own_check():
    chk = check_saved_play(PATROL_A, SCENARIO)  # demo starts on the coasts: nobody starts patrol_a
    assert set(chk.est_return_battery) == {"d1", "d2", "d3", "d4"}
