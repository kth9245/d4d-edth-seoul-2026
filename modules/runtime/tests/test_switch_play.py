from contracts.models import Action, GeoPoint, Play, Step, VehicleState
from modules.runtime.actions.switch_play import switch_play

PLAY = Play(id="watch", name="w", domains=["air"], entry="s1",
            steps=[Step(id="s1", name="s1", do=Action(kind="hold"))])  # fmt: skip


def test_switch_starts_the_new_play_from_its_entry_and_clears_step_state():
    st = VehicleState(id="d1", t_ms=9, pos=GeoPoint(lat=37, lon=126), heading_deg=90,
                      battery_pct=55, status="active", play_id="patrol_a", step_id="s3",
                      entered_step=True, waypoint_idx=-1, target_id="boat1",
                      pending_report_id="r1", resume_play_id="x", resume_step_id="y")  # fmt: skip
    out = switch_play(st, PLAY)
    assert (out.play_id, out.step_id, out.entered_step, out.waypoint_idx) == (
        "watch",
        "s1",
        False,
        0,
    )
    assert (
        out.target_id is out.pending_report_id is out.resume_play_id is out.resume_step_id is None
    )
    assert (out.battery_pct, out.pos, out.heading_deg, out.t_ms) == (55, st.pos, 90, 9)
