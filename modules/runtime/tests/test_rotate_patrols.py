from contracts.models import (
    Action,
    Assignment,
    GeoPoint,
    Operation,
    Play,
    Polygon,
    Step,
    VehicleSpec,
    VehicleState,
)
from modules.runtime.actions.rotate_patrols import rotate_patrols
from shared.geo import offset_latlon

HOME = GeoPoint(lat=37.95, lon=124.70)
SPECS = {
    v: VehicleSpec(id=v, name=v, domain="air", speed_mps=15, endurance_min=90, sensor_range_m=800,
                   capabilities=["patrol_route", "return_home", "hold"], home=HOME, recharge_min=10)
    for v in ("d1", "d2", "d3")
}  # fmt: skip
ROUTE = [{"lat": 38.0, "lon": 124.6 + i / 100} for i in range(4)]


def _play(pid: str, kind: str, **params) -> Play:
    step = Step(id="s", name="s", do=Action(kind=kind, params=params))
    return Play(id=pid, name=pid, domains=["air"], steps=[step], entry="s", approved=True)


PLAYS = {
    "coast_a": _play("coast_a", "patrol_route", route=ROUTE),
    "coast_b": _play("coast_b", "patrol_route", route=ROUTE),
    "go_home": _play("go_home", "return_home"),
    "standby": _play("standby", "hold"),
}
SQ = Polygon(points=[GeoPoint(lat=37.9, lon=124.5), GeoPoint(lat=38.1, lon=124.5),
                     GeoPoint(lat=38.1, lon=124.9)])  # fmt: skip
OP = Operation(id="op", name="op", area=SQ, zone=SQ, vehicle_ids=["d1", "d2", "d3"],
               rotation=["d1", "d2", "d3"], rotation_plays=["coast_a", "coast_b"])  # fmt: skip


def _at(north_m: float) -> GeoPoint:
    lat, lon = offset_latlon(HOME.lat, HOME.lon, 0, north_m)
    return GeoPoint(lat=lat, lon=lon)


def vs(vid, play, battery=100.0, north_m=0.0, status="active", wp=0) -> VehicleState:
    return VehicleState(id=vid, t_ms=0, pos=_at(north_m), heading_deg=0, battery_pct=battery,
                        status=status, play_id=play, step_id="s", entered_step=True,
                        waypoint_idx=wp)  # fmt: skip


def fleet(d1_battery=49.0, d3_status="ready", d3_north=0.0, d3_play="standby", d1_wp=2):
    return [vs("d1", "coast_a", d1_battery, 6000, wp=d1_wp), vs("d2", "coast_b", 90, 3000),
            vs("d3", d3_play, 100, d3_north, d3_status)]  # fmt: skip


def run(states, assignments=(), op=OP):
    out, asg = rotate_patrols(states, SPECS, op, PLAYS, list(assignments), 5000)
    return {s.id: s for s in out}, asg


START = Assignment(vehicle_id="d3", play_id="coast_a", since_ms=0, reason="교대 출발: d3 → d1 @2")


def test_no_rotation_returns_input():
    states = fleet()
    out, asg = rotate_patrols(states, SPECS, OP.model_copy(update={"rotation": []}), PLAYS, [], 0)
    assert out == states and asg == []


def test_relief_starts_at_the_threshold():
    by, asg = run(fleet())
    assert by["d3"].play_id == "coast_a" and by["d1"].play_id == "coast_a"
    assert [a.reason for a in asg] == ["교대 출발: d3 → d1 @2"]


def test_no_relief_before_the_threshold():
    by, asg = run(fleet(d1_battery=60))
    assert by["d3"].play_id == "standby" and asg == []


def test_relief_and_outgoing_meet_at_the_fixed_waypoint():
    by, _ = run(fleet(d3_play="coast_a", d1_wp=3), [START])
    assert (by["d1"].waypoint_idx, by["d3"].waypoint_idx) == (2, 2)


def test_handover_within_500_m_sends_outgoing_home():
    by, asg = run(fleet(d3_play="coast_a", d3_north=5700), [START])
    assert by["d1"].play_id == "go_home" and by["d3"].play_id == "coast_a"
    assert "교대 완료: d3 ← d1" in [a.reason for a in asg]
    assert not any(a.reason.startswith("교대 출발") for a in asg)


def test_no_ready_relief_keeps_patrolling():
    by, asg = run(fleet(d3_status="maintenance"))
    assert by["d1"].play_id == "coast_a" and asg == []


def test_no_relief_still_goes_home_at_the_floor():
    by, asg = run(fleet(d1_battery=36, d3_status="maintenance"))
    assert by["d1"].play_id == "go_home"
    assert [a.reason for a in asg] == ["교대 귀환(하한선): d1"]


def test_two_on_one_play_without_relief_record_is_not_a_handover():
    by, asg = run(fleet(d1_battery=90, d3_play="coast_a", d3_north=5900))
    assert by["d1"].play_id == "coast_a" and by["d3"].play_id == "coast_a" and asg == []
