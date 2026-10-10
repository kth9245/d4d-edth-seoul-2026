from contracts.models import Assignment, GeoPoint, VehicleState
from modules.gateway.actions.track_assignments import track_assignments

START = [Assignment(vehicle_id="d1", role_id="patrol_a", since_ms=0, reason="작전 배정"),
         Assignment(vehicle_id="d2", role_id="standby", since_ms=0, reason="작전 배정")]  # fmt: skip


def vs(vid: str, role_id: str) -> VehicleState:
    return VehicleState(id=vid, t_ms=0, pos=GeoPoint(lat=37, lon=126), heading_deg=0,
                        battery_pct=90, status="active", role_id=role_id)  # fmt: skip


def test_only_vehicles_whose_role_changed_get_a_new_assignment():
    before = {"d1": "patrol_a", "d2": "standby"}
    out = track_assignments(START, before, [vs("d1", "watch"), vs("d2", "standby")], 660_000,
                            "결정 dec-1")  # fmt: skip
    assert START[1] in out and len(out) == 2
    (new,) = [a for a in out if a.vehicle_id == "d1"]
    assert (new.role_id, new.since_ms, new.reason) == ("watch", 660_000, "결정 dec-1")


def test_nothing_changes_when_no_role_changed():
    before = {"d1": "patrol_a", "d2": "standby"}
    assert (
        track_assignments(START, before, [vs("d1", "patrol_a"), vs("d2", "standby")], 1, "x")
        == START
    )
