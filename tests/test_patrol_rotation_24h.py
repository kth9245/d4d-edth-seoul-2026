"""Decision 0037: three drones keep the north (A) and south (B) coasts covered for 24 hours by relieving
each other like a guard post change (90 min endurance, 10 min battery swap). Runs the real tick loop."""

from pathlib import Path

import pytest

from contracts.models import TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json
from shared.geo import dist_m

SCENARIO = Path(__file__).resolve().parent.parent / "demo" / "scenarios" / "baengnyeong_24h.json"
WARMUP_S, DAY_S = 30 * 60, 24 * 3600


@pytest.fixture(scope="module")
def day():
    sc = load_scenario_json(str(SCENARIO))
    es, frames = init_engine(sc), []
    for _ in range(DAY_S * 1000 // sc.tick_ms):
        es, f = tick(es, TickInputs())
        frames.append(f)
    return sc, frames


def _patrolling(f, play):
    return [v for v in f.vehicles if v.play_id == play and v.status.value == "active"]


def test_both_coasts_always_covered_for_24h(day):
    sc, frames = day
    gaps = [
        ((f.t_ms - sc.operation.started_ms) // 1000, play)
        for f in frames
        if f.t_ms - sc.operation.started_ms >= WARMUP_S * 1000
        for play in ("coast_a", "coast_b")
        if not _patrolling(f, play)
    ]
    assert gaps == []


def test_landings_keep_30_percent(day):
    sc, frames = day
    home = {v.id: v.home for v in sc.vehicles}
    landed, prev = [], {}
    for f in frames:
        for v in f.vehicles:
            if v.status.value == "maintenance" and prev.get(v.id) != "maintenance":
                landed.append((v.id, round(v.battery_pct, 1), round(dist_m(v.pos, home[v.id]))))
            prev[v.id] = v.status.value
    print("landings:", len(landed), "lowest:", min(landed, key=lambda x: x[1]) if landed else None)
    assert landed and all(pct >= 30 for _, pct, _ in landed)
