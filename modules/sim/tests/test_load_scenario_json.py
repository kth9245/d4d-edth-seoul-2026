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


def test_assign_to_unknown_play_raises(tmp_path):
    def point_to_nothing(d):
        vid = next(iter(d["operation"]["assign"]))
        d["operation"]["assign"][vid] = "no-such-play"

    with pytest.raises(ValueError, match="assign"):
        load_scenario_json(_write(tmp_path, point_to_nothing))
