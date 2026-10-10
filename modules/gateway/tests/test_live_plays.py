from contracts.models import Action, Condition, Exit, Play, Step
from modules.gateway.tests.test_live import SCENARIO, START, make

PATROL_A = next(p for p in SCENARIO.plays if p.id == "patrol_a")


def no_report_play() -> Play:
    """patrol_a, but target_found goes straight to an approach with no report choice in between."""
    rush = Step(
        id="rush", name="바로 접근", do=Action(kind="approach_target", params={"target": "nearest"})
    )
    exits = [Exit(cond=Condition(kind="target_found"), go_step="rush")]
    patrol = PATROL_A.steps[0].model_copy(update={"on": exits})
    return PATROL_A.model_copy(update={"steps": [patrol, rush]})


def test_check_play_passes_a_demo_play():
    live, _ = make()
    assert live.check_play(PATROL_A).ok


def test_check_play_finds_the_missing_report_point_on_its_step():
    live, _ = make()
    chk = live.check_play(no_report_play())
    assert not chk.ok
    assert ("missing_report_point", "rush") in [(i.code, i.step_id) for i in chk.issues]


def test_save_play_with_errors_saves_nothing_and_keeps_the_run():
    live, _ = make()
    live.jump(60_000)
    assert not live.save_play(no_report_play()).ok
    saved = next(p for p in live.scenario.plays if p.id == "patrol_a")
    assert [s.id for s in saved.steps] == ["patrol", "report"]
    assert live.frame.t_ms == START + 60_000


def test_save_play_replaces_it_in_place_and_resets():
    live, _ = make()
    live.jump(60_000)
    order = [p.id for p in live.scenario.plays]
    assert live.save_play(PATROL_A.model_copy(update={"name": "해안 순찰 A2"})).ok
    assert [p.id for p in live.scenario.plays] == order
    assert next(p for p in live.scenario.plays if p.id == "patrol_a").name == "해안 순찰 A2"
    assert live.frame.t_ms == START + 200
    assert live.frame.run.status == "paused"


def test_save_play_appends_a_new_id():
    live, _ = make()
    assert live.save_play(PATROL_A.model_copy(update={"id": "patrol_c"})).ok
    assert live.scenario.plays[-1].id == "patrol_c"
