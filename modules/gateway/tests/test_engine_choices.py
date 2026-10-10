"""Decision 0044: the choices of an open contact card follow the fleet every tick."""

from dataclasses import replace

from contracts.models import TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json

SC0 = load_scenario_json("demo/scenarios/baengnyeong_night.json")
# the old flow, built here so this test does not depend on the scenario file's start
OLD_START = SC0.operation.model_copy(update={
    "assign": {**SC0.operation.assign, "d1": "patrol_a", "d2": "patrol_b"},
    "reserve": {"d1": ["d3"]}})  # fmt: skip
PLAYS = [
    p.model_copy(update={"steps": [
        s.model_copy(update={"report": s.report.model_copy(update={"auto_choices": True})})
        if s.report else s
        for s in p.steps]})
    if p.id in ("patrol_a", "patrol_b") else p
    for p in SC0.plays
]  # fmt: skip
SC = SC0.model_copy(update={"operation": OLD_START, "plays": PLAYS})


def _first_contact_card():
    es = init_engine(SC)
    while not any(r.kind == "target_detected" for r in es.reports):
        es, _ = tick(es, TickInputs())
    return es, next(r for r in es.reports if r.kind == "target_detected")


def test_a_drone_that_opens_its_own_card_leaves_the_open_cards_choices_next_tick():
    es, card = _first_contact_card()
    assert "take_d4" in [c.id for c in card.choices]
    busy = [
        s.model_copy(update={"pending_report_id": "rep-d4-x"}) if s.id == "d4" else s
        for s in es.states
    ]
    es, _ = tick(replace(es, states=busy), TickInputs())
    now = next(r for r in es.reports if r.id == card.id)
    ids = [c.id for c in now.choices]
    assert ids[0] == "approach" and "take_d3" in ids and not any(i.endswith("_d4") for i in ids)
