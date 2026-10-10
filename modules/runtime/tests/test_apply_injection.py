from contracts.models import Action, GeoPoint, Injection, Role, Step, VehicleState
from modules.runtime.actions.apply_injection import apply_injection

HOME = Role(id="go_home", name="h", domains=["air", "sea"], entry="home",
            steps=[Step(id="home", name="h", do=Action(kind="return_home"))])  # fmt: skip


def vs(vid: str) -> VehicleState:
    return VehicleState(id=vid, t_ms=0, pos=GeoPoint(lat=37, lon=126), heading_deg=0,
                        battery_pct=90, status="active", role_id="watch", step_id="w2",
                        entered_step=True)  # fmt: skip


def test_approved_switch_moves_listed_vehicles_to_the_new_role_entry():
    inj = Injection(id="inj1", t_ms=0, label="전체 귀환", status="approved",
                    role_by_vehicle={"d1": "go_home", "usv": "go_home"})  # fmt: skip
    d1, d2, usv = apply_injection([vs("d1"), vs("d2"), vs("usv")], {"go_home": HOME}, inj)
    assert (d1.role_id, d1.step_id, d1.entered_step) == ("go_home", "home", False)
    assert usv.role_id == "go_home" and usv.resume_role_id is None  # no automatic return
    assert d2 == vs("d2")


WATCH = Role(id="watch", name="표적 감시", domains=["air"], entry="w1",
             steps=[Step(id="w1", name="w", do=Action(kind="watch_target"))])  # fmt: skip


def test_pointing_switch_records_the_target():
    # decision 0048: the operator pointed d2 at boat1 with a role; the vehicle works that target
    inj = Injection(id="inj2", t_ms=0, label="표적 감시: d2 → boat1", status="approved",
                    role_by_vehicle={"d2": "watch"}, target_by_vehicle={"d2": "boat1"})  # fmt: skip
    (d2,) = apply_injection([vs("d2")], {"watch": WATCH}, inj)
    assert (d2.role_id, d2.step_id, d2.target_id) == ("watch", "w1", "boat1")
