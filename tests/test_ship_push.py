"""ship.sh push step: retry over task records, show git's reason, sync .venv."""

import os
from pathlib import Path

from tests.test_ship import git, make_clone, run_ship


def _push_mid_ship(work: Path, mate: Path, path: str) -> None:
    """Replace the clone's smoke step with a push of `path` from `mate`: a push landing mid-ship."""
    git(work, "update-index", "--skip-worktree", "scripts/smoke.py")
    (work / "scripts/smoke.py").write_text(
        "import pathlib, subprocess\n"
        f"m = pathlib.Path({str(mate)!r})\n"
        f"p = m / {path!r}\n"
        "p.parent.mkdir(parents=True, exist_ok=True)\n"
        "p.write_text('x\\n')\n"
        "g = ['git', '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'core.hooksPath=/dev/null']\n"
        f"subprocess.run(g + ['add', {path!r}], cwd=m, check=True)\n"
        "subprocess.run(g + ['commit', '-qm', 'mid-ship'], cwd=m, check=True)\n"
        "subprocess.run(g + ['push', '-q', 'origin', 'HEAD:main'], cwd=m, check=True)\n"
    )


def _ship_with_mid_push(tmp_path, path):
    remote, work = make_clone(tmp_path)
    mate = tmp_path / "mate"
    git(tmp_path, "clone", "-q", str(remote), str(mate))
    _push_mid_ship(work, mate, path)
    (work / "knowledge/inbox/mine.md").write_text("x\n")
    git(work, "add", "knowledge/inbox/mine.md")
    git(work, "commit", "-q", "-m", "mine note")
    return work, run_ship(work)


def test_ship_retries_when_only_task_records_landed_mid_ship(tmp_path):
    work, r = _ship_with_mid_push(tmp_path, "tasks/log.jsonl")
    assert r.returncode == 0, r.stdout + r.stderr
    log = git(work, "log", "--oneline", "origin/main")
    assert "mine note" in log and "mid-ship" in log


def test_ship_stops_when_other_files_landed_mid_ship(tmp_path):
    _, r = _ship_with_mid_push(tmp_path, "knowledge/inbox/mate.md")
    assert r.returncode == 1 and "push 실패" in r.stdout + r.stderr


def test_ship_shows_why_a_push_was_rejected_and_does_not_retry_it(tmp_path):
    remote, work = make_clone(tmp_path)
    count = tmp_path / "pushes"
    hook = remote / "hooks" / "pre-receive"
    hook.write_text(
        f"#!/bin/sh\necho x >> {count}\necho 'GH001: Large files detected' >&2\nexit 1\n"
    )
    hook.chmod(0o755)
    (work / "knowledge/inbox/mine.md").write_text("x\n")
    git(work, "add", "knowledge/inbox/mine.md")
    git(work, "commit", "-q", "-m", "mine note")
    r = run_ship(work)
    assert r.returncode == 1
    assert "GH001" in r.stdout + r.stderr
    assert count.read_text().count("x") == 1


def test_ship_syncs_the_venv_to_the_lock_before_testing(tmp_path):
    _, work = make_clone(tmp_path)
    bin_dir, calls = tmp_path / "bin", tmp_path / "uv-calls"
    bin_dir.mkdir()
    (bin_dir / "uv").write_text(f'#!/bin/sh\necho "$@" >> {calls}\n')
    (bin_dir / "uv").chmod(0o755)
    (work / "knowledge/inbox/mine.md").write_text("x\n")
    git(work, "add", "knowledge/inbox/mine.md")
    git(work, "commit", "-q", "-m", "mine note")
    r = run_ship(work, {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"})
    assert r.returncode == 0, r.stdout + r.stderr
    assert "sync -q --frozen --inexact" in calls.read_text()
