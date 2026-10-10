from pathlib import Path

from contracts.models import Scenario
from modules.ontology.actions.kind_chain import kind_chain

DEMO = Path(__file__).resolve().parents[3] / "demo" / "scenarios" / "baengnyeong_night.json"
ONTO = Scenario.model_validate_json(DEMO.read_text(encoding="utf-8")).ontology


def test_walks_up_to_the_root():
    chain = [k.id for k in kind_chain("recon_drone", ONTO)]
    assert chain == ["recon_drone", "air_vehicle", "vehicle"]


def test_the_root_is_its_own_chain():
    assert [k.id for k in kind_chain("vehicle", ONTO)] == ["vehicle"]
