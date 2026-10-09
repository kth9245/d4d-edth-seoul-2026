import json
import subprocess
import sys
from pathlib import Path

from tools.guard import check_edit as g

ROOT = Path(__file__).resolve().parent.parent
SPEC = (
    "<!-- prefix: TRK -->\n| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |\n"
    "|---|---|---|---|---|---|---|\n| TRK-01 | predict_tracks | a | b | c | d | 진행중 |\n"
)


def repo(tmp_path: Path) -> Path:
    for m in ("tracking", "assess", "cop-ui"):
        (tmp_path / "modules" / m / "actions").mkdir(parents=True)
    (tmp_path / "modules" / "tracking" / "SPEC.md").write_text(SPEC, encoding="utf-8")
    (tmp_path / "decisions" / "log").mkdir(parents=True)
    return tmp_path


def claude(path: Path, content: str = "x\n", tool: str = "Write") -> dict:
    key = "content" if tool == "Write" else "new_string"
    return {
        "tool_name": tool,
        "cwd": str(path.parent),
        "tool_input": {"file_path": str(path), key: content},
    }


def codex(cwd: Path, patch: str) -> dict:
    return {"tool_name": "apply_patch", "cwd": str(cwd), "tool_input": {"command": patch}}


def test_owner_branch_can_edit_own_module(tmp_path):
    r = repo(tmp_path)
    p = claude(r / "modules/tracking/pipeline.py")
    assert g.check_pre(p, r, "tracking/kalman", False) is None


def test_any_branch_can_edit_any_module(tmp_path):
    r = repo(tmp_path)
    assert g.check_pre(claude(r / "modules/tracking/x.py"), r, "main", False) is None
    assert (
        g.check_pre(claude(r / "modules/assess/pipeline.py"), r, "tracking/kalman", False) is None
    )
    assert g.check_pre(claude(r / "knowledge/cards/a.md"), r, "main", False) is None


def test_unregistered_new_action_blocked(tmp_path):
    r = repo(tmp_path)
    msg = g.check_pre(
        claude(r / "modules/tracking/actions/smooth_tracks.py"), r, "tracking/x", False
    )
    assert msg and "new_action.py" in msg
    ok = claude(r / "modules/tracking/actions/predict_tracks.py")
    assert g.check_pre(ok, r, "tracking/x", False) is None


def test_freeze_skips_spec_registration(tmp_path):
    r = repo(tmp_path)
    p = claude(r / "modules/tracking/actions/smooth_tracks.py")
    assert g.check_pre(p, r, "tracking/x", True) is None


def test_protected_files(tmp_path):
    r = repo(tmp_path)
    for rel in (
        ".env",
        "decisions/POLICY.md",
        "tasks/BOARD.md",
        "tasks/log.jsonl",
        "tasks/NOW.md",
        "knowledge/INDEX.md",
        "modules/cop-ui/src/contracts.gen.ts",
        "contracts/schema/track.json",
    ):
        assert g.check_pre(claude(r / rel), r, "infra/x", False), rel


def test_confirmed_decision_protected(tmp_path):
    r = repo(tmp_path)
    d = r / "decisions/log/0001-a.md"
    d.write_text("---\nid: 0001\nstatus: 확정\n---\n", encoding="utf-8")
    assert g.check_pre(claude(d, tool="Edit"), r, "tracking/x", False)


def test_ai_cannot_write_confirmed_status(tmp_path):
    r = repo(tmp_path)
    p = claude(r / "decisions/log/0002-b.md", "---\nstatus: 확정\n---\n")
    assert g.check_pre(p, r, "tracking/x", False)
    p2 = claude(r / "decisions/log/0002-b.md", "---\nstatus: 제안\n---\n")
    assert g.check_pre(p2, r, "tracking/x", False) is None


def test_codex_relative_path_resolves_from_cwd(tmp_path):
    r = repo(tmp_path)
    patch = "*** Begin Patch\n*** Add File: actions/smooth_tracks.py\n+x\n*** End Patch\n"
    msg = g.check_pre(codex(r / "modules/tracking", patch), r, "tracking/x", False)
    assert msg and "smooth_tracks" in msg
    patch2 = "*** Begin Patch\n*** Update File: pipeline.py\n@@\n-a\n+b\n*** End Patch\n"
    assert g.check_pre(codex(r / "modules/tracking", patch2), r, "tracking/x", False) is None
    patch3 = "*** Begin Patch\n*** Update File: ../../.env\n@@\n+b\n*** End Patch\n"
    assert g.check_pre(codex(r / "modules/tracking", patch3), r, "tracking/x", False)


def test_codex_added_confirmed_status_blocked(tmp_path):
    r = repo(tmp_path)
    patch = "*** Begin Patch\n*** Add File: decisions/log/0003-c.md\n+status: 확정\n*** End Patch\n"
    assert g.check_pre(codex(r, patch), r, "tracking/x", False)


def test_path_outside_repo_allowed(tmp_path):
    r = repo(tmp_path / "repo")
    assert g.check_pre(claude(tmp_path / "elsewhere.py"), r, "main", False) is None


