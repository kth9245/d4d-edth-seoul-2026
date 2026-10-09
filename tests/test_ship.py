import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_GIT = ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.hooksPath=/dev/null"]


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *ENV_GIT, *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


def make_clone(tmp_path: Path) -> tuple[Path, Path]:
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(remote))
    work = tmp_path / "work"
    shutil.copytree(
        ROOT,
        work,
        symlinks=True,
        ignore=shutil.ignore_patterns(
            ".git", "node_modules", "dist", ".venv", "*.pmtiles", ".tools", "__pycache__"
        ),
    )
    (work / ".venv").symlink_to(ROOT / ".venv")
    git(work, "init", "-q", "-b", "main")
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", "base")
    git(work, "remote", "add", "origin", str(remote))
    git(work, "push", "-q", "origin", "main")
    git(work, "switch", "-q", "-c", "tracking/work")
    return remote, work


def test_ship_pushes_rebased_branch_to_main(tmp_path):
    remote, work = make_clone(tmp_path)
    (work / "knowledge/inbox/note.md").write_text("x\n")
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", "note")
    r = subprocess.run(
        ["bash", "scripts/ship.sh"],
        cwd=work,
        capture_output=True,
        text=True,
        env={
            "PATH": "/usr/bin:/bin",
            "HOME": str(tmp_path),
            "GIT_CONFIG_PARAMETERS": "'core.hookspath=/dev/null'",
        },
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "note" in git(work, "log", "--oneline", "origin/main", "-1")


def test_ship_refuses_dirty_tree(tmp_path):
    _, work = make_clone(tmp_path)
    (work / "README.md").write_text("dirty\n")
    r = subprocess.run(["bash", "scripts/ship.sh"], cwd=work, capture_output=True, text=True)
    assert r.returncode == 1 and "커밋" in r.stdout + r.stderr


def test_ship_fails_on_broken_module_test(tmp_path):
    _, work = make_clone(tmp_path)
    t = work / "modules/tracking/tests/test_delete_stale_tracks.py"
    t.write_text(t.read_text() + "\n\ndef test_broken():\n    assert False\n")
    git(work, "commit", "-qam", "break")
    r = subprocess.run(["bash", "scripts/ship.sh"], cwd=work, capture_output=True, text=True)
    assert r.returncode == 1
    assert "test_broken" in r.stdout + r.stderr


def run_ship(work: Path, env: dict | None = None):
    return subprocess.run(
        ["bash", "scripts/ship.sh"], cwd=work, capture_output=True, text=True, env=env
    )


def test_gitignore_ignores_venv_symlink(tmp_path):
    repo = tmp_path / "r"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    shutil.copy(ROOT / ".gitignore", repo / ".gitignore")
    (repo / ".venv").symlink_to(tmp_path)
    r = subprocess.run(["git", "check-ignore", "-q", ".venv"], cwd=repo)
    assert r.returncode == 0


def test_ship_rebases_over_teammate_push(tmp_path):
    remote, work = make_clone(tmp_path)
    mate = tmp_path / "mate"
    git(tmp_path, "clone", "-q", str(remote), str(mate))
    (mate / "knowledge/inbox/mate.md").write_text("m\n")
    git(mate, "add", "-A")
    git(mate, "commit", "-q", "-m", "mate note")
    git(mate, "push", "-q", "origin", "main")
    (work / "knowledge/inbox/mine.md").write_text("x\n")
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", "mine note")
    r = run_ship(work)
    assert r.returncode == 0, r.stdout + r.stderr
    log = git(work, "log", "--oneline", "origin/main")
    assert "mine note" in log and "mate note" in log


def test_ship_reports_rebase_in_progress(tmp_path):
    _, work = make_clone(tmp_path)
    git_dir = Path(git(work, "rev-parse", "--git-path", "rebase-merge").strip())
    (work / git_dir).mkdir(parents=True, exist_ok=True)
    r = run_ship(work)
    assert r.returncode == 1 and "rebase 진행 중" in r.stdout + r.stderr


def test_ship_runs_tests_when_only_tests_dir_changed(tmp_path):
    _, work = make_clone(tmp_path)
    (work / "tests/test_zz_broken.py").write_text("def test_zz_broken():\n    assert False\n")
    git(work, "add", "-A")
    git(work, "commit", "-qm", "only tests")
    r = run_ship(work)
    assert r.returncode == 1 and "test_zz_broken" in r.stdout + r.stderr


def test_ship_freeze_downgrades_test_failure_to_warning(tmp_path):
    remote, work = make_clone(tmp_path)
    t = work / "modules/tracking/tests/test_delete_stale_tracks.py"
    t.write_text(t.read_text() + "\n\ndef test_broken():\n    assert False\n")
    git(work, "commit", "-qam", "break")
    env = {**os.environ, "KDTH_FREEZE": "1"}
    r = subprocess.run(
        ["bash", "scripts/ship.sh"], cwd=work, capture_output=True, text=True, env=env
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "경고" in r.stdout + r.stderr
    assert "break" in git(work, "log", "--oneline", "origin/main", "-1")


def test_ship_allows_module_with_spec_only_and_no_tests(tmp_path):
    _, work = make_clone(tmp_path)
    spec = work / "modules/play/SPEC.md"
    spec.write_text(
        spec.read_text(encoding="utf-8") + "| PLY-99 | do_nothing | - | - | - | t | 예정 |\n",
        encoding="utf-8",
    )
    git(work, "commit", "-qam", "spec only")
    r = run_ship(work)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "테스트가 없습니다" in r.stdout + r.stderr
