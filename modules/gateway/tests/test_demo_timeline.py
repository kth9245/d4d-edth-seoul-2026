"""Part2-19: the demo scenario on the real tick loop gives the scenes in the strike-phase order
(docs/superpowers/specs/2026-10-10-strike-phase-design.md section 2): s1 s2 s3 s5 s6 s4 (s7 s8 later).

The operator is scripted here: cards answered 20 s after they appear, d2 sent past the NLL at
20:00, the block's alternative applied at 20:05, d2 sent to the far south-east corner at 20:30.
"""

import pytest

from contracts.models import Decision, DirectControl, GeoPoint, TickInputs
from modules.gateway.engine import init_engine, tick
from modules.play import check_operation
from modules.sim import load_scenario_json

SC = load_scenario_json("demo/scenarios/baengnyeong_night.json")
START, MIN = SC.operation.started_ms, 60_000
PAST_NLL = GeoPoint(lat=38.05, lon=124.66)  # s5: north of the zone edge (lat 38.0)
FAR_SE = GeoPoint(lat=37.905, lon=124.835)  # s6: inside the zone, beyond d2's return battery


def _inputs(es, t: int, n: dict) -> TickInputs:
    decs, direct = [], []
    for r in es.reports:
        if r.choices and not r.resolved_ms and t == r.t_ms + 20_000:
            n["dec"] += 1
            decs.append(Decision(id=f"dec-{n['dec']}", t_ms=t, report_id=r.id,
                                 choice_id=r.choices[0].id))  # fmt: skip
    goal = {20 * MIN: PAST_NLL, 20 * MIN + 30_000: FAR_SE}.get(t - START)
    if t - START == 20 * MIN + 5_000 and es.blocks and es.blocks[-1].alternative:
        goal = GeoPoint(**es.blocks[-1].alternative.params["target"])
    if goal:
        n["dir"] += 1
        direct.append(DirectControl(id=f"dir-{n['dir']}", vehicle_id="d2", target=goal, t_ms=t))
    return TickInputs(decisions=decs, direct=direct)


@pytest.fixture(scope="module")
def scenes() -> dict[str, int]:
    es, n, seen = init_engine(SC), {"dec": 0, "dir": 0}, {}

    def mark(scene: str, ok: bool) -> None:
        if ok and scene not in seen:
            seen[scene] = es.t_ms - START

    for _ in range(25 * MIN // SC.tick_ms):
        es, fr = tick(es, _inputs(es, es.t_ms + SC.tick_ms, n))
        mark("s1", any(r.kind == "target_detected" and r.vehicle_id == "d1" for r in es.reports))
        mark("s2", sum(a.reason == "결정 dec-1" for a in es.assignments) == 4)
        mark("s3", any(r.kind == "vehicle_gap" for r in es.reports))
        mark("s5", any(b.vehicle_id == "d2" and b.reason == "outside_zone" for b in es.blocks))
        mark(
            "s6",
            any(b.vehicle_id == "d2" and b.reason == "battery_insufficient" for b in es.blocks),
        )
        mark("s4", any(t.id == "fast1" for t in es.targets))
    return seen


def test_scenes_happen_in_strike_phase_order(scenes):
    order = ["s1", "s2", "s3", "s5", "s6", "s4"]
    assert [s for s in order if s in scenes] == order, scenes
    assert [scenes[s] for s in order] == sorted(scenes[s] for s in order), scenes


def test_alternative_after_zone_block_is_not_blocked(scenes):
    assert scenes["s6"] - scenes["s5"] == 30_000  # only the 20:30 command was blocked after s5


def test_operation_passes_play_checks_including_reserve_return_battery():
    plays, specs = {p.id: p for p in SC.plays}, {v.id: v for v in SC.vehicles}
    assert check_operation(SC.operation, plays, specs).ok
