"""Part2-28: the demo scenario's threat scene (decisions 0039, 0040).

boat2 is silent when its contact card comes (16:22), starts emitting at 17:00 while d2 is within
RF range, and its score jumps by exactly 0.30 (0.42 to 0.72) above boat1's: the card moves to the top of the list.
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


def test_boat2_starts_emitting_after_its_card_and_overtakes_boat1():
    es, before, card_ms = init_engine(SC), None, None
    for _ in range(17 * MIN // SC.tick_ms + 25):
        before = _score(es, "boat2")
        es, _ = tick(es, _answer_cards_after_20s(es, es.t_ms + SC.tick_ms))
        now = _score(es, "boat2")
        card = next(
            (r for r in es.reports if r.kind == "target_detected" and r.target_id == "boat2"), None
        )
        card_ms = card.t_ms if card else card_ms
        if now and now.emitting and not before.emitting:
            break
    assert card_ms is not None and card_ms - START == 16 * MIN + 22_200
    assert es.t_ms - START == 17 * MIN
    assert now.rf_detected and now.seen_by and "rf_emission" in now.threat_reasons
    assert (before.threat, now.threat) == (42, 72)  # +0.30 for the RF and nothing else changes
    assert "near_watch_radius" in now.threat_reasons  # outside 2 km but inside 4 km (0041)
    assert now.threat > _score(es, "boat1").threat  # 0.72 vs 0.50: its card goes to the top
    assert not _score(es, "boat1").emitting and not _score(es, "boat3").emitting
