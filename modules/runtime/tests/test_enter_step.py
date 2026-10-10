from contracts.models import (
    Action,
    Choice,
    GeoPoint,
    Play,
    ReportSpec,
    Step,
    Target,
    VehicleSpec,
    VehicleState,
)
from modules.runtime.actions.enter_step import enter_step

HOME = GeoPoint(lat=37.0, lon=126.0)


def spec(domain: str = "air") -> VehicleSpec:
    return VehicleSpec(id="d1", name="d1", domain=domain, speed_mps=15, endurance_min=40,
                       sensor_range_m=800, capabilities=[], home=HOME)  # fmt: skip


def vs(**kw) -> VehicleState:
    return VehicleState(id="d1", t_ms=0, pos=HOME, heading_deg=0, battery_pct=90,
                        status="active", play_id="p", step_id="s1", **kw)  # fmt: skip


def boat(tid: str, north_m: float, seen_by: tuple[str, ...] = ()) -> Target:
    pos = GeoPoint(lat=HOME.lat + north_m / 111_195, lon=HOME.lon)
    return Target(id=tid, kind="boat", pos=pos, vel_east_mps=0, vel_north_mps=0,
                  first_seen_ms=0, last_seen_ms=0, seen_by=list(seen_by))  # fmt: skip


def run(do: Action, targets=(), report: ReportSpec | None = None, domain: str = "air", **kw):
    step = Step(id="s1", name="s1", do=do, report=report)
    play = Play(id="p", name="p", domains=["air"], steps=[step], entry="s1", approved=True)
    return enter_step(vs(**kw), spec(domain), play, step, list(targets), 7000)


def test_nearest_target_becomes_target_id_of_the_command():
    st, cmd, rep = run(Action(kind="watch_target", params={"target": "nearest", "distance_m": 150}),
                       [boat("far", 3000), boat("near", 500)])  # fmt: skip
    assert (st.target_id, st.entered_step, st.waypoint_idx) == ("near", True, 0)
    assert cmd.kind == "orbit" and cmd.params == {"distance_m": 150, "target_id": "near"}
    p = cmd.provenance
    assert (p.source, p.play_id, p.step_id, p.issued_ms) == ("play_step", "p", "s1", 7000)
    assert cmd.id == "cmd-d1-7000" and rep is None


def test_nearest_prefers_a_boat_nobody_reported_yet():  # decision 0036
    near = boat("near", 300, ("d1",)).model_copy(update={"reported_by": "d2"})
    watch = Action(kind="watch_target", params={"target": "nearest"})
    assert run(watch, [near, boat("new", 600, ("d1",))])[0].target_id == "new"
    assert run(watch, [near])[0].target_id == "near"  # all reported: nearest of all


def test_operator_target_asks_with_a_target_select_card():
    st, cmd, rep = run(Action(kind="watch_target", params={"target": "operator"}),
                       [boat("boat1", 500), boat("fast1", 900)])  # fmt: skip
    assert cmd is None and rep.kind == "target_select" and rep.vehicle_id == "d1"
    assert [c.id for c in rep.choices] == ["boat1", "fast1"]
    assert st.pending_report_id == rep.id == "rep-d1-7000"


def test_operator_target_already_chosen_goes_ahead():
    st, cmd, rep = run(Action(kind="watch_target", params={"target": "operator"}),
                       [boat("fast1", 900)], target_id="fast1")  # fmt: skip
    assert cmd.params["target_id"] == "fast1" and rep is None and st.pending_report_id is None


def test_fixed_target_id():
    st, cmd, _ = run(Action(kind="approach_target", params={"target": "fast1"}), [boat("boat1", 1)])
    assert st.target_id == "fast1" and cmd.kind == "keep_distance"


def test_move_to_keeps_its_target_coordinates():
    dest = {"lat": 37.01, "lon": 126.01, "alt_m": 0}
    st, cmd, _ = run(Action(kind="move_to", params={"target": dest}))
    assert cmd.kind == "move" and cmd.params == {"target": dest} and st.target_id is None


def test_return_step_sets_returning():
    st, cmd, _ = run(Action(kind="return_home"))
    assert st.status == "returning" and cmd.kind == "return_home"


def test_report_with_choices_waits_for_a_decision():
    rs = ReportSpec(text="보트 발견", choices=[Choice(id="approach", label="접근")])
    st, _, rep = run(Action(kind="hold"), [boat("boat1", 500, ("d1",))], rs)
    assert (rep.kind, rep.target_id) == ("target_detected", "boat1")
    assert rep.text == "보트 발견 · d1 센서 탐지 · boat1(보트) · 500 m"
    assert st.pending_report_id == rep.id


def test_report_without_choices_does_not_wait():
    st, _, rep = run(Action(kind="hold"), report=ReportSpec(text="도착"))
    assert rep is not None and st.pending_report_id is None
    assert rep.text == "도착"  # no target, no basis


def test_no_command_when_the_domain_cannot_do_the_action():
    st, cmd, _ = run(Action(kind="watch_target", params={"target": "nearest"}), [boat("b", 1)],
                     domain="ground")  # fmt: skip
    assert cmd is None and st.entered_step


def test_strike_command_carries_decision_and_target_position():
    tg = boat("fast1", 900)
    st, cmd, rep = run(Action(kind="strike_target", params={"target": "operator", "distance_m": 0}),
                       [tg], domain="sea", target_id="fast1", decision_id="dec-3")  # fmt: skip
    assert cmd.kind == "strike" and cmd.provenance.decision_id == "dec-3"
    assert cmd.params == {"distance_m": 0, "target_id": "fast1", "target": tg.pos.model_dump()}
    assert rep is None and st.target_id == "fast1"


def test_report_card_names_the_tracked_target():
    ask = ReportSpec(text="타격 승인 요청", choices=[Choice(id="strike_d2", label="타격")])
    st, cmd, rep = run(Action(kind="watch_target", params={"target": "operator", "distance_m": 300}),
                       [boat("boat1", 300, ("d1",)), boat("fast1", 600, ("d1",))],
                       report=ask, target_id="fast1")  # fmt: skip
    assert rep.target_id == "fast1" and st.pending_report_id == rep.id
    assert rep.text == "타격 승인 요청 · d1 센서 탐지 · fast1(보트) · 600 m"


def test_card_basis_says_tracking_when_the_vehicle_has_not_seen_the_target():
    ask = ReportSpec(text="타격 승인 요청", choices=[Choice(id="strike_d2", label="타격")])
    _, _, rep = run(Action(kind="watch_target", params={"target": "operator", "distance_m": 300}),
                    [boat("fast1", 1000)], report=ask, target_id="fast1")  # fmt: skip
    assert rep.text == "타격 승인 요청 · d1 추적 중 · fast1(보트) · 1000 m"
