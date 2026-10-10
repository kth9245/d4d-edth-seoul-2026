"""Strike operation: each recon drone searches its own coast stretch; the emitting site is heard before it is seen."""

from contracts.models import TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json

SC = load_scenario_json("demo/scenarios/baengnyeong_strike.json")
START, MIN = SC.operation.started_ms, 60_000
RUN_MINUTES = 25  # r2 meets site_c at 5 min, r1 hears site_a at 14 min, r3 sees site_b at 24 min


def _run():
    es, heard, seen = init_engine(SC), None, None
    for _ in range(RUN_MINUTES * MIN // SC.tick_ms):
        es, _ = tick(es, TickInputs())
        a = next((t for t in es.targets if t.id == "site_a"), None)
        if a and a.rf_detected and heard is None:
            heard = es.t_ms - START
        if a and a.seen_by and seen is None:
            seen = es.t_ms - START
    return es, heard, seen


def test_the_sites_spawn_and_the_emitting_one_is_heard_before_it_is_seen():
    es, heard, seen = _run()
    assert {t.id for t in es.targets} == {
        "site_a",
        "site_b",
        "site_c",
    }  # an offset of 0 would leave none
    assert heard is not None and seen is not None and heard < seen


def test_each_recon_drone_raises_the_card_for_the_site_on_its_own_stretch():
    es, _, _ = _run()
    cards = [r for r in es.reports if r.kind == "target_detected"]
    pairs = {(r.vehicle_id, r.target_id) for r in cards}
    assert pairs == {("r1", "site_a"), ("r2", "site_c"), ("r3", "site_b")}
    assert len(cards) == 3 and all(c.text.startswith("미식별 거점 감지") for c in cards)


def test_the_emitting_site_has_its_threat_reasons():
    es, _, _ = _run()
    a = next(t for t in es.targets if t.id == "site_a")
    assert a.threat == 75 and a.threat_reasons == [
        "kind_unknown",
        "near_watch_radius",
        "rf_emission",
    ]


def test_the_silent_sites_are_not_heard():
    es, _, _ = _run()
    assert not any(t.rf_detected for t in es.targets if t.id in ("site_b", "site_c"))
