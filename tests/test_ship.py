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
