from contracts.models import TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json


def _states(path: str, target_id: str, ticks: int) -> set[str]:
    es, seen = init_engine(load_scenario_json(path)), set()
    for _ in range(ticks):
        es, _ = tick(es, TickInputs())
        seen |= {t.ident_state for t in es.targets if t.id == target_id}
    return seen


def test_the_night_operation_never_gets_identification_fields():
    es = init_engine(load_scenario_json("demo/scenarios/baengnyeong_night.json"))
    boats = set()
    for _ in range(4000):  # 13 simulated minutes: the boats appear at 11 minutes
        es, _ = tick(es, TickInputs())
        boats |= {t.ident_state for t in es.targets}
    assert boats == {"undetected"}


def test_the_strike_operation_identifies_site_a_through_the_tick_loop():
    seen = _states("demo/scenarios/baengnyeong_strike.json", "site_a", 2400)  # 8 minutes
    assert {"rf_only", "identified"} <= seen
