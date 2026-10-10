"""scripts/qa: the screen QA checklists are valid without a browser (run.mjs --check).

A misspelled step key would do nothing and still pass, so --check rejects unknown keys and steps that do nothing.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "scripts" / "qa" / "run.mjs"
CHECKLISTS = sorted((ROOT / "scripts" / "qa").glob("*.json"))
pytestmark = pytest.mark.skipif(
    shutil.which("node") is None, reason="node가 없음 (cop-ui 설치 필요)"
)


def _check(*files: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["node", str(RUN), "--check", *map(str, files)], capture_output=True, text=True, timeout=30
    )


def test_repo_checklists_exist_and_pass_the_check():
    assert {p.name for p in CHECKLISTS} >= {
        "editor.json",
        "draft_to_live.json",
        "live.json",
        "scenes.json",
    }
    r = _check(*CHECKLISTS)
    assert r.returncode == 0, r.stdout + r.stderr


def test_a_misspelled_step_key_is_rejected(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps([{"nav": "/#live"}, {"clik": "재생"}]), encoding="utf-8")
    r = _check(bad)
    assert r.returncode == 1
    assert "clik" in r.stdout


def test_a_step_that_does_nothing_is_rejected(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps([{"label": "no action, no read"}]), encoding="utf-8")
    r = _check(bad)
    assert r.returncode == 1
    assert "step 1" in r.stdout
