from contracts.models import Action, GeoPoint, Injection, Play, Step, VehicleState
from modules.runtime.actions.apply_injection import apply_injection

HOME = Play(id="go_home", name="h", domains=["air", "sea"], entry="home",
            steps=[Step(id="home", name="h", do=Action(kind="return_home"))])  # fmt: skip


def vs(vid: str) -> VehicleState:
    return VehicleState(id=vid, t_ms=0, pos=GeoPoint(lat=37, lon=126), heading_deg=0,
                        battery_pct=90, status="active", play_id="watch", step_id="w2",
                        entered_step=True)  # fmt: skip


def test_approved_switch_moves_listed_vehicles_to_the_new_play_entry():
    inj = Injection(id="inj1", t_ms=0, label="전체 귀환", status="approved",
                    play_by_vehicle={"d1": "go_home", "usv": "go_home"})  # fmt: skip
    d1, d2, usv = apply_injection([vs("d1"), vs("d2"), vs("usv")], {"go_home": HOME}, inj)
    assert (d1.play_id, d1.step_id, d1.entered_step) == ("go_home", "home", False)
    assert usv.play_id == "go_home" and usv.resume_play_id is None  # no automatic return
    assert d2 == vs("d2")
