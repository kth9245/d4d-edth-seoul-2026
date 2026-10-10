import pytest

from contracts.models import Action, ActionKind, CommandKind, Domain
from modules.role.actions.expand_action import TABLE, expand_action


@pytest.mark.parametrize(
    ("kind", "domain", "want"),
    [
        ("move_to", "sea", CommandKind.move),
        ("patrol_route", "ground", CommandKind.follow_route),
        ("watch_target", "air", CommandKind.orbit),
        ("watch_target", "sea", CommandKind.keep_distance),
        ("watch_point", "ground", CommandKind.hold),
        ("approach_target", "sea", CommandKind.keep_distance),
        ("return_home", "air", CommandKind.return_home),
        ("strike_target", "air", CommandKind.strike),
        ("strike_target", "sea", CommandKind.strike),
    ],
)
def test_action_becomes_the_domain_command(kind, domain, want):
    assert expand_action(Action(kind=kind), Domain(domain)) == want


def test_none_when_the_domain_cannot_do_it():
    assert expand_action(Action(kind="search_area"), Domain.ground) is None
    assert expand_action(Action(kind="strike_target"), "ground") is None


def test_ground_robot_can_watch_a_target():  # 24h raid: ugv tracks a ground enemy (decision 0055)
    assert expand_action(Action(kind="watch_target"), Domain.ground) == CommandKind.keep_distance


def test_table_covers_every_action_for_three_domains():
    assert set(TABLE) == {k.value for k in ActionKind}
    assert all(len(row) == len(Domain) for row in TABLE.values())


def test_ground_cannot_strike():
    assert expand_action(Action(kind="strike_target"), Domain.ground) is None
