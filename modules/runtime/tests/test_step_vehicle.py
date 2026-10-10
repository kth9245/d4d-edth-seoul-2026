from contracts.models import (
    Action,
    Condition,
    Exit,
    GeoPoint,
    Role,
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


ROLE = Role(id="p", name="p", domains=["air"], entry="patrol", approved=True, steps=[
    Step(id="patrol", name="순찰", do=Action(kind="hold"),
         on=[ex("battery_below", "home", pct=30), ex("target_found", "watch"),
             ex("arrived", "home")]),
    Step(id="watch", name="감시", do=Action(kind="watch_target", params={"target": "nearest"})),
    Step(id="home", name="귀환", do=Action(kind="return_home")),
])  # fmt: skip


def vs(step: str | None = "patrol", entered: bool = True, **kw) -> VehicleState:
    base = dict(id="d1", t_ms=0, pos=HOME, heading_deg=0, battery_pct=90, status="active",
                role_id="p", step_id=step, entered_step=entered)  # fmt: skip
    return VehicleState(**{**base, **kw})


def boat(seen_by: list[str], accum: int = 450_000) -> Target:
    return Target(id="boat1", kind="boat", pos=HOME, vel_east_mps=0, vel_north_mps=0,
                  first_seen_ms=0, last_seen_ms=0, seen_by=seen_by, threat_accum=accum)  # fmt: skip


def step(st: VehicleState, targets: list[Target] = ()) -> tuple:
    return step_vehicle(st, SPEC, ROLE, list(targets), 3000)


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


TRACK = Role(id="t", name="t", domains=["air"], entry="track", approved=True, steps=[
    Step(id="track", name="추적", do=Action(kind="watch_target", params={"target": "operator"}),
         on=[ex("target_found", "ask")]),
    Step(id="ask", name="승인", do=Action(kind="hold")),
])  # fmt: skip


def test_target_found_while_tracking_waits_for_the_vehicle_s_own_target():  # tracking (0033)
    reported = boat(["d1"]).model_copy(update={"reported_by": "d2"})
    other = boat(["d1"]).model_copy(update={"id": "boat2"})
    st = vs(step="track", role_id="t", target_id="boat1")
    assert step_vehicle(st, SPEC, TRACK, [reported], 3000)[0].step_id == "ask"
    assert step_vehicle(st, SPEC, TRACK, [other], 3000)[0].step_id == "track"


def test_waits_while_a_decision_is_pending_or_not_ready_or_active():
    for st in (
        vs(waypoint_idx=-1, pending_report_id="r1"),
        vs(waypoint_idx=-1, status="returning"),
    ):
        assert step(st) == (st, None, None)


def test_direct_control_arrival_resumes_the_saved_step():
    st, cmd, rep = step(vs(step=None, waypoint_idx=-1, resume_role_id="p", resume_step_id="patrol"))
    assert (st.step_id, st.entered_step, st.resume_step_id, st.resume_role_id) == (
        "patrol", False, None, None)  # fmt: skip
    assert cmd is rep is None


def test_no_exit_true_keeps_the_step():
    st = vs()
    assert step(st) == (st, None, None)


TIMED = Role(id="p", name="p", domains=["air"], entry="patrol", approved=True, steps=[
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


NEUTRAL = Role(id="n", name="n", domains=["air"], entry="watch", approved=True, steps=[
    Step(id="watch", name="감시", do=Action(kind="watch_target", params={"target": "operator"}),
         on=[ex("target_neutralized", "after")]),
    Step(id="after", name="무력화 뒤", do=Action(kind="hold")),
])  # fmt: skip


def test_target_neutralized_waits_for_my_own_target_to_be_struck():  # decision 0066
    struck = boat(["d1"]).model_copy(update={"neutralized_ms": 5000})
    other = boat(["d1"]).model_copy(update={"id": "boat2", "neutralized_ms": 5000})
    st = vs(step="watch", role_id="n", target_id="boat1")
    assert step_vehicle(st, SPEC, NEUTRAL, [struck], 6000)[0].step_id == "after"
    assert step_vehicle(st, SPEC, NEUTRAL, [boat(["d1"])], 6000)[0].step_id == "watch"
    assert step_vehicle(st, SPEC, NEUTRAL, [other], 6000)[0].step_id == "watch"  # not my target


PATROL = Role(id="p", name="p", domains=["air"], entry="patrol", approved=True, steps=[
    Step(id="patrol", name="순찰", do=Action(kind="patrol_route", params={"route": []}),
         on=[ex("target_found", "watch")]),
    Step(id="watch", name="감시", do=Action(kind="watch_target", params={"target": "nearest"})),
])  # fmt: skip


def test_leaving_a_patrol_route_step_remembers_where_it_was():  # decision 0066
    out = step_vehicle(vs(waypoint_idx=7), SPEC, PATROL, [boat(["d1"])], 3000)[0]
    assert (out.step_id, out.patrol_step_id, out.patrol_idx) == ("watch", "patrol", 7)


def test_leaving_any_other_step_remembers_nothing():
    out = step(vs(waypoint_idx=7), [boat(["d1"])])[0]  # ROLE's patrol step does `hold`
    assert (out.step_id, out.patrol_step_id, out.patrol_idx) == ("watch", None, 0)


def test_coming_back_to_the_patrol_step_continues_from_where_it_was_left():  # decision 0066
    left = vs(step="patrol", entered=False, patrol_step_id="patrol", patrol_idx=7)
    out, cmd, _ = step_vehicle(left, SPEC, PATROL, [], 3000)
    assert (out.waypoint_idx, out.patrol_step_id, out.patrol_idx) == (7, None, 0)  # used once
    assert out.entered_step and cmd is not None  # the step's command still goes out


def test_another_step_or_a_fresh_start_begins_at_the_first_waypoint():
    other = vs(step="patrol", entered=False, patrol_step_id="elsewhere", patrol_idx=7)
    out = step_vehicle(other, SPEC, PATROL, [], 3000)[0]
    assert (out.waypoint_idx, out.patrol_step_id, out.patrol_idx) == (0, "elsewhere", 7)
    assert (
        step_vehicle(vs(step="patrol", entered=False), SPEC, PATROL, [], 3000)[0].waypoint_idx == 0
    )
    held = vs(step="patrol", entered=False, patrol_step_id="patrol", patrol_idx=7)
    assert step_vehicle(held, SPEC, ROLE, [], 3000)[0].waypoint_idx == 0  # ROLE's patrol only holds


RESIGHT = Role(id="s", name="s", domains=["air"], entry="patrol", approved=True, steps=[
    Step(id="patrol", name="순찰", do=Action(kind="patrol_route", params={"route": []}),
         on=[ex("target_resighted", "assist")]),
    Step(id="assist", name="함께 관측", do=Action(kind="watch_target", params={"target": "operator"})),
])  # fmt: skip


def reported(by: str = "d2", seen_by: tuple = ("d1",), **kw) -> Target:
    return boat(list(seen_by)).model_copy(update={"reported_by": by, **kw})


def test_target_resighted_stops_at_a_site_another_vehicle_reported():  # decision 0066
    out = step_vehicle(vs(role_id="s"), SPEC, RESIGHT, [reported()], 3000)[0]
    assert (out.step_id, out.target_id, out.entered_step) == ("assist", "boat1", False)


def test_target_resighted_ignores_everything_else():
    def stays(st, *targets):
        return step_vehicle(st, SPEC, RESIGHT, list(targets), 3000)[0].step_id == "patrol"

    assert stays(vs(role_id="s"), reported(by="d1"))  # my own report
    assert stays(vs(role_id="s"), boat(["d1"]))  # nobody reported it: target_found's job
    assert stays(vs(role_id="s"), reported(seen_by=("d2",)))  # I do not see it
    assert stays(vs(role_id="s", target_id="boat1"), reported())  # it is already my target
    assert stays(vs(role_id="s"), reported(threat_accum=449_999))  # the threat has not built up
