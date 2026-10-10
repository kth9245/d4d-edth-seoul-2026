import json
from pathlib import Path

from contracts.models import Action, Condition, Exit, Operation, Role, Step, Switch
from modules.role.actions.check_operation import check_operation
from modules.sim import load_scenario_json

DEMO = Path(__file__).resolve().parents[3] / "demo"
SC = json.loads((DEMO / "scenarios" / "baengnyeong_night.json").read_text(encoding="utf-8"))
OP = Operation.model_validate(SC["operation"])
# capabilities come from the ontology through the loader (decision 0038)
LOADED = load_scenario_json(DEMO / "scenarios" / "baengnyeong_night.json")
SPECS = {v.id: v for v in LOADED.vehicles}
ROLES = {
    p.stem: Role.model_validate_json(p.read_text(encoding="utf-8"))
    for p in (DEMO / "roles").glob("*.json")
}


def test_example_operation_passes():
    chk = check_operation(OP, ROLES, SPECS)
    assert chk.ok and chk.issues == []
    assert set(chk.est_return_battery) == set(SPECS)
    assert all(b >= 30 for b in chk.est_return_battery.values())


def test_battery_estimate_is_the_lowest_over_every_role_a_vehicle_may_run():
    chk = check_operation(OP, ROLES, SPECS)
    d2_roles = ["standby", "patrol_b", "go_home"]  # start, choice "approach", switch all_home
    one = {pid: check_operation(OP.model_copy(update={"assign": {"d2": pid}, "reserve": {},
                                                      "switches": []}), {pid: ROLES[pid]}, SPECS)
           for pid in d2_roles}  # fmt: skip
    assert chk.est_return_battery["d2"] == min(c.est_return_battery["d2"] for c in one.values())


def test_operation_without_its_report_point_fails():
    rush = Role(id="patrol_a", name="r", domains=["air"], entry="patrol", approved=True, steps=[
        Step(id="patrol", name="p", do=Action(kind="hold"),
             on=[Exit(cond=Condition(kind="target_found"), go_step="go")]),
        Step(id="go", name="g", do=Action(kind="approach_target", params={"target": "nearest"})),
    ])  # fmt: skip
    chk = check_operation(OP, {**ROLES, "patrol_a": rush}, SPECS)
    assert not chk.ok and "missing_report_point" in [i.code for i in chk.issues]
    assert any(i.message.startswith("[patrol_a]") for i in chk.issues)


def test_switch_to_a_missing_role_fails():
    op = OP.model_copy(
        update={"switches": [Switch(id="x", label="x", role_by_vehicle={"d1": "nope"})]}
    )
    chk = check_operation(op, ROLES, SPECS)
    assert [i.code for i in chk.issues] == ["missing_role"] and "nope" in chk.issues[0].message
