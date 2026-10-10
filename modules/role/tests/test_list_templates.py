import json
from pathlib import Path

from contracts.models import Role
from modules.role.actions.list_templates import list_templates

ROLES = Path(__file__).resolve().parents[3] / "demo" / "roles"


def test_returns_only_template_roles_in_file_order():
    files = sorted(ROLES.glob("*.json"))
    expected = [p.stem for p in files if json.loads(p.read_text(encoding="utf-8")).get("template")]
    roles = list_templates()
    assert all(isinstance(p, Role) and p.template for p in roles)
    assert [p.id for p in roles] == expected


def test_demo_templates_include_watch_and_exclude_patrols():
    ids = {p.id for p in list_templates()}
    assert {"watch", "go_home", "track_fast"} <= ids
    assert not ids & {"patrol_a", "patrol_b", "landing"}
