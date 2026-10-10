"""Part2-28: the demo scenario's threat scene (decisions 0039, 0040).

boat2 starts emitting at 17:00; when a drone first hears it (RF range) its score jumps by exactly 0.30 and
passes boat1's, so its card moves to the top of the list. The demo now starts on the coast patrol (user, 10/10).
"""

from contracts.models import Decision, TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json

SC = load_scenario_json("demo/scenarios/baengnyeong_night.json")
START, MIN = SC.operation.started_ms, 60_000


def _answer_cards_after_20s(es, t: int) -> TickInputs:
    return TickInputs(decisions=[
        Decision(id=f"dec-{r.id}", t_ms=t, report_id=r.id, choice_id=r.choices[0].id)
        for r in es.reports
        if r.choices and not r.resolved_ms and t == r.t_ms + 20_000
    ])  # fmt: skip


def _score(es, tid: str):
    return next((t for t in es.targets if t.id == tid), None)


def test_scenario_has_watch_point_and_rf_drones():
    assert [(w.id, w.radius_m) for w in SC.watch_points] == [("landing", 2000.0)]
    assert {v.id: v.rf_range_m for v in SC.vehicles} == {
        "d1": 2000.0, "d2": 2000.0, "d3": 2000.0, "d4": 2000.0, "usv": 0.0, "ugv": 0.0,
    }  # fmt: skip


def test_boat2_emits_from_17_and_overtakes_boat1_once_a_drone_hears_it():
    es, before, start_emit = init_engine(SC), None, None
    for _ in range(30 * MIN // SC.tick_ms):
        before = _score(es, "boat2")
        es, _ = tick(es, _answer_cards_after_20s(es, es.t_ms + SC.tick_ms))
        now = _score(es, "boat2")
        if now and now.emitting and start_emit is None:
            start_emit = es.t_ms - START
        if now and now.rf_detected and not before.rf_detected:
            break
    assert start_emit == 17 * MIN
    assert es.t_ms - START >= 17 * MIN and now.rf_detected and "rf_emission" in now.threat_reasons
    assert now.threat - before.threat == 30  # +0.30 for the RF and nothing else changes
    assert now.threat > _score(es, "boat1").threat  # its card goes to the top
    assert not _score(es, "boat1").emitting and not _score(es, "boat3").emitting
