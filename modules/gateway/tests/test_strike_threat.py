"""Strike operation stage 1: the emitting site is heard before it is seen, then gets a threat card."""

from contracts.models import TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json

SC = load_scenario_json("demo/scenarios/baengnyeong_strike.json")
START, MIN = SC.operation.started_ms, 60_000


def _run_ten_minutes():
    es, heard, seen = init_engine(SC), None, None
    for _ in range(10 * MIN // SC.tick_ms):
        es, _ = tick(es, TickInputs())
        a = next((t for t in es.targets if t.id == "site_a"), None)
        if a and a.rf_detected and heard is None:
            heard = es.t_ms - START
        if a and a.seen_by and seen is None:
            seen = es.t_ms - START
    return es, heard, seen


def test_the_sites_spawn_and_the_emitting_one_is_heard_before_it_is_seen():
    es, heard, seen = _run_ten_minutes()
    assert {t.id for t in es.targets} == {
        "site_a",
        "site_b",
        "site_c",
    }  # an offset of 0 would leave none
    assert heard is not None and seen is not None and heard < seen


def test_only_the_emitting_site_gets_a_card_and_it_has_its_threat_reasons():
    es, _, _ = _run_ten_minutes()
    cards = [r for r in es.reports if r.kind == "target_detected"]
    assert [(r.vehicle_id, r.target_id) for r in cards] == [("r1", "site_a")]
    assert cards[0].text.startswith("미식별 거점 감지")
    a = next(t for t in es.targets if t.id == "site_a")
    assert a.threat == 75 and a.threat_reasons == [
        "kind_unknown",
        "near_watch_radius",
        "rf_emission",
    ]


def test_the_silent_sites_are_not_heard():
    es, _, _ = _run_ten_minutes()
    assert not any(t.rf_detected for t in es.targets if t.id in ("site_b", "site_c"))
