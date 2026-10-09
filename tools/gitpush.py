"""Commit tasks/ files straight onto origin/main and push (decision 0013). Stdlib only.

The commit is built with git plumbing on a temporary index, so the work tree, the real
index, HEAD and local branches are never touched. Only LOG and NOW may change; anything
else aborts before the push.
"""

import os
import subprocess
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

LOG, NOW = "tasks/log.jsonl", "tasks/NOW.md"
ALLOWED = {LOG, NOW}


class OfflineError(Exception):
    """origin is unreachable or missing."""


class PushFailed(Exception):
    """origin kept rejecting the push."""


def _git(root: Path, *args: str, stdin: str | None = None, env: dict | None = None) -> str:
    r = subprocess.run(
        ["git", *args],
        cwd=root,
        input=stdin,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if r.returncode != 0:
        raise subprocess.CalledProcessError(r.returncode, ["git", *args], r.stdout, r.stderr)
    return r.stdout


def fetch(root: Path) -> bool:
    r = subprocess.run(["git", "fetch", "-q", "origin", "main"], cwd=root, capture_output=True)
    return r.returncode == 0


def read_remote_file(root: Path, path: str, rev: str = "origin/main") -> str:
    """'' only when `path` is absent at `rev`; any other git error raises, so a failed read
    can never be mistaken for an empty log (the next write would replace the whole board)."""
    if not _git(root, "ls-tree", "--name-only", rev, "--", path).strip():
        return ""
    return _git(root, "show", f"{rev}:{path}")


def fetch_age_min(root: Path) -> int | None:
    """Minutes since the last fetch (FETCH_HEAD mtime); None if never fetched."""
    p = Path(_git(root, "rev-parse", "--git-path", "FETCH_HEAD").strip())
    p = p if p.is_absolute() else root / p
    return int((time.time() - p.stat().st_mtime) // 60) if p.exists() else None


def commit_files(root: Path, base: str, files: dict[str, str], message: str) -> str:
    """A commit whose tree is base's tree with `files` replaced. Not pushed."""
    with tempfile.TemporaryDirectory() as d:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(d) / "index")}
        _git(root, "read-tree", base, env=env)
        for path, text in files.items():
            blob = _git(root, "hash-object", "-w", "--stdin", stdin=text).strip()
            _git(root, "update-index", "--add", "--cacheinfo", f"100644,{blob},{path}", env=env)
        tree = _git(root, "write-tree", env=env).strip()
    return _git(root, "commit-tree", tree, "-p", base, "-m", message).strip()


def changed_paths(root: Path, base: str, sha: str) -> set[str]:
    return set(_git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", base, sha).split())


def _landed(root: Path, sha: str, base: str) -> bool:
    r = subprocess.run(
        ["git", "merge-base", "--is-ancestor", sha, base], cwd=root, capture_output=True
    )
    return r.returncode == 0


def push_tasks(root: Path, build: Callable[[str], tuple[str, str, str]], retries: int = 5) -> str:
    """build(old_log) -> (new_log, now_md, message). Called again with the fresh remote log
    after every rejected push, so validation and numbering always see the newest state."""
    last, sha = "", ""
    for _ in range(retries):
        if not fetch(root):
            raise OfflineError("origin에 연결할 수 없음")
        base = _git(root, "rev-parse", "origin/main").strip()
        if sha and _landed(root, sha, base):  # the server took it although the client saw an error
            return sha
        new_log, now_md, message = build(read_remote_file(root, LOG, base))
        sha = commit_files(root, base, {LOG: new_log, NOW: now_md}, message)
        extra = changed_paths(root, base, sha) - ALLOWED
        if extra:
            raise RuntimeError(f"tasks/ 밖 파일이 바뀜: {sorted(extra)}")
        r = subprocess.run(
            ["git", "push", "-q", "origin", f"{sha}:refs/heads/main"],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if r.returncode == 0:
            return sha
        last = r.stderr.strip()
    raise PushFailed(f"push가 {retries}번 거절됨: {last}")
