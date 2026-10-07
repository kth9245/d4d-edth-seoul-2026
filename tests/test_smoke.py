import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_smoke_passes_on_demo_scenario():
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts/smoke.py")], capture_output=True, text=True, cwd=ROOT
    )
    assert r.returncode == 0, r.stderr
    assert "smoke OK" in r.stdout


def test_smoke_fails_on_bad_scenario(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "name: x\nstart_ms: 0\nduration_s: 5\nstep_ms: 500\norigin: {lat: 0, lon: 0}\n"
        "objects: [{id: a, kind: tank, start_east_m: 0, start_north_m: 0, alt_m: 1, "
        "vel_east_mps: 0, vel_north_mps: 0}]\n"
    )
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts/smoke.py"), "--scenario", str(bad)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert r.returncode == 1 and "kind" in r.stderr
