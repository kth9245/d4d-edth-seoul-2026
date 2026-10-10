from pathlib import Path

import pytest

from contracts.models import Action, Choice, Condition, Exit, Play, ReportSpec, Step
from modules.play.actions.check_report_points import check_report_points

PLAYS = Path(__file__).resolve().parents[3] / "demo" / "plays"


def step(sid: str, kind: str = "hold", go: tuple[str, str] | None = None, report=None) -> Step:
    on = [Exit(cond=Condition(kind=go[0]), go_step=go[1])] if go else []
    return Step(id=sid, name=sid, do=Action(kind=kind), on=on, report=report)


def play(*steps: Step) -> Play:
    return Play(id="p", name="p", domains=["sea"], steps=list(steps), entry=steps[0].id)


ASK = ReportSpec(text="접근?", choices=[Choice(id="go", label="접근")])


@pytest.mark.parametrize("path", sorted(PLAYS.glob("*.json")), ids=lambda p: p.stem)
def test_demo_plays_are_clean(path):
    assert check_report_points(Play.model_validate_json(path.read_text(encoding="utf-8"))) == []


def test_approach_right_after_target_found_is_an_error():
    (issue,) = check_report_points(
        play(
            step("patrol", "patrol_route", ("target_found", "rush")),
            step("rush", "approach_target"),
        )
    )
    assert (issue.code, issue.step_id) == ("missing_report_point", "rush")


def test_a_report_with_choices_on_the_way_is_the_approval_point():
    p = play(step("patrol", "patrol_route", ("target_found", "ask")),
             step("ask", report=ASK, go=("operator_choice", "go")), step("go", "approach_target"))  # fmt: skip
    assert check_report_points(p) == []


def test_a_report_without_choices_is_not_an_approval():
    p = play(step("patrol", "patrol_route", ("target_found", "note")),
             step("note", report=ReportSpec(text="발견"), go=("arrived", "go")),
             step("go", "approach_target"))  # fmt: skip
    assert [i.step_id for i in check_report_points(p)] == ["go"]


def test_approach_without_target_found_is_not_checked():
    assert check_report_points(play(step("go", "approach_target"))) == []
