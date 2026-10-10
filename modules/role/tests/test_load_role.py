import json
from pathlib import Path

import pytest

from modules.role.actions.load_role import load_role

ROLES = Path(__file__).resolve().parents[3] / "demo" / "roles"


def test_loads_the_demo_templates():
    watch, patrol = load_role(ROLES / "watch.json"), load_role(str(ROLES / "patrol_a.json"))
    assert (watch.id, watch.entry, watch.template) == ("watch", "watch", True)
    assert patrol.id == "patrol_a" and len(patrol.steps) >= 1


def test_bad_value_names_the_file_and_field(tmp_path):
    data = json.loads((ROLES / "watch.json").read_text(encoding="utf-8"))
    data["steps"][0]["do"]["kind"] = "fly_away"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match=r"bad\.json(.|\n)*steps\.0\.do\.kind"):
        load_role(bad)


def test_broken_json_is_a_value_error(tmp_path):
    bad = tmp_path / "broken.json"
    bad.write_text('{"id": "x",', encoding="utf-8")
    with pytest.raises(ValueError, match="broken.json"):
        load_role(bad)
