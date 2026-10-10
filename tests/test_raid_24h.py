"""Decision 0055 (user 10/10, plan A): the 24h raiders cross the coast patrols and are caught. Runs the real tick loop."""

from pathlib import Path

from contracts.models import TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json

DAY = Path(__file__).resolve().parent.parent / "demo" / "scenarios" / "baengnyeong_24h.json"


def test_24h_patrols_catch_both_raiders_crossing_the_coast():  # user 10/10 A: they cross the patrol at T+17
    day = load_scenario_json(DAY)
    es, seen = init_engine(day), {}
    while es.t_ms < day.operation.started_ms + 18 * 60_000:
        es, f = tick(es, TickInputs())
        for t in f.targets:
            coast = [v for v in t.seen_by if v in day.operation.rotation]
            if coast and t.id not in seen:
                seen[t.id] = (f.t_ms - day.operation.started_ms) / 60_000
    assert set(seen) >= {"e_drone", "e_usv"} and all(16 <= m <= 18 for m in seen.values()), seen
