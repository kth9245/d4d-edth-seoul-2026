import pytest

from contracts.models import Scenario
from modules.gateway.live import Live
from modules.gateway.tests.test_live import ROOT, SCENARIO, FakeEngine, make
from modules.gateway.tests.test_live_roles import PATROL_A

DAY = Scenario.model_validate_json(
    (ROOT / "demo/scenarios/baengnyeong_24h.json").read_text(encoding="utf-8")
)


def make_two() -> tuple[Live, FakeEngine]:
    eng = FakeEngine()
    return Live(SCENARIO, eng.init, eng.tick, [SCENARIO, DAY]), eng


def test_scenario_infos_list_the_catalog_with_the_running_one_active():
    live, _ = make_two()
    infos = live.scenario_infos()
    assert [(i.id, i.active) for i in infos] == [
        ("baengnyeong_night", True),
        ("baengnyeong_24h", False),
    ]
    assert infos[1].name == DAY.operation.name
    assert infos[1].purpose == DAY.operation.purpose


def test_activate_runs_the_other_operation_from_its_start_paused():
    live, eng = make_two()
    live.set_speed(5)
    run = live.activate("baengnyeong_24h")
    assert run.status == "paused"
    assert live.scenario.id == "baengnyeong_24h"
    assert eng.inits[-1].id == "baengnyeong_24h"
    assert [i.active for i in live.scenario_infos()] == [False, True]


def test_a_saved_role_survives_going_to_another_operation_and_back():
    live, _ = make_two()
    assert live.save_role(PATROL_A.model_copy(update={"name": "해안 순찰 A2"})).ok
    live.activate("baengnyeong_24h")
    live.activate("baengnyeong_night")
    assert next(p for p in live.scenario.roles if p.id == "patrol_a").name == "해안 순찰 A2"


def test_activating_the_running_operation_again_keeps_its_saved_role():
    live, _ = make_two()
    assert live.save_role(PATROL_A.model_copy(update={"name": "해안 순찰 A2"})).ok
    assert live.activate("baengnyeong_night").status == "paused"
    assert next(p for p in live.scenario.roles if p.id == "patrol_a").name == "해안 순찰 A2"


def test_activate_an_unknown_id_raises_and_changes_nothing():
    live, eng = make_two()
    inits = len(eng.inits)
    with pytest.raises(KeyError):
        live.activate("nope")
    assert live.scenario.id == "baengnyeong_night"
    assert len(eng.inits) == inits


def test_without_a_catalog_only_the_running_scenario_is_listed():
    live, _ = make()
    assert [(i.id, i.active) for i in live.scenario_infos()] == [("baengnyeong_night", True)]


def test_the_running_scenario_wins_over_a_catalog_entry_with_its_id():
    backup = SCENARIO.model_copy(
        update={"operation": SCENARIO.operation.model_copy(update={"name": "백업"})}
    )
    eng = FakeEngine()
    live = Live(backup, eng.init, eng.tick, [SCENARIO, DAY])
    assert [i.name for i in live.scenario_infos()] == ["백업", DAY.operation.name]
