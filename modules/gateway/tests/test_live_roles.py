from contracts.models import Action, Condition, Exit, Role, Step
from modules.gateway.tests.test_live import SCENARIO, START, make

PATROL_A = next(p for p in SCENARIO.roles if p.id == "patrol_a")


def no_report_role() -> Role:
    """patrol_a, but target_found goes straight to an approach with no report choice in between."""
    rush = Step(
        id="rush", name="바로 접근", do=Action(kind="approach_target", params={"target": "nearest"})
    )
    exits = [Exit(cond=Condition(kind="target_found"), go_step="rush")]
    patrol = PATROL_A.steps[0].model_copy(update={"on": exits})
    return PATROL_A.model_copy(update={"steps": [patrol, rush]})


def test_check_role_passes_a_demo_role():
    live, _ = make()
    assert live.check_role(PATROL_A).ok


def test_check_role_finds_the_missing_report_point_on_its_step():
    live, _ = make()
    chk = live.check_role(no_report_role())
    assert not chk.ok
    assert ("missing_report_point", "rush") in [(i.code, i.step_id) for i in chk.issues]


def test_save_role_with_errors_saves_nothing_and_keeps_the_run():
    live, _ = make()
    live.jump(60_000)
    assert not live.save_role(no_report_role()).ok
    saved = next(p for p in live.scenario.roles if p.id == "patrol_a")
    assert [s.id for s in saved.steps] == ["patrol", "report"]
    assert live.frame.t_ms == START + 60_000


def test_save_role_replaces_it_in_place_and_resets():
    live, _ = make()
    live.jump(60_000)
    order = [p.id for p in live.scenario.roles]
    assert live.save_role(PATROL_A.model_copy(update={"name": "해안 순찰 A2"})).ok
    assert [p.id for p in live.scenario.roles] == order
    assert next(p for p in live.scenario.roles if p.id == "patrol_a").name == "해안 순찰 A2"
    assert live.frame.t_ms == START + 200
    assert live.frame.run.status == "paused"


def test_the_engine_starts_from_the_saved_role():
    live, eng = make()
    live.save_role(PATROL_A.model_copy(update={"name": "해안 순찰 A2"}))
    assert "해안 순찰 A2" in [p.name for p in eng.inits[-1].roles]


def test_check_role_looks_at_the_whole_operation():
    live, _ = make()
    approach_air = next(p for p in SCENARIO.roles if p.id == "approach").model_copy(
        update={"domains": ["air"]}
    )  # usv receives approach through patrol_a's choice
    assert not live.check_role(approach_air).ok


def test_save_role_appends_a_new_id():
    live, _ = make()
    assert live.save_role(PATROL_A.model_copy(update={"id": "patrol_c"})).ok
    assert live.scenario.roles[-1].id == "patrol_c"


def test_delete_role_removes_it_and_resets_paused():  # decision 0050
    live, eng = make()
    live.set_speed(5)
    inits = len(eng.inits)
    left = live.delete_role("patrol_a")
    assert "patrol_a" not in [p.id for p in left]
    assert [p.id for p in live.scenario.roles] == [p.id for p in left]
    assert live.run.status == "paused" and len(eng.inits) == inits + 1


def test_delete_role_with_an_unknown_id_raises_and_changes_nothing():
    live, eng = make()
    before = [p.id for p in live.scenario.roles]
    try:
        live.delete_role("nope")
        raise AssertionError("expected KeyError")
    except KeyError:
        pass
    assert [p.id for p in live.scenario.roles] == before


def test_deleting_a_start_role_leaves_its_vehicles_unassigned():  # decision 0050
    live, _ = make()
    pid = live.scenario.operation.assign["d1"]
    live.delete_role(pid)
    assert pid not in live.scenario.operation.assign.values()
    assert "d1" not in live.scenario.operation.assign  # starts with no role, waits at home
