from contracts.models import (
    Action,
    Choice,
    Condition,
    Decision,
    Exit,
    GeoPoint,
    Report,
    Role,
    Step,
    VehicleState,
)
from modules.runtime.actions.apply_decision import apply_decision


def role(pid: str) -> Role:
    return Role(id=pid, name=pid, domains=["air", "sea", "ground"], entry=f"{pid}-1",
                steps=[Step(id=f"{pid}-1", name="1", do=Action(kind="hold"))])  # fmt: skip


ROLES = {p: role(p) for p in ("patrol_a", "standby", "watch", "approach", "landing", "patrol_b")}


def vs(vid: str, role_id: str, **kw) -> VehicleState:
    return VehicleState(id=vid, t_ms=0, pos=GeoPoint(lat=37, lon=126), heading_deg=0,
                        battery_pct=90, status="active", role_id=role_id,
                        step_id=f"{role_id}-2", entered_step=True, **kw)  # fmt: skip


APPROACH = Choice(id="approach", label="접근",
                  role_by_vehicle={"d1": "watch", "usv": "approach", "ugv": "landing",
                                   "d2": "patrol_b"})  # fmt: skip
CARD = Report(id="r1", t_ms=0, kind="target_detected", vehicle_id="d1", text="보트",
              choices=[APPROACH, Choice(id="ignore", label="무시")])  # fmt: skip


def decide(choice: str, report_id: str = "r1") -> Decision:
    return Decision(id="dec1", t_ms=660_000, report_id=report_id, choice_id=choice)


def test_one_choice_switches_four_vehicles_at_once():
    states = [vs("d1", "patrol_a", pending_report_id="r1"), vs("d2", "standby"),
              vs("d3", "standby"), vs("usv", "standby"), vs("ugv", "standby")]  # fmt: skip
    out, reports = apply_decision(states, ROLES, decide("approach"), [CARD])
    got = {s.id: (s.role_id, s.step_id, s.entered_step) for s in out}
    assert got["d1"] == ("watch", "watch-1", False)
    assert got["usv"] == ("approach", "approach-1", False)
    assert got["ugv"] == ("landing", "landing-1", False)
    assert got["d2"] == ("patrol_b", "patrol_b-1", False)
    assert out[2] == states[2]  # d3 not in the choice
    assert out[0].pending_report_id is None
    assert (reports[0].resolved_ms, reports[0].decision_id) == (660_000, "dec1")


def test_choice_without_the_reporter_just_releases_it():
    out, _ = apply_decision([vs("d1", "patrol_a", pending_report_id="r1")], ROLES, decide("ignore"),
                            [CARD])  # fmt: skip
    assert (out[0].role_id, out[0].pending_report_id) == ("patrol_a", None)


def test_choice_without_the_reporter_follows_its_operator_choice_exit():
    # Decision 0031: the reporter stays in its role and takes the exit named by the chosen choice.
    go = Exit(cond=Condition(kind="operator_choice", params={"choice": "go"}), go_step="approach")
    draft = Role(id="draft", name="d", domains=["air"], entry="report", steps=[
        Step(id="report", name="보고", do=Action(kind="hold"), on=[go]),
        Step(id="approach", name="접근", do=Action(kind="approach_target"))])  # fmt: skip
    card = Report(id="r3", t_ms=0, kind="target_detected", vehicle_id="d1", text="보트",
                  choices=[Choice(id="go", label="접근 승인")])  # fmt: skip
    st = vs("d1", "draft", pending_report_id="r3").model_copy(update={"step_id": "report"})
    out, _ = apply_decision([st], {**ROLES, "draft": draft}, decide("go", "r3"), [card])
    got = (out[0].role_id, out[0].step_id, out[0].entered_step, out[0].pending_report_id)
    assert got == ("draft", "approach", False, None)


def test_target_select_sets_the_target_and_reenters_the_step():
    card = Report(id="r2", t_ms=0, kind="target_select", vehicle_id="d1", text="표적",
                  choices=[Choice(id="boat1", label="b"), Choice(id="fast1", label="f")])  # fmt: skip
    st = vs("d1", "watch", pending_report_id="r2")
    out, reports = apply_decision([st], ROLES, decide("fast1", "r2"), [CARD, card])
    assert (out[0].target_id, out[0].pending_report_id, out[0].entered_step) == (
        "fast1",
        None,
        False,
    )
    assert out[0].step_id == st.step_id
    assert reports[0].resolved_ms is None and reports[1].decision_id == "dec1"


