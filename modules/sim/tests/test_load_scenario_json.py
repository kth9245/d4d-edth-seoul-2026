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


def test_the_24h_drones_get_the_night_capabilities_from_the_ontology():  # decision 0051
    night = {v.id: v for v in load_scenario_json(DEMO).vehicles}
    day = load_scenario_json(ROOT / "demo" / "scenarios" / "baengnyeong_24h.json")
    assert day.ontology is not None
    assert all(v.kind_path and v.capabilities == night[v.id].capabilities for v in day.vehicles)
