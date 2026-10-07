import subprocess
import sys
from pathlib import Path

import pytest

from tools.guard import check_edit as g

ROOT = Path(__file__).resolve().parent.parent


def repo(tmp_path: Path) -> Path:
    (tmp_path / "modules" / "tracking" / "actions").mkdir(parents=True)
    (tmp_path / "decisions" / "log").mkdir(parents=True)
    return tmp_path


def write(path: Path) -> dict:
    return {
        "tool_name": "Write",
        "cwd": str(path.parent),
        "tool_input": {"file_path": str(path), "content": "x\n"},
    }


def bash(cmd) -> dict:
    return {"tool_name": "Bash", "cwd": "/", "tool_input": {"command": cmd}}


@pytest.mark.parametrize(
    "rel", ["demo/BUILT_HERE.md", "demo/scenarios/x.yaml", "pyproject.toml", "uv.lock"]
)
def test_always_editable_from_module_branch(tmp_path, rel):
    r = repo(tmp_path)
    assert g.check_pre(write(r / rel), r, "tracking/x", False) is None


def test_demo_runbook_still_infra_only(tmp_path):
    r = repo(tmp_path)
    assert g.check_pre(write(r / "demo/RUNBOOK.md"), r, "tracking/x", False)


def test_modules_init_is_infra(tmp_path):
    r = repo(tmp_path)
    assert g.check_pre(write(r / "modules/__init__.py"), r, "infra/x", False) is None
    assert g.check_pre(write(r / "modules/__init__.py"), r, "tracking/x", False)


def test_new_module_dir_editable_by_its_prefix(tmp_path):
    r = repo(tmp_path)
    assert g.check_pre(write(r / "modules/edge/pipeline.py"), r, "edge/x", False) is None
    assert g.check_pre(write(r / "modules/edge/pipeline.py"), r, "tracking/x", False)
    assert g.check_pre(write(r / "modules/edge/pipeline.py"), r, "main", False)


@pytest.mark.parametrize(
    "cmd",
    [
        "uv run python scripts/decide.py accept 0001 --by me",
        "python3 scripts/decide.py   accept 0002",
        "echo hi >> decisions/POLICY.md",
        "sed -i 's/a/b/' decisions/POLICY.md",
        "echo x | tee -a decisions/POLICY.md",
        ["bash", "-lc", "uv run python scripts/decide.py accept 0003"],
    ],
)
def test_bash_blocks_confirmation_and_policy_writes(tmp_path, cmd):
    r = repo(tmp_path)
    msg = g.check_pre(bash(cmd), r, "tracking/x", False)
    assert msg and "사람" in msg


@pytest.mark.parametrize(
    "cmd",
    ["ls", "uv run pytest", "uv run python scripts/decide.py new t", "cat decisions/POLICY.md"],
)
def test_bash_allows_normal_commands(tmp_path, cmd):
    r = repo(tmp_path)
    assert g.check_pre(bash(cmd), r, "tracking/x", False) is None


def test_guard_logs_unexpected_exception(tmp_path):
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    res = subprocess.run(
        [sys.executable, str(ROOT / "tools/guard/check_edit.py"), "pre"],
        input="[]",
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert res.returncode == 0
    log = tmp_path / ".git" / "guard-errors.log"
    assert log.exists() and "AttributeError" in log.read_text()
