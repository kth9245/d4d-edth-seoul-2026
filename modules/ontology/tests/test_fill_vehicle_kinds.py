from pathlib import Path

from contracts.models import Scenario
from modules.ontology.actions.fill_vehicle_kinds import fill_vehicle_kinds

DEMO = Path(__file__).resolve().parents[3] / "demo" / "scenarios" / "baengnyeong_night.json"
RAW = Scenario.model_validate_json(DEMO.read_text(encoding="utf-8"))


def test_capabilities_and_kind_path_come_from_the_hierarchy():
    v = {x.id: x for x in fill_vehicle_kinds(RAW).vehicles}
    assert "strike_target" not in v["d1"].capabilities
    assert "strike_target" in v["d2"].capabilities
    assert v["d1"].kind_path == ["정찰 드론", "공중 기체", "기체"]
    assert v["ugv"].kind_path == ["지상 로봇", "지상 기체", "기체"]


def test_kind_overrides_stale_capabilities():
    stale = RAW.model_copy(
        update={
            "vehicles": [
                v.model_copy(update={"capabilities": ["strike_target"]}) for v in RAW.vehicles
            ]
        }
    )
    d1 = next(v for v in fill_vehicle_kinds(stale).vehicles if v.id == "d1")
    assert "strike_target" not in d1.capabilities and "watch_target" in d1.capabilities


def test_without_ontology_or_kind_nothing_changes():
    bare = RAW.model_copy(update={"ontology": None})
    assert fill_vehicle_kinds(bare) == bare
    nokind = RAW.model_copy(
        update={"vehicles": [v.model_copy(update={"kind": None}) for v in RAW.vehicles]}
    )
    assert fill_vehicle_kinds(nokind).vehicles == nokind.vehicles