def test_post_length_limits(tmp_path):
    r = repo(tmp_path)
    a = r / "modules/tracking/actions/predict_tracks.py"
    a.write_text("x = 1\n" * 81)
    assert "80" in g.check_post(claude(a), r, False)
    a.write_text("x = 1\n" * 80)
    assert g.check_post(claude(a), r, False) is None
    other = r / "modules/tracking/pipeline.py"
    other.write_text("x = 1\n" * 201)
    assert "200" in g.check_post(claude(other), r, False)
    assert g.check_post(claude(other), r, True) is None


def test_branch_during_rebase(tmp_path):
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    rb = tmp_path / ".git" / "rebase-merge"
    rb.mkdir()
    (rb / "head-name").write_text("refs/heads/tracking/kalman\n")
    subprocess.run(
        ["git", "-C", str(tmp_path), "commit", "-q", "--allow-empty", "-m", "x"],
        check=True,
        env={
            "GIT_AUTHOR_NAME": "a",
            "GIT_AUTHOR_EMAIL": "a@a",
            "GIT_COMMITTER_NAME": "a",
            "GIT_COMMITTER_EMAIL": "a@a",
            "PATH": "/usr/bin:/bin",
        },
    )
    subprocess.run(["git", "-C", str(tmp_path), "checkout", "-q", "--detach"], check=True)
    assert g.current_branch(tmp_path) == "tracking/kalman"


def test_cli_exit_codes(tmp_path):
    r = repo(tmp_path)
    subprocess.run(["git", "init", "-q", "-b", "main", str(r)], check=True)
    payload = json.dumps(claude(r / "decisions/POLICY.md"))
    res = subprocess.run(
        [sys.executable, str(ROOT / "tools/guard/check_edit.py"), "pre"],
        input=payload,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 2 and "POLICY" in res.stderr
    res = subprocess.run(
        [sys.executable, str(ROOT / "tools/guard/check_edit.py"), "pre"],
        input="not json",
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0


def test_edit_replacing_status_with_confirmed_blocked(tmp_path):
    r = repo(tmp_path)
    d = r / "decisions/log/0002.md"
    d.write_text("---\nstatus: 제안\n---\n", encoding="utf-8")
    p = claude(d, tool="Edit")
    p["tool_input"].update(old_string="제안", new_string="확정")
    assert g.check_pre(p, r, "tracking/x", False)
    p["tool_input"].update(new_string="보류")
    assert g.check_pre(p, r, "tracking/x", False) is None


def test_quoted_confirmed_status_blocked(tmp_path):
    r = repo(tmp_path)
    p = claude(r / "decisions/log/0004.md", '---\nstatus: "확정"\n---\n')
    assert g.check_pre(p, r, "tracking/x", False)


def test_post_flags_confirmed_decision(tmp_path):
    r = repo(tmp_path)
    d = r / "decisions/log/0005.md"
    d.write_text("---\nstatus: 확정\n---\n", encoding="utf-8")
    assert g.check_post(claude(d, tool="Edit"), r, False)
    assert g.check_post(claude(d, tool="Edit"), r, True)
    d.write_text("---\nstatus: 제안\n---\n", encoding="utf-8")
    assert g.check_post(claude(d, tool="Edit"), r, False) is None


def test_branch_during_rebase_in_worktree(tmp_path):
    env = {
        "GIT_AUTHOR_NAME": "a",
        "GIT_AUTHOR_EMAIL": "a@a",
        "GIT_COMMITTER_NAME": "a",
        "GIT_COMMITTER_EMAIL": "a@a",
        "PATH": "/usr/bin:/bin",
    }
    main = tmp_path / "main"
    subprocess.run(["git", "init", "-q", "-b", "main", str(main)], check=True)
    subprocess.run(
        ["git", "-C", str(main), "commit", "-q", "--allow-empty", "-m", "x"], check=True, env=env
    )
    wt = tmp_path / "wt"
    subprocess.run(
        ["git", "-C", str(main), "worktree", "add", "-q", "--detach", str(wt)], check=True
    )
    gd = subprocess.run(
        ["git", "-C", str(wt), "rev-parse", "--absolute-git-dir"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    (Path(gd) / "rebase-merge").mkdir()
    (Path(gd) / "rebase-merge" / "head-name").write_text("refs/heads/tracking/kalman\n")
    assert g.current_branch(wt) == "tracking/kalman"


def test_cli_fails_open_on_malformed_payload(tmp_path):
    for bad in ("[]", '{"cwd": 5}', '"x"'):
        res = subprocess.run(
            [sys.executable, str(ROOT / "tools/guard/check_edit.py"), "pre"],
            input=bad,
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, bad


def test_codex_move_into_actions_requires_spec(tmp_path):
    r = repo(tmp_path)
    patch = (
        "*** Begin Patch\n*** Update File: pipeline.py\n*** Move to: actions/smooth_tracks.py\n"
        "@@\n+b\n*** End Patch\n"
    )
    msg = g.check_pre(codex(r / "modules/tracking", patch), r, "tracking/x", False)
    assert msg and "smooth_tracks" in msg
