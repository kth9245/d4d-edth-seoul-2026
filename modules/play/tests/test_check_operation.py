import json
from pathlib import Path

from contracts.models import Action, Condition, Exit, Operation, Play, Step, Switch
from modules.play.actions.check_operation import check_operation
from modules.sim import load_scenario_json

DEMO = Path(__file__).resolve().parents[3] / "demo"
SC = json.loads((DEMO / "scenarios" / "baengnyeong_night.json").read_text(encoding="utf-8"))
OP = Operation.model_validate(SC["operation"])
# demo start is the coast patrol (user, 10/10); patrol_a/patrol_b and the d1 -> d3 reserve are checked here
PATROL_OP = OP.model_copy(update={"assign": {**OP.assign, "d1": "patrol_a", "d2": "patrol_b"},
                                  "reserve": {"d1": ["d3"]}})  # fmt: skip
# capabilities come from the ontology through the loader (decision 0038)
LOADED = load_scenario_json(DEMO / "scenarios" / "baengnyeong_night.json")
SPECS = {v.id: v for v in LOADED.vehicles}
PLAYS = {
    p.stem: Play.model_validate_json(p.read_text(encoding="utf-8"))
    for p in (DEMO / "plays").glob("*.json")
}


def test_example_operation_passes():
    chk = check_operation(OP, PLAYS, SPECS)
    assert chk.ok and chk.issues == []
    assert set(chk.est_return_battery) == set(SPECS)
    assert all(b >= 30 for b in chk.est_return_battery.values())


def test_battery_estimate_is_the_lowest_over_every_play_a_vehicle_may_run():
    chk = check_operation(PATROL_OP, PLAYS, SPECS)
    d2_plays = ["patrol_b", "go_home", "coast_b"]  # start, switch all_home, switch patrol_all
    one = {pid: check_operation(PATROL_OP.model_copy(update={"assign": {"d2": pid}, "reserve": {},
                                                             "switches": []}), {pid: PLAYS[pid]}, SPECS)
           for pid in d2_plays}  # fmt: skip
    rated = [c.est_return_battery["d2"] for c in one.values() if "d2" in c.est_return_battery]
    assert chk.est_return_battery["d2"] == min(
        rated
    )  # coast_b: rotation play, no full-lap estimate


def test_operation_without_its_report_point_fails():
    rush = Play(id="patrol_a", name="r", domains=["air"], entry="patrol", approved=True, steps=[
        Step(id="patrol", name="p", do=Action(kind="hold"),
             on=[Exit(cond=Condition(kind="target_found"), go_step="go")]),
        Step(id="go", name="g", do=Action(kind="approach_target", params={"target": "nearest"})),
    ])  # fmt: skip
    chk = check_operation(PATROL_OP, {**PLAYS, "patrol_a": rush}, SPECS)
    assert not chk.ok and "missing_report_point" in [i.code for i in chk.issues]
    assert any(i.message.startswith("[patrol_a]") for i in chk.issues)


def test_switch_to_a_missing_play_fails():
    op = OP.model_copy(
        update={"switches": [Switch(id="x", label="x", play_by_vehicle={"d1": "nope"})]}
    )
    chk = check_operation(op, PLAYS, SPECS)
    assert [i.code for i in chk.issues] == ["missing_play"] and "nope" in chk.issues[0].message
