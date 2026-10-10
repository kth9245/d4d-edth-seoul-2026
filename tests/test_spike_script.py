"""The port tree (knowledge/spikes/rolecall_engine_proto/port/modules/...) is copy-ready and runs the
whole 3-minute script on the demo scenario (decisions 0015-0024, devil-advocate 2026-10-10)."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from contracts.models import Frame
from tools.check_imports import problems as import_problems

ROOT = Path(__file__).resolve().parent.parent
SPIKE = ROOT / "knowledge/spikes/rolecall_engine_proto"
PORT = SPIKE / "port"
ACTIONS = sorted(p for p in PORT.glob("modules/*/actions/*.py") if p.name != "__init__.py")
MIN = 60_000


@pytest.fixture(scope="module")
def result(tmp_path_factory):
    out = tmp_path_factory.mktemp("spike") / "frames.json"
    env = {**os.environ, "PYTHONPATH": f"{PORT}{os.pathsep}{ROOT}"}
    r = subprocess.run([sys.executable, str(SPIKE / "run_script.py"), "--out", str(out)],
                       cwd=ROOT, env=env, capture_output=True, text=True)  # fmt: skip
    assert r.returncode == 0, r.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    return {
        "start_ms": data["start_ms"],
        "frames": [Frame.model_validate(f) for f in data["frames"]],
    }


def _at(result, offset_ms):
    frames = result["frames"]
    return next((f for f in frames if f.t_ms - result["start_ms"] >= offset_ms), frames[-1])


def test_report_card_comes_from_sensing_after_the_boat_appears(result):
    reps = [r for r in result["frames"][-1].reports if r.kind == "target_detected"]
    assert reps and reps[0].vehicle_id == "d1"
    assert reps[0].t_ms - result["start_ms"] >= 11 * MIN


def test_one_decision_switches_four_vehicles(result):
    rep = next(r for r in result["frames"][-1].reports if r.kind == "target_detected")
    after = _at(result, rep.resolved_ms - result["start_ms"] + 5000)
    roles = {v.id: v.role_id for v in after.vehicles}
    want = {"d1": "watch", "usv": "approach", "ugv": "landing", "d2": "patrol_b"}
    assert {k: roles[k] for k in want} == want


def test_reserve_takes_over_the_watch_step(result):
    f = _at(result, 20 * MIN)
    d1, d3 = (next(v for v in f.vehicles if v.id == i) for i in ("d1", "d3"))
    assert d1.status in ("returning", "maintenance")
    assert (d3.role_id, d3.step_id) == ("watch", "watch")
    assert any(a.reason == "예비 투입: d1 대신" for a in f.assignments)
    assert result["frames"][-1].metrics.vehicle_gap_ms > 0


def test_switch_then_operator_picks_the_fast_boat(result):
    f = _at(result, 25 * MIN)
    d2 = next(v for v in f.vehicles if v.id == "d2")
    assert (d2.role_id, d2.target_id) == ("track_fast", "fast1")
    assert any(r.kind == "target_select" and r.resolved_ms for r in f.reports)


def test_only_the_direct_control_commands_are_blocked(result):
    blocks = result["frames"][-1].blocks
    assert [b.reason for b in blocks] == ["outside_zone", "battery_insufficient"]
    assert blocks[0].alternative is not None


@pytest.mark.parametrize("path", ACTIONS, ids=lambda p: p.stem)
def test_port_action_fits_the_action_rules(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 80, f"{path.name}: {len(lines)} lines"
    assert re.search(rf"^def {path.stem}\(", "\n".join(lines), re.M), "public function = file name"
    spec = (ROOT / "modules" / path.parent.parent.name / "SPEC.md").read_text(encoding="utf-8")
    assert f"| {path.stem} |" in spec, f"no SPEC row for {path.stem}"


def test_port_is_formatted_and_keeps_module_boundaries():
    ruff = [sys.executable, "-m", "ruff"]  # ship.sh runs .venv/bin/pytest without the venv on PATH
    fmt = subprocess.run([*ruff, "format", "--check", "--line-length", "100", str(PORT)],
                         capture_output=True, text=True)  # fmt: skip
    assert fmt.returncode == 0, fmt.stdout
    assert import_problems(PORT) == []
