from pathlib import Path

import pytest

from modules.sim.actions.load_scenario import load_scenario

ROOT = Path(__file__).resolve().parents[3]

VALID = """name: t
start_ms: 1760061600000
duration_s: 10
step_ms: 500
origin: {lat: 37.5665, lon: 126.978}
objects:
  - {id: d1, kind: drone, start_east_m: -800, start_north_m: 0, alt_m: 120, vel_east_mps: 10, vel_north_mps: 0}
"""


def test_load_valid(tmp_path):
    p = tmp_path / "s.yaml"
    p.write_text(VALID)
    s = load_scenario(p)
    assert s.objects[0].kind == "drone" and s.step_ms == 500


def test_load_scenario_rejects_unknown_kind(tmp_path):
    p = tmp_path / "s.yaml"
    p.write_text(VALID.replace("kind: drone", "kind: helicopter"))
    with pytest.raises(ValueError) as e:
        load_scenario(p)
    assert "s.yaml" in str(e.value) and "kind" in str(e.value)


def test_load_scenario_rejects_nonpositive_duration(tmp_path):
    p = tmp_path / "s.yaml"
    p.write_text(VALID.replace("duration_s: 10", "duration_s: -1"))
    with pytest.raises(ValueError, match="duration_s"):
        load_scenario(p)


def test_demo_scenario_loads():
    s = load_scenario(ROOT / "demo/scenarios/seoul_mixed.yaml")
    assert {o.kind for o in s.objects} == {"drone", "balloon", "bird"}
