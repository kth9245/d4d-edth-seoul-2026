import os
import subprocess
import sys
from pathlib import Path

from shared.kst import now_kst
from tools.frontmatter import parse

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "decide.py"


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--root", str(root)], capture_output=True, text=True
    )


def test_new_creates_numbered_proposal(tmp_path):
    (tmp_path / "decisions" / "log").mkdir(parents=True)
    r = run(tmp_path, "new", "추적은 Kalman filter", "--modules", "tracking,assess")
    assert r.returncode == 0, r.stderr
    files = list((tmp_path / "decisions" / "log").glob("*.md"))
    assert [f.name for f in files] == ["0001-추적은-kalman-filter.md"]
    meta, body = parse(files[0].read_text(encoding="utf-8"))
    assert meta["status"] == "제안" and meta["decided_by"] is None
    assert meta["modules"] == ["tracking", "assess"]
    for h in ("## 결정", "## 이유", "## 버린 대안", "## 영향"):
        assert h in body
    assert run(tmp_path, "new", "두번째").returncode == 0
    assert (tmp_path / "decisions" / "log" / "0002-두번째.md").exists()


def test_accept_sets_status_owner_and_date(tmp_path):
    (tmp_path / "decisions" / "log").mkdir(parents=True)
    run(tmp_path, "new", "WGS84")
    r = run(tmp_path, "accept", "0001", "--by", "영희")
    assert r.returncode == 0, r.stderr
    meta, _ = parse((tmp_path / "decisions" / "log" / "0001-wgs84.md").read_text(encoding="utf-8"))
    assert meta["status"] == "확정"
    assert meta["decided_by"] == "영희"
    assert meta["date"] == now_kst().date().isoformat()


def test_accept_unknown_id_fails(tmp_path):
    (tmp_path / "decisions" / "log").mkdir(parents=True)
    r = run(tmp_path, "accept", "0042", "--by", "영희")
    assert r.returncode == 1
    assert "0042" in r.stderr


def test_dates_are_kst_whatever_the_machine_timezone(tmp_path):
    # UTC-12 differs from KST during 00:00-20:59 KST and UTC+14 during 19:00-23:59 KST,
    # so at any moment at least one of the two runs catches a machine-local date.
    (tmp_path / "decisions" / "log").mkdir(parents=True)
    for i, tz in enumerate(("Etc/GMT+12", "Etc/GMT-14"), 1):
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "new", f"t{i}", "--root", str(tmp_path)],
            env={**os.environ, "TZ": tz},
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, r.stderr
        p = next((tmp_path / "decisions" / "log").glob(f"{i:04d}-*.md"))
        meta, _ = parse(p.read_text(encoding="utf-8"))
        assert meta["date"] == now_kst().date().isoformat(), tz
