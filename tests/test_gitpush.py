import subprocess

import pytest

from tests.ledger_fixtures import clone, make_repo, remote_file, sh
from tools.gitpush import (
    LOG,
    OfflineError,
    changed_paths,
    commit_files,
    fetch,
    fetch_age_min,
    push_tasks,
    read_remote_file,
)
from tools.tasks import Refused


def test_push_changes_only_tasks_files_and_leaves_checkout_alone(tmp_path):
    remote, work = make_repo(tmp_path)
    (work / "README.md").write_text("dirty\n")
    (work / "new.txt").write_text("untracked\n")
    head, status = sh(work, "rev-parse", "HEAD"), sh(work, "status", "--porcelain")
    sha = push_tasks(work, lambda old: (old + "a\n", "now\n", "task: x"))
    assert sh(work, "rev-parse", "HEAD") == head
    assert sh(work, "status", "--porcelain") == status
    assert sh(remote, "rev-parse", "main").strip() == sha
    assert remote_file(remote, "tasks/log.jsonl") == "a\n"
    assert remote_file(remote, "tasks/NOW.md") == "now\n"
    assert changed_paths(work, sha + "~1", sha) == {"tasks/log.jsonl", "tasks/NOW.md"}
    assert "task: x" in sh(remote, "log", "-1", "--format=%s", "main")


def test_retry_rebuilds_from_the_newer_remote_log(tmp_path):
    remote, work = make_repo(tmp_path)
    mate = clone(tmp_path, remote, "mate", "황승주")
    seen = []

    def build(old):
        seen.append(old)
        if len(seen) == 1:  # a teammate pushes between our fetch and our push
            push_tasks(mate, lambda o: (o + "mate\n", "n\n", "task: mate"))
        return old + "me\n", "n\n", "task: me"

    push_tasks(work, build)
    assert seen == ["", "mate\n"]
    assert remote_file(remote, "tasks/log.jsonl") == "mate\nme\n"


def test_offline_raises_and_pushes_nothing(tmp_path):
    remote, work = make_repo(tmp_path)
    sh(work, "remote", "set-url", "origin", str(tmp_path / "nowhere.git"))
    with pytest.raises(OfflineError):
        push_tasks(work, lambda old: (old + "a\n", "n\n", "task: x"))
    assert remote_file(remote, "tasks/log.jsonl") == ""


def test_refusal_inside_build_pushes_nothing(tmp_path):
    remote, work = make_repo(tmp_path)

    def build(old):
        raise Refused("no")

    with pytest.raises(Refused):
        push_tasks(work, build)
    assert remote_file(remote, "tasks/log.jsonl") == ""


def test_changed_paths_sees_files_outside_tasks(tmp_path):
    _, work = make_repo(tmp_path)
    assert fetch(work)
    base = sh(work, "rev-parse", "origin/main").strip()
    sha = commit_files(work, base, {"tasks/log.jsonl": "a\n", "README.md": "x\n"}, "m")
    assert changed_paths(work, base, sha) == {"tasks/log.jsonl", "README.md"}


def test_fetch_age_after_fetch_is_zero(tmp_path):
    _, work = make_repo(tmp_path)
    assert fetch(work)
    assert fetch_age_min(work) == 0


def test_push_that_landed_but_reported_failure_is_not_repeated(tmp_path, monkeypatch):
    remote, work = make_repo(tmp_path)
    real = subprocess.run

    def lossy(args, **kw):  # the server takes the push, the client sees a dropped connection
        r = real(args, **kw)
        if list(args[:2]) == ["git", "push"]:
            return subprocess.CompletedProcess(args, 1, "", "connection reset")
        return r

    monkeypatch.setattr(subprocess, "run", lossy)
    calls = []

    def build(old):
        calls.append(old)
        return old + "a\n", "n\n", "task: x"

    push_tasks(work, build)
    assert calls == [""]
    assert remote_file(remote, LOG) == "a\n"


def test_read_remote_file_raises_on_git_errors_but_not_on_missing_path(tmp_path):
    _, work = make_repo(tmp_path)
    assert fetch(work)
    assert read_remote_file(work, LOG) == ""
    with pytest.raises(subprocess.CalledProcessError):
        read_remote_file(work, LOG, "no-such-ref")
