"""engine.tick on the real modules: incident 1 -> report -> decision -> switch, no stubs."""

from contracts.models import Decision, Frame, TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json

SC = load_scenario_json("demo/scenarios/baengnyeong_night.json")
MIN = 60_000


def _until(es, pred, minutes: int = 20):  # d1's patrol first comes within range at ~16 min
    for _ in range(minutes * MIN // SC.tick_ms):
        es, fr = tick(es, TickInputs())
        if pred(es):
            return es, fr
    raise AssertionError("condition never met")


def test_tick_advances_time_by_tick_ms_and_returns_frame():
    es = init_engine(SC)
    es2, fr = tick(es, TickInputs())
    assert es2.t_ms == SC.operation.started_ms + SC.tick_ms
    assert isinstance(fr, Frame) and fr.t_ms == es2.t_ms


def test_each_tick_writes_a_debug_line_to_gateway_engine_logger(caplog):
    caplog.set_level("DEBUG", logger="kdth.gateway.engine")
    tick(init_engine(SC), TickInputs())
    assert [r for r in caplog.records if r.name == "kdth.gateway.engine" and r.levelname == "DEBUG"]


def test_boat_event_gives_target_detected_card_from_d1():
    es, _ = _until(init_engine(SC), lambda e: any(r.kind == "target_detected" for r in e.reports))
    rep = next(r for r in es.reports if r.kind == "target_detected")
    assert rep.vehicle_id == "d1" and rep.choices
    assert rep.t_ms - SC.operation.started_ms >= 11 * MIN


def test_one_decision_switches_four_vehicles():
    es, _ = _until(init_engine(SC), lambda e: any(r.kind == "target_detected" for r in e.reports))
    rep = next(r for r in es.reports if r.kind == "target_detected")
    dec = Decision(id="dec-1", t_ms=es.t_ms + SC.tick_ms, report_id=rep.id,
                   choice_id=rep.choices[0].id)  # fmt: skip
    es, fr = tick(es, TickInputs(decisions=[dec]))
    for _ in range(5):
        es, fr = tick(es, TickInputs())
    plays = {v.id: v.play_id for v in fr.vehicles}
    want = {"d1": "watch", "usv": "approach", "ugv": "landing", "d2": "patrol_b"}
    assert {k: plays[k] for k in want} == want
    assert any(a.reason == "결정 dec-1" for a in fr.assignments)


def test_strike_next_to_a_target_neutralizes_it_and_logs():
    from dataclasses import replace

    from contracts.models import Command, PassedCommand, Target, VehicleStatus

    es = init_engine(SC)
    d1 = es.states[0]
    tg = Target(id="x", kind="boat", pos=d1.pos, vel_east_mps=0, vel_north_mps=0,
                first_seen_ms=0, last_seen_ms=0)  # fmt: skip
    cmd = Command(
        id="c", vehicle_id=d1.id, kind="strike", params={"target_id": "x", "distance_m": 0}
    )
    # model_copy does not validate: give the enum, not the string (step_vehicle reads .value)
    d1 = d1.model_copy(update={"entered_step": True, "status": VehicleStatus.active,
                               "decision_id": "dec-1",  # approved strike (decision 0033)
                               "active": PassedCommand(command=cmd, checks=[], passed_ms=0)})  # fmt: skip
    es = replace(es, states=[d1, *es.states[1:]], targets=[tg])
    es, fr = tick(es, TickInputs())
    assert fr.targets[0].neutralized_ms == es.t_ms
    assert any(line.endswith("x 무력화(d1)") for line in fr.log)
    assert fr.metrics.mission_success is True


def test_enemy_appears_and_moves_by_its_play():
    from contracts.models import Action, EnemySpec, Play, Step

    dest = {"lat": 37.985, "lon": 124.75, "alt_m": 0}
    play = Play(id="enemy_x", name="x", domains=["sea"], entry="go", approved=True,
                steps=[Step(id="go", name="go", do=Action(kind="move_to", params={"target": dest}))])  # fmt: skip
    enemy = EnemySpec(id="x", kind="boat", speed_mps=5, appear_offset_ms=SC.tick_ms,
                      pos={"lat": 37.985, "lon": 124.70}, play_id="enemy_x")  # fmt: skip
    sc = SC.model_copy(update={"enemies": [enemy], "plays": [*SC.plays, play]})
    es = init_engine(sc)
    es, fr = tick(es, TickInputs())
    first = next(t for t in fr.targets if t.id == "x")
    assert first.vel_east_mps > 4.9 and any("적 등장 x" in line for line in fr.log)
    es, fr = tick(es, TickInputs())
    assert next(t for t in fr.targets if t.id == "x").pos.lon > first.pos.lon
