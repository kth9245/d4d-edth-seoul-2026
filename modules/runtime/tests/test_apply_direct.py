from contracts.models import DirectControl, GeoPoint, VehicleState
from modules.runtime.actions.apply_direct import apply_direct

G = GeoPoint(lat=37.05, lon=126.05)


def vs(vid: str, **kw) -> VehicleState:
    return VehicleState(id=vid, t_ms=0, pos=GeoPoint(lat=37, lon=126), heading_deg=0,
                        battery_pct=100, status="active", **kw)  # fmt: skip


def direct(vid: str = "d1") -> DirectControl:
    return DirectControl(id="dc1", vehicle_id=vid, target=G, t_ms=1000)


def test_operator_direct_move_command():
    _, cmd = apply_direct([vs("d1", play_id="p", step_id="s1")], direct(), 1000)
    assert (cmd.id, cmd.vehicle_id, cmd.kind) == ("cmd-d1-1000", "d1", "move")
    assert cmd.params == {"target": G.model_dump()}
    assert cmd.provenance.source == "operator_direct" and cmd.provenance.issued_ms == 1000


def test_vehicle_leaves_its_step_and_remembers_where_to_resume():
    states, _ = apply_direct([vs("d1", play_id="p", step_id="s2", waypoint_idx=-1),
                              vs("d2", play_id="q", step_id="t1")], direct(), 1000)  # fmt: skip
    d1, d2 = states
    assert (d1.step_id, d1.entered_step, d1.waypoint_idx) == (None, True, 0)
    assert (d1.resume_play_id, d1.resume_step_id) == ("p", "s2")
    assert d2 == vs("d2", play_id="q", step_id="t1")


def test_second_direct_keeps_the_first_resume_point():
    first, _ = apply_direct([vs("d1", play_id="p", step_id="s2")], direct(), 1000)
    again, _ = apply_direct(first, direct(), 2000)
    assert (again[0].resume_play_id, again[0].resume_step_id) == ("p", "s2")
