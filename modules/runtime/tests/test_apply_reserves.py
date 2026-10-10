from contracts.models import (
    Action,
    Assignment,
    GeoPoint,
    Operation,
    Play,
    Polygon,
    Step,
    VehicleState,
)
from modules.runtime.actions.apply_reserves import apply_reserves


def P(lat: float, lon: float) -> GeoPoint:
    return GeoPoint(lat=lat, lon=lon)


ZONE = Polygon(points=[P(37.0, 126.0), P(37.0, 126.1), P(37.1, 126.1)])
OP = Operation(id="op1", name="op", area=ZONE, zone=ZONE, vehicle_ids=["d1", "d3"],
               reserve={"d1": ["d3"]})  # fmt: skip
WATCH = Play(id="watch", name="w", domains=["air"], entry="w1",
             steps=[Step(id="w1", name="1", do=Action(kind="watch_target")),
                    Step(id="w2", name="2", do=Action(kind="return_home"))])  # fmt: skip
PLAYS = {"watch": WATCH}
START = [Assignment(vehicle_id="d1", play_id="watch", since_ms=0, reason="작전 배정"),
         Assignment(vehicle_id="d3", play_id="standby", since_ms=0, reason="작전 배정")]  # fmt: skip


def vs(vid: str, status: str, play_id: str, step_id: str) -> VehicleState:
    return VehicleState(id=vid, t_ms=0, pos=P(37.05, 126.05), heading_deg=0, battery_pct=90,
                        status=status, play_id=play_id, step_id=step_id, entered_step=True)  # fmt: skip


def test_reserve_takes_over_the_play_from_its_entry():
    states = [vs("d1", "returning", "watch", "w2"), vs("d3", "ready", "standby", "s1")]
    out, asg, rep = apply_reserves(states, OP, PLAYS, START, 1_140_000)
    d3 = out[1]
    assert (d3.play_id, d3.step_id, d3.entered_step) == ("watch", "w1", False)
    assert out[0] == states[0]
    new = [a for a in asg if a.vehicle_id == "d3"]
    assert len(new) == 1 and (new[0].reason, new[0].since_ms) == ("예비 투입: d1 대신", 1_140_000)
    assert (rep.kind, rep.vehicle_id) == ("vehicle_gap", "d3")


def test_only_once_per_lost_vehicle():
    states = [vs("d1", "returning", "watch", "w2"), vs("d3", "ready", "standby", "s1")]
    out, asg, _ = apply_reserves(states, OP, PLAYS, START, 1000)
    again = apply_reserves(out, OP, PLAYS, asg, 2000)
    assert again == (out, asg, None)


def test_nothing_while_the_vehicle_is_working_or_no_reserve_is_free():
    working = [vs("d1", "active", "watch", "w1"), vs("d3", "ready", "standby", "s1")]
    assert apply_reserves(working, OP, PLAYS, START, 1000) == (working, START, None)
    busy = [vs("d1", "lost", "watch", "w1"), vs("d3", "maintenance", "standby", "s1")]
    assert apply_reserves(busy, OP, PLAYS, START, 1000) == (busy, START, None)


def test_reserve_keeps_watching_the_target_of_the_vehicle_it_replaces():  # decision 0036
    gone = vs("d1", "returning", "watch", "w2").model_copy(update={"target_id": "boat2"})
    out, _, _ = apply_reserves([gone, vs("d3", "active", "standby", "s1")], OP, PLAYS, START, 1000)
    assert (out[1].play_id, out[1].target_id, out[1].decision_id) == ("watch", "boat2", None)
