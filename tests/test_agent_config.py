import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_claude_hooks_call_guard():
    cfg = json.loads((ROOT / ".claude/settings.json").read_text())
    pre = cfg["hooks"]["PreToolUse"][0]
    assert pre["matcher"] == "Edit|Write|MultiEdit|NotebookEdit"
    assert 'check_edit.py" pre' in pre["hooks"][0]["command"]
    assert 'check_edit.py" post' in cfg["hooks"]["PostToolUse"][0]["hooks"][0]["command"]


def test_codex_hooks_call_guard():
    cfg = json.loads((ROOT / ".codex/hooks.json").read_text())
    assert cfg["hooks"]["PreToolUse"][0]["matcher"] == "^apply_patch$"
    assert 'check_edit.py" pre' in cfg["hooks"]["PreToolUse"][0]["hooks"][0]["command"]


def test_bash_matcher_registered_pre_only():
    cl = json.loads((ROOT / ".claude/settings.json").read_text())["hooks"]
    assert any(h["matcher"] == "Bash" for h in cl["PreToolUse"])
    assert all(h["matcher"] != "Bash" for h in cl["PostToolUse"])
    cx = json.loads((ROOT / ".codex/hooks.json").read_text())["hooks"]
    assert any(h["matcher"] == "^(Bash|shell)$" for h in cx["PreToolUse"])
    assert all(h["matcher"] != "^(Bash|shell)$" for h in cx["PostToolUse"])


def test_skills_shared_via_symlink():
    link = ROOT / ".claude/skills"
    assert link.is_symlink() and link.resolve() == (ROOT / ".agents/skills").resolve()
    for name in ("new-action", "new-module", "kb-save", "decide", "ship", "task"):
        text = (ROOT / ".agents/skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert text.startswith(f"---\nname: {name}\ndescription: ")


def test_no_claude_md_anywhere():
    found = [p for p in ROOT.rglob("CLAUDE*.md") if "node_modules" not in p.parts]
    assert found == []
