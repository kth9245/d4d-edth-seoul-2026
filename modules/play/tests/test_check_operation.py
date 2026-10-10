import json
from pathlib import Path

from contracts.models import Action, Condition, Exit, Operation, Play, Step, Switch
from modules.play.actions.check_operation import check_operation
from modules.sim import load_scenario_json

DEMO = Path(__file__).resolve().parents[3] / "demo"
SC = json.loads((DEMO / "scenarios" / "baengnyeong_night.json").read_text(encoding="utf-8"))
OP = Operation.model_validate(SC["operation"])
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
    chk = check_operation(OP, PLAYS, SPECS)
    d2_plays = ["standby", "patrol_b", "go_home"]  # start, choice "approach", switch all_home
    one = {pid: check_operation(OP.model_copy(update={"assign": {"d2": pid}, "reserve": {},
                                                      "switches": []}), {pid: PLAYS[pid]}, SPECS)
           for pid in d2_plays}  # fmt: skip
    assert chk.est_return_battery["d2"] == min(c.est_return_battery["d2"] for c in one.values())


def test_operation_without_its_report_point_fails():
    rush = Play(id="patrol_a", name="r", domains=["air"], entry="patrol", approved=True, steps=[
        Step(id="patrol", name="p", do=Action(kind="hold"),
             on=[Exit(cond=Condition(kind="target_found"), go_step="go")]),
        Step(id="go", name="g", do=Action(kind="approach_target", params={"target": "nearest"})),
    ])  # fmt: skip
    chk = check_operation(OP, {**PLAYS, "patrol_a": rush}, SPECS)
    assert not chk.ok and "missing_report_point" in [i.code for i in chk.issues]
    assert any(i.message.startswith("[patrol_a]") for i in chk.issues)


def test_switch_to_a_missing_play_fails():
    op = OP.model_copy(
        update={"switches": [Switch(id="x", label="x", play_by_vehicle={"d1": "nope"})]}
    )
    chk = check_operation(op, PLAYS, SPECS)
    assert [i.code for i in chk.issues] == ["missing_play"] and "nope" in chk.issues[0].message
