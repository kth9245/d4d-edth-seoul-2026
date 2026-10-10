from contracts.models import Action, EmergencyRules, GeoPoint, Role, Step, VehicleState
from modules.runtime.actions.apply_emergency import apply_emergency

STEPS = [Step(id="s1", name="s1", do=Action(kind="hold")),
         Step(id="home", name="home", do=Action(kind="return_home"))]  # fmt: skip
ROLES = {
    "watch": Role(id="watch", name="w", domains=["air"], steps=STEPS, entry="s1",
                  emergency=EmergencyRules(battery_low_pct=30, battery_low_step="home")),
    "plain": Role(id="plain", name="p", domains=["air"], steps=STEPS, entry="s1"),
}  # fmt: skip


def vs(
    battery: float, role: str = "watch", step: str = "s1", status: str = "active"
) -> VehicleState:
    return VehicleState(id="d1", t_ms=0, pos=GeoPoint(lat=37, lon=126), heading_deg=0,
                        battery_pct=battery, status=status, role_id=role, step_id=step,
                        entered_step=True)  # fmt: skip


def test_low_battery_jumps_to_the_role_emergency_step():
    (out,) = apply_emergency([vs(25)], ROLES)
    assert (out.step_id, out.entered_step, out.emergency) == ("home", False, "battery_low")


def test_untouched_when_battery_ok_or_rule_does_not_apply():
    cases = [vs(50), vs(25, step="home"), vs(25, status="returning"), vs(25, role="plain")]
    assert apply_emergency(cases, ROLES) == cases
