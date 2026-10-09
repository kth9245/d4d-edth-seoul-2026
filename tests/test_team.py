import subprocess
import sys

from tests.test_new_action import SCRIPT, make_module
from tools.tasks import person_of


def test_git_names_map_to_team_members():
    assert person_of("Paleshift") == "황승주"
    assert person_of("blackchoi0624") == "최동호"
    assert person_of("kth9245") == "kth9245"
    assert person_of(" 황승주 ") == "황승주"
    assert person_of("dongho") == "dongho"


def test_new_action_owner_is_the_member_behind_the_git_name(tmp_path):
    mod = make_module(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Paleshift"], cwd=tmp_path, check=True)
    cmd = [sys.executable, str(SCRIPT), "tracking", "predict_tracks", "x", "--planned"]
    r = subprocess.run(
        [*cmd, "--root", str(tmp_path)], cwd=tmp_path, capture_output=True, text=True
    )
    assert r.returncode == 0, r.stderr
    assert "| 황승주 | 예정 |" in (mod / "SPEC.md").read_text(encoding="utf-8")
