from pathlib import Path

import pytest

from contracts.models import Action, Condition, EmergencyRules, Exit, Play, Step
from modules.play.actions.check_links import check_links

PLAYS = Path(__file__).resolve().parents[3] / "demo" / "plays"


def step(sid: str, *go: str) -> Step:
    on = [Exit(cond=Condition(kind="arrived"), go_step=g) for g in go]
    return Step(id=sid, name=sid, do=Action(kind="hold"), on=on)


def play(steps: list[Step], entry: str = "a", **kw) -> Play:
    return Play(id="p", name="p", domains=["air"], steps=steps, entry=entry, **kw)


@pytest.mark.parametrize("path", sorted(PLAYS.glob("*.json")), ids=lambda p: p.stem)
def test_demo_plays_are_clean(path):
    assert check_links(Play.model_validate_json(path.read_text(encoding="utf-8"))) == []


def test_go_step_to_a_missing_step():
    (issue,) = check_links(play([step("a", "zzz")]))
    assert (issue.code, issue.step_id) == ("missing_step", "a") and "zzz" in issue.message


def test_missing_entry():
    codes = [i.code for i in check_links(play([step("a")], entry="nope"))]
    assert "missing_step" in codes


def test_step_unreachable_from_entry():
    (issue,) = check_links(play([step("a", "b"), step("b"), step("orphan")]))
    assert (issue.code, issue.step_id) == ("unreachable_step", "orphan")


def test_emergency_step_counts_as_reachable():
    em = EmergencyRules(battery_low_step="home")
    assert check_links(play([step("a"), step("home")], emergency=em)) == []
