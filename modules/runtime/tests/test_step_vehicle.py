from contracts.models import (
    Action,
    Condition,
    Exit,
    GeoPoint,
    Play,
    Step,
    Target,
    VehicleSpec,
    VehicleState,
)
from modules.runtime.actions.step_vehicle import step_vehicle

HOME = GeoPoint(lat=37.0, lon=126.0)
SPEC = VehicleSpec(id="d1", name="d1", domain="air", speed_mps=15, endurance_min=40,
                   sensor_range_m=800, capabilities=[], home=HOME)  # fmt: skip


def ex(kind: str, go: str, **params) -> Exit:
    return Exit(cond=Condition(kind=kind, params=params), go_step=go)


PLAY = Play(id="p", name="p", domains=["air"], entry="patrol", approved=True, steps=[
    Step(id="patrol", name="순찰", do=Action(kind="hold"),
         on=[ex("battery_below", "home", pct=30), ex("target_found", "watch"),
             ex("arrived", "home")]),
    Step(id="watch", name="감시", do=Action(kind="watch_target", params={"target": "nearest"})),
    Step(id="home", name="귀환", do=Action(kind="return_home")),
])  # fmt: skip


def vs(step: str | None = "patrol", entered: bool = True, **kw) -> VehicleState:
    base = dict(id="d1", t_ms=0, pos=HOME, heading_deg=0, battery_pct=90, status="active",
                play_id="p", step_id=step, entered_step=entered)  # fmt: skip
    return VehicleState(**{**base, **kw})


def boat(seen_by: list[str], accum: int = 450_000) -> Target:
    return Target(id="boat1", kind="boat", pos=HOME, vel_east_mps=0, vel_north_mps=0,
                  first_seen_ms=0, last_seen_ms=0, seen_by=seen_by, threat_accum=accum)  # fmt: skip


def step(st: VehicleState, targets: list[Target] = ()) -> tuple:
    return step_vehicle(st, SPEC, PLAY, list(targets), 3000)


def test_new_step_is_entered_once_with_its_command():
    st, cmd, _ = step(vs(entered=False))
    assert st.entered_step and cmd.kind == "hold" and cmd.provenance.step_id == "patrol"


def test_first_true_exit_wins():
    st, cmd, _ = step(vs(battery_pct=20), [boat(["d1"])])
    assert (st.step_id, st.entered_step, cmd) == ("home", False, None)


def test_target_found_and_arrived():
    assert step(vs(), [boat(["d1"])])[0].step_id == "watch"
    assert step(vs(), [boat(["d2"])])[0].step_id == "patrol"
    assert step(vs(waypoint_idx=-1))[0].step_id == "home"


def test_target_found_while_patrolling_waits_until_the_threat_has_built_up():  # decision 0043
    assert step(vs(), [boat(["d1"], accum=449_999)])[0].step_id == "patrol"
    assert step(vs(), [boat(["d1"], accum=450_000)])[0].step_id == "watch"
    quiet, ready = boat(["d1"], accum=0), boat(["d1"]).model_copy(update={"id": "boat2"})
    assert step(vs(), [quiet, ready])[0].step_id == "watch"  # any one ready boat is enough


def test_target_found_while_patrolling_wants_a_boat_nobody_reported():  # decision 0036
    reported = boat(["d1"]).model_copy(update={"reported_by": "d2"})
    other = boat(["d1"]).model_copy(update={"id": "boat2"})
    for st in (vs(), vs(target_id="boat1")):  # an old target from before a hand-off is ignored
        assert step(st, [reported])[0].step_id == "patrol"
        assert step(st, [reported, other])[0].step_id == "watch"


TRACK = Play(id="t", name="t", domains=["air"], entry="track", approved=True, steps=[
    Step(id="track", name="추적", do=Action(kind="watch_target", params={"target": "operator"}),
         on=[ex("target_found", "ask")]),
    Step(id="ask", name="승인", do=Action(kind="hold")),
])  # fmt: skip


def test_target_found_while_tracking_waits_for_the_vehicle_s_own_target():  # tracking (0033)
    reported = boat(["d1"]).model_copy(update={"reported_by": "d2"})
    other = boat(["d1"]).model_copy(update={"id": "boat2"})
    st = vs(step="track", play_id="t", target_id="boat1")
    assert step_vehicle(st, SPEC, TRACK, [reported], 3000)[0].step_id == "ask"
    assert step_vehicle(st, SPEC, TRACK, [other], 3000)[0].step_id == "track"


def test_waits_while_a_decision_is_pending_or_not_ready_or_active():
    for st in (
        vs(waypoint_idx=-1, pending_report_id="r1"),
        vs(waypoint_idx=-1, status="returning"),
    ):
        assert step(st) == (st, None, None)


def test_direct_control_arrival_resumes_the_saved_step():
    st, cmd, rep = step(vs(step=None, waypoint_idx=-1, resume_play_id="p", resume_step_id="patrol"))
    assert (st.step_id, st.entered_step, st.resume_step_id, st.resume_play_id) == (
        "patrol", False, None, None)  # fmt: skip
    assert cmd is rep is None


def test_no_exit_true_keeps_the_step():
    st = vs()
    assert step(st) == (st, None, None)


TIMED = Play(id="p", name="p", domains=["air"], entry="patrol", approved=True, steps=[
    Step(id="patrol", name="순찰", do=Action(kind="hold"), on=[ex("at_time", "home", offset_ms=60_000)]),
    Step(id="home", name="귀환", do=Action(kind="return_home")),
])  # fmt: skip
START = 1_000_000


def test_at_time_fires_at_its_T_plus_offset():  # decision 0045
    before, _, _ = step_vehicle(vs(), SPEC, TIMED, [], START + 59_999, START)
    after, _, _ = step_vehicle(vs(), SPEC, TIMED, [], START + 60_000, START)
    assert before.step_id == "patrol" and after.step_id == "home"


def test_at_time_without_the_operation_start_never_fires():
    st, _, _ = step_vehicle(vs(), SPEC, TIMED, [], START + 10**9)
    assert st.step_id == "patrol"
