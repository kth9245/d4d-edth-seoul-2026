from contracts.models import Choice, ReportSpec
from modules.gateway.actions.check_saved_role import check_saved_role
from modules.gateway.tests.test_live import SCENARIO
from modules.gateway.tests.test_live_roles import PATROL_A, no_report_role

ROLES = {p.id: p for p in SCENARIO.roles}


def with_choice(role_by_vehicle: dict[str, str]):
    """patrol_a whose report choice sends vehicles to the given roles."""
    report = ReportSpec(
        text="t", choices=[Choice(id="c", label="c", role_by_vehicle=role_by_vehicle)]
    )
    step = PATROL_A.steps[1].model_copy(update={"report": report})
    return PATROL_A.model_copy(update={"steps": [PATROL_A.steps[0], step]})


def codes(chk):
    return [(i.code, i.step_id) for i in chk.issues]


def test_every_demo_role_passes():
    for p in SCENARIO.roles:
        assert check_saved_role(p, SCENARIO).ok, p.id


def test_a_choice_to_a_missing_role_fails():
    chk = check_saved_role(with_choice({"d1": "nope"}), SCENARIO)
    assert not chk.ok
    assert ("missing_role", None) in codes(chk)


def test_a_role_reached_by_a_choice_is_checked_for_that_vehicle():
    approach_air = ROLES["approach"].model_copy(
        update={"domains": ["air"]}
    )  # usv gets it via the choice
    chk = check_saved_role(approach_air, SCENARIO)
    assert not chk.ok
    assert "domain_mismatch" in [c for c, _ in codes(chk)]


def test_the_roles_own_issue_is_listed_once():
    chk = check_saved_role(no_report_role(), SCENARIO)
    assert codes(chk).count(("missing_report_point", "rush")) == 1


def test_battery_comes_from_the_roles_own_check():
    chk = check_saved_role(PATROL_A, SCENARIO)
    assert set(chk.est_return_battery) == {"d1", "d3"}
