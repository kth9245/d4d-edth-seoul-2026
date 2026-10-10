from contracts.models import Action, Choice, Decision, GeoPoint, Play, Report, Step, VehicleState
from modules.runtime.actions.apply_decision import apply_decision


def play(pid: str) -> Play:
    return Play(id=pid, name=pid, domains=["air", "sea", "ground"], entry=f"{pid}-1",
                steps=[Step(id=f"{pid}-1", name="1", do=Action(kind="hold"))])  # fmt: skip


PLAYS = {p: play(p) for p in ("patrol_a", "standby", "watch", "approach", "landing", "patrol_b")}


def vs(vid: str, play_id: str, **kw) -> VehicleState:
    return VehicleState(id=vid, t_ms=0, pos=GeoPoint(lat=37, lon=126), heading_deg=0,
                        battery_pct=90, status="active", play_id=play_id,
                        step_id=f"{play_id}-2", entered_step=True, **kw)  # fmt: skip


APPROACH = Choice(id="approach", label="접근",
                  play_by_vehicle={"d1": "watch", "usv": "approach", "ugv": "landing",
                                   "d2": "patrol_b"})  # fmt: skip
CARD = Report(id="r1", t_ms=0, kind="target_detected", vehicle_id="d1", text="보트",
              choices=[APPROACH, Choice(id="ignore", label="무시")])  # fmt: skip


def decide(choice: str, report_id: str = "r1") -> Decision:
    return Decision(id="dec1", t_ms=660_000, report_id=report_id, choice_id=choice)


def test_one_choice_switches_four_vehicles_at_once():
    states = [vs("d1", "patrol_a", pending_report_id="r1"), vs("d2", "standby"),
              vs("d3", "standby"), vs("usv", "standby"), vs("ugv", "standby")]  # fmt: skip
    out, reports = apply_decision(states, PLAYS, decide("approach"), [CARD])
    got = {s.id: (s.play_id, s.step_id, s.entered_step) for s in out}
    assert got["d1"] == ("watch", "watch-1", False)
    assert got["usv"] == ("approach", "approach-1", False)
    assert got["ugv"] == ("landing", "landing-1", False)
    assert got["d2"] == ("patrol_b", "patrol_b-1", False)
    assert out[2] == states[2]  # d3 not in the choice
    assert out[0].pending_report_id is None
    assert (reports[0].resolved_ms, reports[0].decision_id) == (660_000, "dec1")


def test_choice_without_the_reporter_just_releases_it():
    out, _ = apply_decision([vs("d1", "patrol_a", pending_report_id="r1")], PLAYS, decide("ignore"),
                            [CARD])  # fmt: skip
    assert (out[0].play_id, out[0].pending_report_id) == ("patrol_a", None)


def test_target_select_sets_the_target_and_reenters_the_step():
    card = Report(id="r2", t_ms=0, kind="target_select", vehicle_id="d1", text="표적",
                  choices=[Choice(id="boat1", label="b"), Choice(id="fast1", label="f")])  # fmt: skip
    st = vs("d1", "watch", pending_report_id="r2")
    out, reports = apply_decision([st], PLAYS, decide("fast1", "r2"), [CARD, card])
    assert (out[0].target_id, out[0].pending_report_id, out[0].entered_step) == (
        "fast1",
        None,
        False,
    )
    assert out[0].step_id == st.step_id
    assert reports[0].resolved_ms is None and reports[1].decision_id == "dec1"
