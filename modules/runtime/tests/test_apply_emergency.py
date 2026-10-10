from contracts.models import Action, EmergencyRules, GeoPoint, Play, Step, VehicleState
from modules.runtime.actions.apply_emergency import apply_emergency

STEPS = [Step(id="s1", name="s1", do=Action(kind="hold")),
         Step(id="home", name="home", do=Action(kind="return_home"))]  # fmt: skip
PLAYS = {
    "watch": Play(id="watch", name="w", domains=["air"], steps=STEPS, entry="s1",
                  emergency=EmergencyRules(battery_low_pct=30, battery_low_step="home")),
    "plain": Play(id="plain", name="p", domains=["air"], steps=STEPS, entry="s1"),
}  # fmt: skip


def vs(
    battery: float, play: str = "watch", step: str = "s1", status: str = "active"
) -> VehicleState:
    return VehicleState(id="d1", t_ms=0, pos=GeoPoint(lat=37, lon=126), heading_deg=0,
                        battery_pct=battery, status=status, play_id=play, step_id=step,
                        entered_step=True)  # fmt: skip


def test_low_battery_jumps_to_the_play_emergency_step():
    (out,) = apply_emergency([vs(25)], PLAYS)
    assert (out.step_id, out.entered_step, out.emergency) == ("home", False, "battery_low")


def test_untouched_when_battery_ok_or_rule_does_not_apply():
    cases = [vs(50), vs(25, step="home"), vs(25, status="returning"), vs(25, play="plain")]
    assert apply_emergency(cases, PLAYS) == cases
