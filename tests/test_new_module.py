import subprocess
import sys
from pathlib import Path

from tools.spec import parse_spec

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "new_module.py"


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--root", str(root)], capture_output=True, text=True
    )


def test_scaffolds_module(tmp_path):
    r = run(tmp_path, "edge", "EDG")
    assert r.returncode == 0, r.stderr
    m = tmp_path / "modules" / "edge"
    for f in ("__init__.py", "AGENTS.md", "SPEC.md", "actions/__init__.py", "tests/__init__.py"):
        assert (m / f).exists(), f
    prefix, rows = parse_spec((m / "SPEC.md").read_text(encoding="utf-8"))
    assert prefix == "EDG" and rows == []
    assert "| id | 액션 |" in (m / "SPEC.md").read_text(encoding="utf-8")
    assert len((m / "AGENTS.md").read_text(encoding="utf-8").splitlines()) <= 40


def test_refuses_existing_and_bad_names(tmp_path):
    assert run(tmp_path, "edge", "EDG").returncode == 0
    again = run(tmp_path, "edge", "EDG")
    assert again.returncode == 1 and "이미" in again.stderr
    assert run(tmp_path, "Bad-Name", "BAD").returncode == 1
    assert run(tmp_path, "okname", "lower").returncode == 1
