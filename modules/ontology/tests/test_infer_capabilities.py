from pathlib import Path

from contracts.models import ActionKind, Scenario
from modules.ontology.actions.infer_capabilities import infer_capabilities

DEMO = Path(__file__).resolve().parents[3] / "demo" / "scenarios" / "baengnyeong_night.json"
ONTO = Scenario.model_validate_json(DEMO.read_text(encoding="utf-8")).ontology
MOVE = {"move_to", "patrol_route", "return_home", "hold"}


def test_recon_drone_has_everything_but_strike_in_enum_order():
    got = infer_capabilities("recon_drone", ONTO)
    assert got == [a for a in ActionKind if a != ActionKind.strike_target]


def test_armed_usv_strikes_but_does_not_relay():
    got = {a.value for a in infer_capabilities("armed_usv", ONTO)}
    assert "strike_target" in got and "relay_comms" not in got


def test_ground_robot_moves_and_watches_a_point():
    assert {a.value for a in infer_capabilities("ground_robot", ONTO)} == MOVE | {"watch_point"}
