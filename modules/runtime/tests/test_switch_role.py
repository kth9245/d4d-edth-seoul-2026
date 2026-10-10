from contracts.models import Action, GeoPoint, Role, Step, VehicleState
from modules.runtime.actions.switch_role import switch_role

ROLE = Role(id="watch", name="w", domains=["air"], entry="s1",
            steps=[Step(id="s1", name="s1", do=Action(kind="hold"))])  # fmt: skip


def test_switch_starts_the_new_role_from_its_entry_and_clears_step_state():
    st = VehicleState(id="d1", t_ms=9, pos=GeoPoint(lat=37, lon=126), heading_deg=90,
                      battery_pct=55, status="active", role_id="patrol_a", step_id="s3",
                      entered_step=True, waypoint_idx=-1, target_id="boat1",
                      pending_report_id="r1", resume_role_id="x", resume_step_id="y")  # fmt: skip
    out = switch_role(st, ROLE)
    assert (out.role_id, out.step_id, out.entered_step, out.waypoint_idx) == (
        "watch",
        "s1",
        False,
        0,
    )
    assert (
        out.target_id is out.pending_report_id is out.resume_role_id is out.resume_step_id is None
    )
    assert (out.battery_pct, out.pos, out.heading_deg, out.t_ms) == (55, st.pos, 90, 9)


def test_switch_clears_decision_id():
    st = VehicleState(id="d2", t_ms=0, pos=GeoPoint(lat=37, lon=126), heading_deg=0,
                      battery_pct=80, status="active", decision_id="dec-3")  # fmt: skip
    assert switch_role(st, ROLE).decision_id is None
