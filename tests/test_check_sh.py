import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.hooksPath=/dev/null"]


def make_repo(tmp_path: Path) -> Path:
    work = tmp_path / "w"
    work.mkdir()
    for d in ("scripts", "tools", "contracts"):
        shutil.copytree(ROOT / d, work / d, ignore=shutil.ignore_patterns("__pycache__"))
    (work / "modules").mkdir()
    (work / ".venv").symlink_to(ROOT / ".venv")
    subprocess.run([*GIT, "init", "-q", "-b", "main"], cwd=work, check=True)
    return work


def check(work: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", "scripts/check.sh", *args], cwd=work, capture_output=True, text=True
    )


def stage(work: Path, rel: str, text: str) -> None:
    p = work / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    subprocess.run([*GIT, "add", rel], cwd=work, check=True)


def test_secret_in_staged_diff_blocks_commit(tmp_path):
    work = make_repo(tmp_path)
    stage(work, "notes.txt", "key = " + "AKIA" + "ABCDEFGHIJKLMNOP" + "\n")
    r = check(work)
    assert r.returncode == 1 and "비밀" in r.stderr


def test_private_key_header_and_sk_token_blocked(tmp_path):
    work = make_repo(tmp_path)
    stage(work, "a.txt", "-----BEGIN " + "RSA PRIVATE KEY-----\n")
    assert check(work).returncode == 1
    subprocess.run([*GIT, "reset", "-q"], cwd=work, check=True)
    stage(work, "b.txt", "t = sk-" + "a" * 24 + "\n")
    assert check(work).returncode == 1


def test_clean_commit_passes_and_foreign_violation_ignored(tmp_path):
    work = make_repo(tmp_path)
    (work / "modules/gateway").mkdir(parents=True)
    (work / "modules/gateway/bad.py").write_text("from modules.tracking.actions.a import a\n")
    stage(work, "modules/assess/ok.py", "x = 1\n")
    r = check(work)
    assert r.returncode == 0, r.stdout + r.stderr
    assert check(work, "--all").returncode != 0
