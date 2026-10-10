import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("sync_docs", ROOT / "scripts" / "sync_docs.py")
sd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sd)

SPEC = (
    "<!-- prefix: TRK -->\n# tracking SPEC\n\n"
    "| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |\n|---|---|---|---|---|---|---|\n"
    "| TRK-01 | predict_tracks | a | b | c | 철수 | 완료 |\n"
)
CARD = (
    "---\nid: rf-bands\ntitle: RF 대역\nsummary: 2.4/5.8GHz\ntags: [rf]\n"
    "modules: [sensing, sim]\nconfidence: 확인됨\n---\n## 결론\n"
)
DECISION = (
    "---\nid: 0001\ntitle: 좌표 WGS84\nstatus: 확정\ndecided_by: 영희\n"
    "date: 2026-10-10\nmodules: [tracking]\nsupersedes: null\n---\n## 결정\n"
)


def make_repo(root: Path) -> None:
    (root / "modules" / "tracking").mkdir(parents=True)
    (root / "modules" / "tracking" / "SPEC.md").write_text(SPEC, encoding="utf-8")
    (root / "knowledge" / "cards").mkdir(parents=True)
    (root / "knowledge" / "cards" / "rf-bands.md").write_text(CARD, encoding="utf-8")
    (root / "decisions" / "log").mkdir(parents=True)
    (root / "decisions" / "log" / "0001-wgs84.md").write_text(DECISION, encoding="utf-8")
    (root / "decisions" / "POLICY.md").write_text("# 정책\n\n1. 오프라인 시연\n", encoding="utf-8")
    (root / "tasks").mkdir()
    (root / "AGENTS.md").write_text(
        "# 규칙\n<!-- POLICY:BEGIN -->\nold\n<!-- POLICY:END -->\n끝\n", encoding="utf-8"
    )


def test_board_lists_rows_with_module(tmp_path):
    make_repo(tmp_path)
    board = sd.build_board(tmp_path)
    assert "| tracking | TRK-01 | predict_tracks | 철수 | 완료 |" in board
    assert "자동 생성" in board


def test_knowledge_index_groups_by_module(tmp_path):
    make_repo(tmp_path)
    idx = sd.build_knowledge_index(tmp_path)
    assert "## sensing" in idx and "## sim" in idx
    assert "- [RF 대역](cards/rf-bands.md) — 2.4/5.8GHz `rf` (확인됨)" in idx


def test_decision_index(tmp_path):
    make_repo(tmp_path)
    idx = sd.build_decision_index(tmp_path)
    assert "| [0001](log/0001-wgs84.md) | 좌표 WGS84 | 확정 | 영희 | tracking |" in idx


def test_apply_policy_replaces_block_only():
    out = sd.apply_policy(
        "a\n<!-- POLICY:BEGIN -->\nold\n<!-- POLICY:END -->\nz\n", "# 정책\n\n1. x\n"
    )
    assert out == "a\n<!-- POLICY:BEGIN -->\n1. x\n<!-- POLICY:END -->\nz\n"


def test_apply_policy_without_markers_is_noop():
    assert sd.apply_policy("no markers\n", "1. x\n") == "no markers\n"


def test_sync_writes_files_and_reports_agents_change(tmp_path):
    make_repo(tmp_path)
    assert sd.sync(tmp_path) is True
    assert (tmp_path / "tasks" / "BOARD.md").exists()
    assert (tmp_path / "knowledge" / "INDEX.md").exists()
    assert (tmp_path / "decisions" / "INDEX.md").exists()
    assert "1. 오프라인 시연" in (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert sd.sync(tmp_path) is False


def test_sync_tolerates_empty_repo(tmp_path):
    assert sd.sync(tmp_path) is False
