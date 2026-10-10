import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/smoke.py"), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def test_smoke_runs_the_integration_1_slice_on_the_demo_scenario():
    # docs/research/09 section 4: target appears -> report card -> one decision switches the choice's
    # vehicles to their new roles, every resulting command passes safety, operator_actions = 1.
    r = run()
    assert r.returncode == 0, r.stderr
    assert "smoke OK" in r.stdout
    assert "operator_actions=1" in r.stdout


def test_smoke_fails_on_bad_scenario(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"id": "x"}', encoding="utf-8")
    r = run("--scenario", str(bad))
    assert r.returncode == 1 and "smoke FAIL" in r.stderr
