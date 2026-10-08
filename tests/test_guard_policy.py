import json
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


def test_ask_mode_lets_accept_through_to_human_prompt(tmp_path):
    r = repo(tmp_path)
    cmd = "uv run python scripts/decide.py accept 0001 --by me"
    assert g.check_pre(bash(cmd), r, "tracking/x", False, accept_mode="ask") is None


@pytest.mark.parametrize(
    "cmd",
    [
        "echo hi >> decisions/POLICY.md",
        "uv run python scripts/decide.py accept 1 && echo x >> decisions/POLICY.md",
    ],
)
def test_ask_mode_still_blocks_policy_writes(tmp_path, cmd):
    r = repo(tmp_path)
    assert g.check_pre(bash(cmd), r, "tracking/x", False, accept_mode="ask")


def _hook(tmp_path, cmd: str, *flags: str):
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    payload = json.dumps(
        {"tool_name": "Bash", "cwd": str(tmp_path), "tool_input": {"command": cmd}}
    )
    return subprocess.run(
        [sys.executable, str(ROOT / "tools/guard/check_edit.py"), "pre", *flags],
        input=payload,
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )


def test_hook_asks_human_for_accept_with_flag(tmp_path):
    res = _hook(tmp_path, "uv run python scripts/decide.py accept 0001 --by me", "--ask-accept")
    assert res.returncode == 0
    out = json.loads(res.stdout)["hookSpecificOutput"]
    assert out["permissionDecision"] == "ask" and out["hookEventName"] == "PreToolUse"


def test_hook_blocks_accept_without_flag(tmp_path):
    res = _hook(tmp_path, "uv run python scripts/decide.py accept 0001 --by me")
    assert res.returncode == 2 and "사람" in res.stderr


@pytest.mark.parametrize(
    "cmd",
    [
        "uv run python scripts/decide.py accept 0001 --by me",
        "python3 scripts/decide.py accept 0002",
        ["bash", "-lc", "uv run python scripts/decide.py accept 0003 --by me"],
        "bash -lc 'uv run python scripts/decide.py accept 0004'",
    ],
)
def test_defer_mode_passes_simple_accept_to_codex_rules(tmp_path, cmd):
    r = repo(tmp_path)
    assert g.check_pre(bash(cmd), r, "tracking/x", False, accept_mode="defer") is None


@pytest.mark.parametrize(
    "cmd",
    [
        "cd x && uv run python scripts/decide.py accept 0001",
        "uv run python scripts/decide.py accept 0001; rm -rf x",
        "uv run python scripts/decide.py accept $(cat id)",
        "echo hi >> decisions/POLICY.md",
    ],
)
def test_defer_mode_blocks_compound_accept_and_policy_writes(tmp_path, cmd):
    r = repo(tmp_path)
    assert g.check_pre(bash(cmd), r, "tracking/x", False, accept_mode="defer")


def test_hook_defer_flag_exits_zero_for_simple_accept(tmp_path):
    res = _hook(tmp_path, "uv run python scripts/decide.py accept 0001 --by me", "--defer-accept")
    assert res.returncode == 0 and res.stdout == ""


def test_codex_rules_prompt_for_accept():
    text = (ROOT / ".codex/rules/decide.rules").read_text(encoding="utf-8")
    assert '"scripts/decide.py", "accept"]' in text and 'decision = "prompt"' in text
    hooks = json.loads((ROOT / ".codex/hooks.json").read_text(encoding="utf-8"))
    cmds = [h["command"] for e in hooks["hooks"]["PreToolUse"] for h in e["hooks"]]
    assert any("--defer-accept" in c for c in cmds)


def test_hook_ask_flag_does_not_prompt_normal_commands(tmp_path):
    res = _hook(tmp_path, "ls", "--ask-accept")
    assert res.returncode == 0 and res.stdout == ""


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
