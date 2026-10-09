import subprocess
import sys
from pathlib import Path

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
