"""Part2-28: the tick loop scores targets (decision 0039) and turns emission on (SIM-14)."""

from contracts.models import GeoPoint, TickInputs, WatchPoint
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json

SC = load_scenario_json("demo/scenarios/baengnyeong_night.json")
WATCH = [WatchPoint(id="landing", name="landing", pos=GeoPoint(lat=37.978, lon=124.70),
                    radius_m=2000)]  # fmt: skip


def run_until_first_enemy_appears():
    first = min(SC.enemies, key=lambda e: e.appear_offset_ms)
    enemies = [e.model_copy(update={"emit_start_offset_ms": 0}) if e.id == first.id else e
               for e in SC.enemies]  # fmt: skip
    silent_drones = [
        v.model_copy(update={"rf_range_m": 0.0}) for v in SC.vehicles
    ]  # only the scan matters here
    sc = SC.model_copy(
        update={"watch_points": WATCH, "enemies": enemies, "vehicles": silent_drones}
    )
    es = init_engine(sc)
    for _ in range(first.appear_offset_ms // sc.tick_ms + 2):
        es, _ = tick(es, TickInputs())
    return first.id, es


def test_unscanned_enemy_is_scored_as_unknown_inside_the_watch_radius():
    eid, es = run_until_first_enemy_appears()
    tg = next(t for t in es.targets if t.id == eid)
    assert not tg.seen_by
    assert tg.threat_reasons[:2] == ["kind_unknown", "inside_watch_radius"] and tg.threat == 60
    assert tg.threat_accum == 0  # not observed yet


def test_enemy_with_emit_offset_zero_is_emitting_from_its_first_tick():
    eid, es = run_until_first_enemy_appears()
    assert next(t for t in es.targets if t.id == eid).emitting is True
    assert not any(t.emitting for t in es.targets if t.id != eid)
