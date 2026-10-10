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
    seen = _states(
        "demo/scenarios/baengnyeong_strike.json", "site_a", 5000
    )  # 17 minutes: r1 reaches it at 14
    assert {"rf_only", "identified"} <= seen


def test_the_tick_loop_opens_strike_choices_only_after_identification():
    sc = load_scenario_json("demo/scenarios/baengnyeong_strike.json")
    es, before, after = init_engine(sc), set(), set()
    for _ in range(5000):  # r1 identifies site_a at about 15.7 minutes
        es, _ = tick(es, TickInputs())
        site = next((t for t in es.targets if t.id == "site_a"), None)
        card = next(
            (r for r in es.reports if r.kind == "target_detected" and r.target_id == "site_a"), None
        )
        if site is None or card is None or card.resolved_ms:
            continue
        ids = {c.id for c in card.choices}
        (after if site.ident_state == "identified" else before).update(
            i for i in ids if i.startswith("strike_")
        )
    assert before == set() and {"strike_a1", "strike_a2", "strike_a3"} <= after


def test_a_click_on_a_strike_choice_that_just_vanished_does_not_stop_the_loop():
    from contracts.models import Decision

    sc = load_scenario_json("demo/scenarios/baengnyeong_strike.json")
    es = init_engine(sc)
    while not any(r.kind == "target_detected" and r.target_id == "site_a" for r in es.reports):
        es, _ = tick(es, TickInputs())
    card = next(r for r in es.reports if r.kind == "target_detected" and r.target_id == "site_a")
    assert "strike_ghost" not in [c.id for c in card.choices]  # what a vanished choice looks like
    stale = Decision(id="dec-1", t_ms=es.t_ms + 200, report_id=card.id, choice_id="strike_ghost")
    es, _ = tick(es, TickInputs(decisions=[stale]))  # used to raise StopIteration
    assert not next(
        r for r in es.reports if r.id == card.id
    ).resolved_ms  # ignored, card still open
