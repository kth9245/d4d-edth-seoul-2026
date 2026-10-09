"""new_action.py and the task ledger (decisions 0013, 0019)."""

import subprocess
import sys

from tests.ledger_fixtures import clone, make_repo, remote_file, seed
from tests.test_new_action import SCRIPT, make_module

LINKED = {
    "at": "2026-10-10T12:00:00+09:00",
    "by": "kth9245",
    "op": "add",
    "id": "Part2-1",
    "title": "tracking predict_tracks",
    "parent": None,
    "assign": "최동호",
    "slot": "1",
    "spec": "TRK-01",
}


def planned_repo(tmp_path, root_sub=""):
    remote, work = make_repo(tmp_path, "최동호")
    root = work / root_sub if root_sub else work
    mod = make_module(root)
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "tracking",
            "predict_tracks",
            "x",
            "--planned",
            "--root",
            str(root),
            "--owner",
            "최동호",
        ],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    seed(work, [LINKED])
    return remote, work, root, mod


def claim(root, owner, *extra):
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "tracking",
            "predict_tracks",
            "x",
            *extra,
            "--root",
            str(root),
            "--owner",
            owner,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_claim_starts_linked_plan_item(tmp_path):
    remote, _, root, mod = planned_repo(tmp_path)
    r = claim(root, "최동호")
    assert r.returncode == 0, r.stderr
    assert "Part2-1 시작" in r.stdout
    last = remote_file(remote, "tasks/log.jsonl").splitlines()[-1]
    assert '"op": "start"' in last and '"by": "최동호"' in last
    assert (mod / "actions" / "predict_tracks.py").exists()


def test_claim_refused_when_someone_else_started_the_item(tmp_path):
    from tools.ledger import write

    remote, _, root, mod = planned_repo(tmp_path)
    write(clone(tmp_path, remote, "mate", "황승주"), "start", "Part2-1", "황승주")
    before = (mod / "SPEC.md").read_text(encoding="utf-8")
    r = claim(root, "최동호")
    assert r.returncode == 1 and "황승주" in r.stderr
    assert (mod / "SPEC.md").read_text(encoding="utf-8") == before
    assert not (mod / "actions" / "predict_tracks.py").exists()


def test_claim_skips_ledger_when_root_is_not_repo_top(tmp_path):
    remote, _, root, mod = planned_repo(tmp_path, root_sub="inner")
    r = claim(root, "최동호")
    assert r.returncode == 0, r.stderr
    assert "경고: 할 일 기록 못 올림" in r.stderr
    assert len(remote_file(remote, "tasks/log.jsonl").splitlines()) == 1


def test_claim_warns_and_continues_when_ledger_log_is_broken(tmp_path):
    from tools.gitpush import push_tasks

    _, work, root, mod = planned_repo(tmp_path)
    push_tasks(work, lambda old: (old + "{oops\n", "n\n", "task: break"))
    r = claim(root, "최동호")
    assert r.returncode == 0, r.stderr
    assert "기록 파일 오류" in r.stderr and "Traceback" not in r.stderr
    assert (mod / "actions" / "predict_tracks.py").exists()


def test_claim_of_someone_elses_assignment_prints_a_chat_note(tmp_path):
    _, work = make_repo(tmp_path, "최동호")
    mod = make_module(work)
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "tracking",
            "predict_tracks",
            "x",
            "--planned",
            "--root",
            str(work),
            "--owner",
            "황승주",
        ],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    seed(work, [{**LINKED, "assign": "황승주"}])
    r = claim(work, "최동호")
    assert r.returncode == 0, r.stderr
    assert "Part2-1 시작" in r.stdout and "배정: 황승주 — 채팅에 알리세요" in r.stdout
    assert (mod / "actions" / "predict_tracks.py").exists()
