import json
from pathlib import Path

import pytest

from contracts.models import Action, Condition, Exit, Operation, Role, Step
from modules.role.actions.check_role import check_role
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
TEMPLATES = sorted(pid for pid, p in ROLES.items() if p.template)


@pytest.mark.parametrize("pid", TEMPLATES)
def test_every_template_passes_for_the_demo_vehicles(pid):
    chk = check_role(ROLES[pid], OP, SPECS)
    assert chk.ok and chk.issues == []


def test_assigned_vehicle_and_its_reserve_get_a_battery_estimate():
    chk = check_role(ROLES["patrol_a"], OP, SPECS)
    assert chk.ok and set(chk.est_return_battery) == {"d1", "d3"}
    assert all(30 <= b <= 100 for b in chk.est_return_battery.values())


def test_vehicle_outside_the_role_domains():
    op = OP.model_copy(update={"assign": {"usv": "watch"}})
    chk = check_role(ROLES["watch"], op, SPECS)
    assert not chk.ok and "domain_mismatch" in [i.code for i in chk.issues]


def test_vehicle_missing_a_capability():
    weak = SPECS["usv"].model_copy(update={"capabilities": ["hold", "return_home"]})
    op = OP.model_copy(update={"assign": {"usv": "approach"}})
    chk = check_role(ROLES["approach"], op, {**SPECS, "usv": weak})
    assert not chk.ok and {i.code for i in chk.issues} == {"missing_capability"}


def test_missing_capability_message_shows_the_kind_path():  # decision 0038
    strike = next(p for p in LOADED.roles if p.id == "strike")
    op = OP.model_copy(update={"assign": {"d1": "strike"}})
    chk = check_role(strike, op, SPECS)
    msgs = [i.message for i in chk.issues if i.code == "missing_capability"]
    assert "d1는 strike_target를 못 함: 정찰 드론 → 공중 기체 → 기체 어디에도 이 능력 없음" in msgs


def test_role_without_its_report_point_fails():
    rush = Role(id="rush", name="r", domains=["sea"], entry="patrol", steps=[
        Step(id="patrol", name="p", do=Action(kind="hold"),
             on=[Exit(cond=Condition(kind="target_found"), go_step="go")]),
        Step(id="go", name="g", do=Action(kind="approach_target", params={"target": "nearest"})),
    ])  # fmt: skip
    chk = check_role(rush, OP, SPECS)
    assert not chk.ok and [i.code for i in chk.issues] == ["missing_report_point"]


def test_broken_link_fails():
    bad = ROLES["watch"].model_copy(update={"entry": "nope"})
    assert "missing_step" in [i.code for i in check_role(bad, OP, SPECS).issues]


def test_rotation_role_skips_the_full_lap_battery_check():  # decision 0037
    import json

    from contracts.models import Operation, Role

    root = Path(__file__).resolve().parents[3]
    night = json.loads((root / "demo" / "scenarios" / "baengnyeong_night.json").read_text("utf-8"))
    coast = Role.model_validate(
        json.loads((root / "demo" / "roles" / "coast_a.json").read_text("utf-8"))
    )
    specs = SPECS  # capabilities from the ontology (decision 0038)
    specs = {
        **specs,
        "d1": specs["d1"].model_copy(update={"endurance_min": 50.0}),
    }  # a lap must not fit
    op = Operation.model_validate(night["operation"]).model_copy(
        update={"assign": {"d1": "coast_a"}}
    )
    plain = check_role(coast, op.model_copy(update={"rotation_roles": []}), specs)
    assert "low_return_battery" in {i.code for i in plain.issues}
    assert check_role(coast, op, specs).ok
