from pathlib import Path

from contracts.models import ActionKind, Scenario
from modules.ontology.actions.ontology_view import ontology_view

DEMO = Path(__file__).resolve().parents[3] / "demo" / "scenarios" / "baengnyeong_night.json"
RAW = Scenario.model_validate_json(DEMO.read_text(encoding="utf-8"))


def test_every_vehicle_gets_a_verdict_per_action():
    view = ontology_view(RAW)
    assert view.ontology == RAW.ontology
    assert [v.vehicle_id for v in view.vehicles] == ["d1", "d2", "d3", "usv", "ugv"]
    assert all([r.action for r in v.reasons] == list(ActionKind) for v in view.vehicles)
    d1 = view.vehicles[0]
    strike = next(r for r in d1.reasons if r.action == ActionKind.strike_target)
    assert d1.kind == "recon_drone" and not strike.allowed
