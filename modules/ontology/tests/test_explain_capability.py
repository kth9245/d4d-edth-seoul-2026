from pathlib import Path

from contracts.models import ActionKind, Scenario
from modules.ontology.actions.explain_capability import explain_capability

DEMO = Path(__file__).resolve().parents[3] / "demo" / "scenarios" / "baengnyeong_night.json"
ONTO = Scenario.model_validate_json(DEMO.read_text(encoding="utf-8")).ontology


def test_recon_drone_watches_through_air_vehicle():
    r = explain_capability("recon_drone", ActionKind.watch_target, ONTO)
    assert (r.allowed, r.path, r.via) == (True, ["recon_drone", "air_vehicle"], "watch")


def test_recon_drone_cannot_strike_and_the_path_reaches_the_root():
    r = explain_capability("recon_drone", ActionKind.strike_target, ONTO)
    assert (r.allowed, r.path, r.via) == (False, ["recon_drone", "air_vehicle", "vehicle"], None)


def test_armed_drone_strikes_from_its_own_kind():
    r = explain_capability("armed_drone", ActionKind.strike_target, ONTO)
    assert (r.allowed, r.path, r.via) == (True, ["armed_drone"], "strike")


def test_a_single_action_in_provides():
    ok = explain_capability("ground_robot", ActionKind.watch_point, ONTO)
    no = explain_capability("ground_robot", ActionKind.watch_target, ONTO)
    assert (ok.allowed, ok.path, ok.via) == (
        True,
        ["ground_robot", "ground_vehicle"],
        "watch_point",
    )
    assert not no.allowed and no.path == ["ground_robot", "ground_vehicle", "vehicle"]


def test_moving_comes_from_the_root():
    r = explain_capability("armed_usv", ActionKind.move_to, ONTO)
    assert (r.allowed, r.path, r.via) == (True, ["armed_usv", "sea_vehicle", "vehicle"], "move")
