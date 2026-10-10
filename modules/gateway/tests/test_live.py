from pathlib import Path

from contracts.models import (
    DecisionIn,
    DirectIn,
    Frame,
    GeoPoint,
    Metrics,
    RunState,
    Scenario,
    SwitchIn,
    TickInputs,
)
from modules import sim
from modules.gateway.live import Live

ROOT = Path(__file__).resolve().parents[3]
# through the loader so capabilities come from the ontology (decision 0038)
SCENARIO = sim.load_scenario_json(ROOT / "demo/scenarios/baengnyeong_night.json")
START = SCENARIO.operation.started_ms


class FakeEngine:
    """Records every TickInputs; the engine state is just t_ms."""

    def __init__(self):
        self.seen: list[TickInputs] = []
        self.inits: list[Scenario] = []  # the scenario each reset handed to the engine

    def init(self, scenario: Scenario) -> int:
        self.inits.append(scenario)
        return scenario.operation.started_ms

    def tick(self, t_ms: int, inputs: TickInputs) -> tuple[int, Frame]:
        self.seen.append(inputs)
        t = t_ms + 200
        empty = dict(vehicles=[], targets=[], reports=[], assignments=[], blocks=[], injections=[])
        frame = Frame(
            t_ms=t, run=RunState(status="ended"), metrics=Metrics(), log=[f"t{t}"], **empty
        )
        return t, frame


def make() -> tuple[Live, FakeEngine]:
    eng = FakeEngine()
    return Live(SCENARIO, eng.init, eng.tick), eng


def test_reset_is_paused_with_a_first_frame():
    live, eng = make()
    assert live.frame.t_ms == START + 200
    assert live.frame.run == RunState(status="paused", speed=1.0)
    assert len(eng.seen) == 1


def test_speed_runs_that_many_ticks_per_period():
    live, eng = make()
    live.set_speed(3)
    live.period()
    assert live.frame.t_ms == START + 4 * 200
    assert live.frame.run == RunState(status="running", speed=3)


def test_half_speed_runs_one_tick_every_two_periods():
    live, _ = make()
    live.set_speed(0.5)
    live.period()
    assert live.frame.t_ms == START + 200
    live.period()
    assert live.frame.t_ms == START + 400


def test_speed_zero_pauses_and_keeps_the_last_speed():
    live, _ = make()
    live.set_speed(15)
    assert live.set_speed(0) == RunState(status="paused", speed=15)
    live.period()
    assert live.frame.t_ms == START + 200
    assert live.frame.run.status == "paused"


def test_decision_goes_into_the_next_tick_inputs_once():
    live, eng = make()
    acc = live.decide(DecisionIn(report_id="rep-d1-1", choice_id="watch"))
    assert (acc.id, acc.t_ms) == ("dec-1", START + 400)
    live.set_speed(2)
    live.period()
    first, second = eng.seen[-2:]
    assert [(d.id, d.t_ms, d.report_id, d.choice_id) for d in first.decisions] == [
        ("dec-1", START + 400, "rep-d1-1", "watch")
    ]
    assert second.decisions == []


def test_direct_gets_a_server_id():
    live, eng = make()
    acc = live.direct(DirectIn(vehicle_id="d2", target=GeoPoint(lat=37.9, lon=124.6)))
    live.jump(400)
    assert acc.id == "dir-1"
    assert [(d.id, d.vehicle_id) for d in eng.seen[1].direct] == [("dir-1", "d2")]


def test_partial_switch_then_approve():
    live, eng = make()
    inj = live.request_switch(SwitchIn(role_by_vehicle={"d2": "track_fast"}))
    assert (inj.id, inj.status, inj.label) == ("inj-1", "pending", "고속 보트 추적: d2")
    live.jump(400)
    assert live.settle_injection("inj-1", approve=True).status == "approved"
    live.jump(600)
    assert [(i.id, i.status) for i in eng.seen[1].injections] == [("inj-1", "pending")]
    assert [(i.id, i.status) for i in eng.seen[2].injections] == [("inj-1", "approved")]


def test_approve_before_the_request_ticked_waits_one_tick():
    # the engine opens the pending card in the request's tick and closes it in a later one
    live, eng = make()
    live.request_switch(SwitchIn(role_by_vehicle={"d2": "track_fast"}))
    live.settle_injection("inj-1", approve=True)
    live.jump(600)
    assert [i.status for i in eng.seen[1].injections] == ["pending"]
    assert [i.status for i in eng.seen[2].injections] == ["approved"]


def test_switch_button_uses_the_operation_switch():
    live, _ = make()
    inj = live.request_switch(SwitchIn(switch_id="all_home"))
    assert (inj.label, inj.switch_id) == ("전 기체 귀환", "all_home")
    assert inj.role_by_vehicle["usv"] == "go_home"
    assert live.settle_injection(inj.id, approve=False).status == "rejected"


def test_pointing_request_is_approved_at_once_and_carries_the_target():
    # decisions 0048, 0049: point d2 at boat1 with a role; the press is the approval, so no pending card
    live, eng = make()
    inj = live.request_switch(
        SwitchIn(role_by_vehicle={"d2": "watch"}, target_by_vehicle={"d2": "boat1"}, approve=True)
    )
    assert (inj.status, inj.target_by_vehicle, inj.label) == (
        "approved",
        {"d2": "boat1"},
        "표적 감시: d2 → boat1",
    )
    live.jump(400)
    assert [(i.id, i.status) for i in eng.seen[1].injections] == [(inj.id, "approved")]


def test_jump_runs_ticks_up_to_the_offset():
    live, _ = make()
    live.jump(16 * 60_000)
    assert live.frame.t_ms == START + 16 * 60_000
    assert live.frame.run.status == "paused"


def test_set_operation_replaces_it_and_resets():
    live, _ = make()
    live.jump(60_000)
    op = SCENARIO.operation.model_copy(update={"name": "새 작전"})
    live.set_operation(op)
    assert live.scenario.operation.name == "새 작전"
    assert live.frame.t_ms == START + 200


def test_log_lines_of_every_tick_reach_each_connection_once():
    live, _ = make()
    frame, cur = live.frame_for(None)
    assert frame.log == [f"t{START + 200}"]  # a new connection gets the lines since reset
    live.set_speed(3)
    live.period()
    frame, cur = live.frame_for(cur)
    assert frame.log == [f"t{START + 400}", f"t{START + 600}", f"t{START + 800}"]
    live.set_speed(0)
    assert live.frame_for(cur)[0].log == []  # paused: nothing sent twice


def test_log_cursor_restarts_after_reset():
    live, _ = make()
    _, cur = live.frame_for(None)
    live.jump(1000)
    live.reset()
    assert live.frame_for(cur)[0].log == [f"t{START + 200}"]
