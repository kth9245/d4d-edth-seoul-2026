from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_root_agents_md_limits_and_markers():
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) <= 150
    assert "<!-- POLICY:BEGIN -->" in text and "<!-- POLICY:END -->" in text
    assert "knowledge/INDEX.md" in text and "decisions/INDEX.md" in text


def test_module_agents_md_limit():
    for p in (ROOT / "modules").glob("*/AGENTS.md"):
        assert len(p.read_text(encoding="utf-8").splitlines()) <= 40, p


def test_policy_synced_into_agents():
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "가상(synthetic)" in agents


def test_problem_doc_lists_t1_problems():
    text = (ROOT / "docs/problem.md").read_text(encoding="utf-8")
    for pid in ("T1-1", "T1-2", "T1-3", "T1-4"):
        assert pid in text
