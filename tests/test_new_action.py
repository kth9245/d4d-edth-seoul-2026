import subprocess
import sys
from pathlib import Path

from tests.ledger_fixtures import clone, make_repo, remote_file, seed

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "new_action.py"

SPEC = (
    "<!-- prefix: TRK -->\n# tracking SPEC\n\n"
    "| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |\n|---|---|---|---|---|---|---|\n"
)


def make_module(root: Path) -> Path:
    mod = root / "modules" / "tracking"
    (mod / "actions").mkdir(parents=True)
    (mod / "tests").mkdir()
    (mod / "__init__.py").write_text("")
    (mod / "SPEC.md").write_text(SPEC, encoding="utf-8")
    return mod


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--root", str(root), "--owner", "철수"],
        capture_output=True,
        text=True,
    )


def test_creates_spec_row_action_and_failing_test(tmp_path):
    mod = make_module(tmp_path)
    r = run(tmp_path, "tracking", "predict_tracks", "1초 뒤 위치 예측")
    assert r.returncode == 0, r.stderr
    action = (mod / "actions" / "predict_tracks.py").read_text(encoding="utf-8")
    assert action.startswith(
        '"""TRK-01 predict_tracks: 1초 뒤 위치 예측\nSPEC: modules/tracking/SPEC.md#TRK-01'
    )
    assert "def predict_tracks(" in action and "raise NotImplementedError" in action
    test = (mod / "tests" / "test_predict_tracks.py").read_text(encoding="utf-8")
    assert "from modules.tracking.actions.predict_tracks import predict_tracks" in test
    assert "| TRK-01 | predict_tracks |" in (mod / "SPEC.md").read_text(encoding="utf-8")
    assert (mod / "actions" / "__init__.py").exists()
    assert (mod / "tests" / "__init__.py").exists()


def test_rejects_bad_name(tmp_path):
    make_module(tmp_path)
    r = run(tmp_path, "tracking", "PredictTracks", "x")
    assert r.returncode == 1
    assert "verb_noun" in r.stderr


def test_rejects_existing_action(tmp_path):
    make_module(tmp_path)
    assert run(tmp_path, "tracking", "predict_tracks", "x").returncode == 0
    r = run(tmp_path, "tracking", "predict_tracks", "x")
    assert r.returncode == 1
    assert "이미" in r.stderr


def test_rejects_unknown_module(tmp_path):
    make_module(tmp_path)
    r = run(tmp_path, "nosuch", "do_thing", "x")
    assert r.returncode == 1
    assert "모듈" in r.stderr


def test_planned_row_has_no_files_and_is_claimed_by_plain_run(tmp_path):
    mod = make_module(tmp_path)
    r = run(
        tmp_path, "tracking", "predict_tracks", "x", "--planned", "--inputs", "a", "--done", "c"
    )
    assert r.returncode == 0, r.stderr
    assert "| TRK-01 | predict_tracks | a |  | c | 철수 | 예정 |" in (mod / "SPEC.md").read_text()
    assert not (mod / "actions" / "predict_tracks.py").exists()
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "tracking",
            "predict_tracks",
            "x",
            "--root",
            str(tmp_path),
            "--owner",
            "영희",
        ],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    spec = (mod / "SPEC.md").read_text()
    assert (
        "| TRK-01 | predict_tracks | a |  | c | 영희 | 진행중 |" in spec
        and spec.count("TRK-01") == 1
    )
    assert (mod / "actions" / "predict_tracks.py").exists()
    assert (mod / "tests" / "test_predict_tracks.py").exists()


def test_take_rewrites_owner_of_started_row(tmp_path):
    mod = make_module(tmp_path)
    assert run(tmp_path, "tracking", "predict_tracks", "x").returncode == 0
    r = run(tmp_path, "tracking", "predict_tracks", "x")
    assert r.returncode == 1 and "--take" in r.stderr
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "tracking",
            "predict_tracks",
            "x",
            "--take",
            "--root",
            str(tmp_path),
            "--owner",
            "영희",
        ],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    assert "| TRK-01 | predict_tracks |  |  |  | 영희 | 진행중 |" in (mod / "SPEC.md").read_text()


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