STRIKE_BOTH = Choice(id="strike_both", label="함께 타격",
                     role_by_vehicle={"d2": "strike", "usv": "strike"})  # fmt: skip
ASK_D2 = Report(id="r-d2", t_ms=0, kind="target_detected", vehicle_id="d2", target_id="fast1",
                text="타격 승인 요청", choices=[STRIKE_BOTH])  # fmt: skip
ASK_USV = Report(id="r-usv", t_ms=0, kind="target_detected", vehicle_id="usv", target_id="fast1",
                 text="타격 승인 요청", choices=[STRIKE_BOTH])  # fmt: skip


def _strike_world():
    roles = {**ROLES, "strike": role("strike")}
    states = [vs("d2", "track_fast", pending_report_id="r-d2", target_id="fast1"),
              vs("usv", "track_fast_sea", pending_report_id="r-usv", target_id="fast1")]  # fmt: skip
    return roles, states


def test_moved_vehicles_carry_the_decision_and_the_card_target():
    roles, states = _strike_world()
    out, _ = apply_decision(states, roles, decide("strike_both", "r-d2"), [ASK_D2, ASK_USV])
    got = {s.id: (s.role_id, s.decision_id, s.target_id) for s in out}
    assert got == {"d2": ("strike", "dec1", "fast1"), "usv": ("strike", "dec1", "fast1")}


def test_moved_vehicles_open_cards_close():
    roles, states = _strike_world()
    _, reports = apply_decision(states, roles, decide("strike_both", "r-d2"), [ASK_D2, ASK_USV])
    assert [(r.id, r.resolved_ms, r.decision_id) for r in reports] == [
        ("r-d2", 660_000, "dec1"),
        ("r-usv", 660_000, "dec1"),
    ]


def test_operator_choice_exit_records_the_decision_for_a_strike_step():
    # Decision 0031 path + 0033: "approve, then strike" inside one role carries this decision id,
    # replacing any older one, so safety sees who approved this strike.
    go = Exit(cond=Condition(kind="operator_choice", params={"choice": "strike"}), go_step="hit")
    draft = Role(id="draft", name="d", domains=["air"], entry="ask", steps=[
        Step(id="ask", name="승인", do=Action(kind="hold"), on=[go]),
        Step(id="hit", name="타격", do=Action(kind="strike_target", params={"target": "operator"}))])  # fmt: skip
    card = Report(id="r4", t_ms=0, kind="target_detected", vehicle_id="d2", target_id="fast1",
                  text="타격 승인 요청", choices=[Choice(id="strike", label="타격")])  # fmt: skip
    st = vs("d2", "draft", pending_report_id="r4", decision_id="dec-old").model_copy(
        update={"step_id": "ask"}
    )
    out, _ = apply_decision([st], {**ROLES, "draft": draft}, decide("strike", "r4"), [card])
    assert (out[0].step_id, out[0].decision_id) == ("hit", "dec1")


def test_choice_target_by_vehicle_sets_each_moved_vehicles_target():  # fleet choices "함께 감시"
    from contracts.models import Choice, Decision, Report

    watch = Role(id="watch", name="w", domains=["air"], entry="w", approved=True,
                 steps=[Step(id="w", name="w", do=Action(kind="watch_target", params={"target": "operator"}))])  # fmt: skip
    st = VehicleState(id="d3", t_ms=0, pos=GeoPoint(lat=37.95, lon=124.7), heading_deg=0,
                      battery_pct=100, status="ready")  # fmt: skip
    ch = Choice(
        id="join_d3_d2",
        label="j",
        role_by_vehicle={"d3": "watch"},
        target_by_vehicle={"d3": "boat2"},
    )
    card = Report(id="r1", t_ms=0, kind="target_detected", vehicle_id="d1", target_id="boat1",
                  text="t", choices=[ch])  # fmt: skip
    out, _ = apply_decision([st], {"watch": watch}, Decision(id="dec-9", t_ms=5, report_id="r1",
                            choice_id="join_d3_d2"), [card])  # fmt: skip
    assert (out[0].role_id, out[0].target_id) == ("watch", "boat2")
