"""Bare remote + clone repos for task ledger tests (no test_ prefix: not collected)."""

import subprocess
from pathlib import Path


def sh(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout


def config(repo: Path, name: str) -> None:
    sh(repo, "config", "user.name", name)
    sh(repo, "config", "user.email", "t@t")


def make_repo(tmp: Path, name: str = "kth9245") -> tuple[Path, Path]:
    remote, work = tmp / "remote.git", tmp / "work"
    sh(tmp, "init", "-q", "--bare", "-b", "main", str(remote))
    work.mkdir()
    sh(work, "init", "-q", "-b", "main")
    config(work, name)
    (work / "README.md").write_text("r\n")
    sh(work, "add", "-A")
    sh(work, "commit", "-qm", "base")
    sh(work, "remote", "add", "origin", str(remote))
    sh(work, "push", "-q", "-u", "origin", "main")
    return remote, work


def clone(tmp: Path, remote: Path, dirname: str, name: str) -> Path:
    d = tmp / dirname
    sh(tmp, "clone", "-q", str(remote), str(d))
    config(d, name)
    return d


def remote_file(remote: Path, path: str) -> str:
    r = subprocess.run(
        ["git", "show", f"main:{path}"],
        cwd=remote,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return r.stdout if r.returncode == 0 else ""


def seed(work: Path, events: list[dict]) -> None:
    """Put a log on origin/main through the real push path."""
    from tools.gitpush import push_tasks
    from tools.tasks import dump_event

    text = "".join(dump_event(e) + "\n" for e in events)
    push_tasks(work, lambda old: (text, "now\n", "task: seed"))
