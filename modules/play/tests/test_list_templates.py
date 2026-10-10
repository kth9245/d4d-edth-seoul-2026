import json
from pathlib import Path

from contracts.models import Play
from modules.play.actions.list_templates import list_templates

PLAYS = Path(__file__).resolve().parents[3] / "demo" / "plays"


def test_returns_only_template_plays_in_file_order():
    files = sorted(PLAYS.glob("*.json"))
    expected = [p.stem for p in files if json.loads(p.read_text(encoding="utf-8")).get("template")]
    plays = list_templates()
    assert all(isinstance(p, Play) and p.template for p in plays)
    assert [p.id for p in plays] == expected


def test_demo_templates_include_watch_and_exclude_patrols():
    ids = {p.id for p in list_templates()}
    assert {"watch", "go_home", "track_fast"} <= ids
    assert not ids & {"patrol_a", "patrol_b", "landing"}
