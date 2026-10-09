import json
from pathlib import Path

from contracts.models import Frame, Play, Scenario

ROOT = Path(__file__).resolve().parent.parent
SCENARIO = ROOT / "demo" / "scenarios" / "baengnyeong_night.json"
PLAYS = ROOT / "demo" / "plays"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_scenario_validates_and_has_a_start_time():
    sc = Scenario.model_validate(_load(SCENARIO))
    assert sc.operation.started_ms is not None
    assert set(sc.operation.assign.values()) <= {p.id for p in sc.plays}


def test_play_files_match_the_scenario_plays():
    sc = Scenario.model_validate(_load(SCENARIO))
    files = {p.stem: Play.model_validate(_load(p)) for p in PLAYS.glob("*.json")}
    assert files == {p.id: p for p in sc.plays}


def test_fast_boat_tracking_lets_the_operator_pick_the_target():
    sc = Scenario.model_validate(_load(SCENARIO))
    track = next(p for p in sc.plays if p.id == "track_fast")
    assert track.steps[0].do.params["target"] == "operator"


def test_switch_scene_shows_the_target_select_card():
    s5 = Frame.model_validate(_load(ROOT / "contracts/examples/frames/s5_zone_block.json"))
    picks = [r for r in s5.reports if r.kind == "target_select"]
    assert picks and picks[0].decision_id == "dec-2"


def test_split_event_makes_a_fast_boat():
    sc = Scenario.model_validate(_load(SCENARIO))
    split = next(e for e in sc.events if e.kind == "split_target")
    assert split.params["kind"] == "fast_boat"
