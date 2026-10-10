import json
from pathlib import Path

import pytest

from contracts.models import Scenario
from modules.sim.actions.load_scenario_json import load_scenario_json

ROOT = Path(__file__).resolve().parents[3]
DEMO = ROOT / "demo" / "scenarios" / "baengnyeong_night.json"


def _write(tmp_path, mutate):
    data = json.loads(DEMO.read_text(encoding="utf-8"))
    mutate(data)
    p = tmp_path / "s.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_loads_the_demo_scenario():
    sc = load_scenario_json(DEMO)
    assert isinstance(sc, Scenario)
    assert sc.operation.started_ms is not None
    assert set(sc.operation.assign) <= set(sc.operation.vehicle_ids)


def test_invalid_value_raises_value_error_with_path_and_location(tmp_path):
    p = _write(tmp_path, lambda d: d["vehicles"][0].update(speed_mps="fast"))
    with pytest.raises(ValueError) as e:
        load_scenario_json(p)
    assert str(p) in str(e.value) and "speed_mps" in str(e.value)


def test_missing_started_ms_raises(tmp_path):
    p = _write(tmp_path, lambda d: d["operation"].update(started_ms=None))
    with pytest.raises(ValueError, match="started_ms"):
        load_scenario_json(p)


def test_assign_to_unknown_role_raises(tmp_path):
    def point_to_nothing(d):
        vid = next(iter(d["operation"]["assign"]))
        d["operation"]["assign"][vid] = "no-such-role"

    with pytest.raises(ValueError, match="assign"):
        load_scenario_json(_write(tmp_path, point_to_nothing))


def test_capabilities_come_from_the_ontology():  # decision 0038
    v = {x.id: x for x in load_scenario_json(DEMO).vehicles}
    assert "strike_target" not in v["d1"].capabilities
    assert "strike_target" in v["usv"].capabilities
    assert v["d2"].kind_path == ["무장 드론", "공중 기체", "기체"]


def test_scenario_without_ontology_keeps_hand_written_capabilities(tmp_path):  # decision 0038
    def plain(d):
        d.pop("ontology")
        for v in d["vehicles"]:
            v.pop("kind", None)
            v["capabilities"] = ["move_to", "hold"]

    sc = load_scenario_json(_write(tmp_path, plain))
    assert sc.ontology is None
    assert all(v.capabilities == ["move_to", "hold"] and v.kind_path == [] for v in sc.vehicles)


def test_the_24h_drones_get_the_night_armed_drone_capabilities_from_the_ontology():  # 0051, user 10/10
    armed = {v.id: v for v in load_scenario_json(DEMO).vehicles}["d2"]  # the night armed drone
    day = load_scenario_json(ROOT / "demo" / "scenarios" / "baengnyeong_24h.json")
    assert day.ontology is not None
    drones = [v for v in day.vehicles if v.domain.value == "air"]
    assert all(v.kind_path and v.capabilities == armed.capabilities for v in drones)


def test_the_24h_usv_and_ugv_stand_by_at_their_night_spots():  # user, 10/10
    night = {v.id: v for v in load_scenario_json(DEMO).vehicles}
    day = load_scenario_json(ROOT / "demo" / "scenarios" / "baengnyeong_24h.json")
    by = {v.id: v for v in day.vehicles}
    assert all(by[i].home == night[i].home and by[i].kind == night[i].kind for i in ("usv", "ugv"))
    assert day.operation.assign["usv"] == day.operation.assign["ugv"] == "standby"


def test_the_24h_coast_cards_call_the_usv_and_ugv_with_the_night_roles():  # user, 10/10
    night = {r.id: r for r in load_scenario_json(DEMO).roles}
    day = load_scenario_json(ROOT / "demo" / "scenarios" / "baengnyeong_24h.json")
    roles = {r.id: r for r in day.roles}
    assert all(roles[i] == night[i] for i in ("approach", "landing", "track_fast_sea", "strike"))
    for coast in ("coast_a", "coast_b"):
        card = roles[coast].steps[1].report
        assert [c.label for c in card.choices] == ["근접 확인", "수상정 인계"] and card.auto_choices
    assert day.operation.switches[0].role_by_vehicle == {"usv": "track_fast_sea"}
