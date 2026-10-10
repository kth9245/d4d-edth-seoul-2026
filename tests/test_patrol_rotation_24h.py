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
def day():  # checks each frame as it comes: keeping 432,000 frames (200 ms ticks) ran WSL out of memory
    sc = load_scenario_json(str(SCENARIO))
    sc = sc.model_copy(
        update={"enemies": []}
    )  # rotation only: the raid (0055) pulls drones off on purpose
    home = {v.id: v.home for v in sc.vehicles}
    es, gaps, landed, prev = init_engine(sc), [], [], {}
    for _ in range(DAY_S * 1000 // sc.tick_ms):
        es, f = tick(es, TickInputs())
        s = (f.t_ms - sc.operation.started_ms) // 1000
        if s >= WARMUP_S:
            gaps += [(s, role) for role in ("coast_a", "coast_b") if not _patrolling(f, role)]
        for v in f.vehicles:
            if v.status.value == "maintenance" and prev.get(v.id) != "maintenance":
                landed.append((v.id, round(v.battery_pct, 1), round(dist_m(v.pos, home[v.id]))))
            prev[v.id] = v.status.value
    return gaps, landed


def _patrolling(f, role):
    return [v for v in f.vehicles if v.role_id == role and v.status.value == "active"]


def test_both_coasts_always_covered_for_24h(day):
    gaps, _ = day
    assert gaps == []


def test_landings_keep_30_percent(day):
    _, landed = day
    print("landings:", len(landed), "lowest:", min(landed, key=lambda x: x[1]) if landed else None)
    assert landed and all(pct >= 30 for _, pct, _ in landed)
