import subprocess
import sys
from pathlib import Path

from tests.ledger_fixtures import clone, make_repo, remote_file, seed, sh
from tools.gitpush import push_tasks

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "task.py"
ITEM = {
    "at": "2026-10-10T12:00:00+09:00",
    "by": "kth9245",
    "op": "add",
    "id": "Part2-17",
    "title": "틱 루프",
    "parent": None,
    "assign": "최동호",
    "slot": "1",
    "spec": "SIM-08",
}


def task(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def setup(tmp_path, name="최동호"):
    remote, work = make_repo(tmp_path, name)
    seed(work, [ITEM])
    return remote, work


def last_event(remote) -> str:
    return remote_file(remote, "tasks/log.jsonl").splitlines()[-1]


def test_start_pushes_and_leaves_checkout_alone(tmp_path):
    remote, work = setup(tmp_path)
    (work / "README.md").write_text("dirty\n")
    head, status = sh(work, "rev-parse", "HEAD"), sh(work, "status", "--porcelain")
    r = task(work, "start", "2-17")
    assert r.returncode == 0, r.stderr
    assert "Part2-17 시작: 최동호" in r.stdout and "KST (main " in r.stdout
    assert '"op": "start"' in last_event(remote) and '"by": "최동호"' in last_event(remote)
    assert "- **Part2-17** 틱 루프 — 최동호" in remote_file(remote, "tasks/NOW.md")
    assert (sh(work, "rev-parse", "HEAD"), sh(work, "status", "--porcelain")) == (head, status)


def test_second_person_is_refused_until_take(tmp_path):
    remote, work = setup(tmp_path)
    mate = clone(tmp_path, remote, "mate", "황승주")
    assert task(work, "start", "2-17").returncode == 0
    r = task(mate, "start", "2-17")
    assert r.returncode == 1 and "최동호" in r.stderr and "--take" in r.stderr
    r = task(mate, "start", "2-17", "--take")
    assert r.returncode == 0, r.stderr
    assert '"from": "최동호"' in last_event(remote)


def test_start_of_someone_elses_assignment_warns(tmp_path):
    remote, _ = setup(tmp_path)
    mate = clone(tmp_path, remote, "mate", "황승주")
    r = task(mate, "start", "2-17")
    assert r.returncode == 0 and "배정: 최동호" in r.stdout


def test_name_outside_team_refused(tmp_path):
    remote, work = setup(tmp_path, name="철수")
    r = task(work, "start", "2-17")
    assert r.returncode == 1 and "git config user.name" in r.stderr
    assert len(remote_file(remote, "tasks/log.jsonl").splitlines()) == 1


def test_offline_fails_without_writing(tmp_path):
    remote, work = setup(tmp_path)
    sh(work, "remote", "set-url", "origin", str(tmp_path / "nowhere.git"))
    r = task(work, "start", "2-17")
    assert r.returncode == 1 and "기록 못 올림" in r.stderr
    assert len(remote_file(remote, "tasks/log.jsonl").splitlines()) == 1


def test_add_and_done_rules(tmp_path):
    _, work = setup(tmp_path)
    r = task(work, "add", "2-17", "스텁 Frame")
    assert r.returncode == 0 and "Part2-17.1 스텁 Frame 추가" in r.stdout
    assert task(work, "start", "2-17").returncode == 0
    r = task(work, "done", "2-17")
    assert r.returncode == 1 and "Part2-17.1" in r.stderr
    assert task(work, "done", "2-17.1").returncode == 0
    assert task(work, "done", "2-17").returncode == 0


def test_show_from_subdirectory(tmp_path):
    _, work = setup(tmp_path)
    (work / "sub").mkdir()
    assert task(work, "start", "2-17").returncode == 0
    assert task(work, "note", "2-17", "스텁 목록은 engine.py 머리").returncode == 0
    assert task(work, "decide", "2-17", "스텁은 예시 JSON").returncode == 0
    out = task(work / "sub", "show").stdout
    assert "진행중" in out and "**Part2-17**" in out and "스텁은 예시 JSON" in out
    assert "메모: 스텁 목록은 engine.py 머리" in task(work / "sub", "show", "2-17").stdout
    assert "# 지금 작업판" in task(work / "sub", "show", "--all").stdout


def test_seed_only_once(tmp_path):
    _, work = setup(tmp_path)
    f = tmp_path / "seed.jsonl"
    f.write_text(
        '{"at": "2026-10-10T12:00:00+09:00", "by": "kth9245", "op": "add", '
        '"id": "Part1-1", "title": "x", "parent": null, "assign": null, '
        '"slot": null, "spec": null}\n',
        encoding="utf-8",
    )
    r = task(work, "seed", str(f))
    assert r.returncode == 1 and "이미 기록" in r.stderr


def test_seed_pushes_log_and_board(tmp_path):
    remote, work = make_repo(tmp_path)
    f = tmp_path / "seed.jsonl"
    f.write_text(
        '{"at": "2026-10-10T12:00:00+09:00", "by": "kth9245", "op": "add", '
        '"id": "Part1-1", "title": "계약", "parent": null, "assign": "kth9245", '
        '"slot": "밤", "spec": null}\n',
        encoding="utf-8",
    )
    r = task(work, "seed", str(f))
    assert r.returncode == 0 and "항목 1개" in r.stdout
    assert "### kth9245" in remote_file(remote, "tasks/NOW.md")


def test_corrupt_log_is_reported_not_traceback(tmp_path):
    _, work = setup(tmp_path)
    push_tasks(work, lambda old: (old + "{oops\n", "n\n", "task: break"))
    r = task(work, "show")
    assert r.returncode == 1 and "2번째 줄" in r.stderr and "Traceback" not in r.stderr
