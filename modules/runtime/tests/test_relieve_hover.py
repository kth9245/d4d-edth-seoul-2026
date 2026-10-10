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
from modules.runtime.actions.relieve_hover import relieve_hover
from shared.geo import offset_latlon

HOME = GeoPoint(lat=37.95, lon=124.70)
SPECS = {
    v: VehicleSpec(id=v, name=v, domain="air", speed_mps=15, endurance_min=50, sensor_range_m=800,
                   capabilities=["watch_target", "return_home"], home=HOME, recharge_min=10)
    for v in ("d1", "d2", "d3", "d4")
}  # fmt: skip
SQ = Polygon(points=[GeoPoint(lat=37.9, lon=124.5), GeoPoint(lat=38.1, lon=124.5),
                     GeoPoint(lat=38.1, lon=124.9)])  # fmt: skip
OP = Operation(id="op", name="op", area=SQ, zone=SQ, vehicle_ids=list(SPECS), rotation=list(SPECS),
               rotation_plays=["coast_a", "coast_b"],
               rotation_pools={"coast_a": ["d1", "d3"], "coast_b": ["d2", "d4"]})  # fmt: skip


def _play(pid, *steps):
    return Play(
        id=pid, name=pid, domains=["air"], entry=steps[0].id, approved=True, steps=list(steps)
    )


PLAYS = {
    "coast_a": _play("coast_a", Step(id="patrol", name="p", do=Action(kind="patrol_route", params={"route": []})),
                     Step(id="report", name="r", do=Action(kind="watch_target", params={"target": "nearest"}))),
    "watch": _play("watch", Step(id="w", name="w", do=Action(kind="watch_target", params={"target": "operator"}))),
    "go_home": _play("go_home", Step(id="h", name="h", do=Action(kind="return_home"))),
}  # fmt: skip


def at(north_m):
    lat, lon = offset_latlon(HOME.lat, HOME.lon, 0, north_m)
    return GeoPoint(lat=lat, lon=lon)


def vs(vid, play, step, battery=100.0, north_m=0.0, status="active", target=None):
    return VehicleState(id=vid, t_ms=0, pos=at(north_m), heading_deg=0, battery_pct=battery, status=status,
                        play_id=play, step_id=step, entered_step=True, target_id=target)  # fmt: skip


def run(states, asg=()):
    out, a = relieve_hover(states, SPECS, OP, PLAYS, list(asg), 1000)
    return {s.id: s for s in out}, a


HOVER = vs("d1", "coast_a", "report", 49, 6000, target="boat1")


def test_hovering_drone_gets_a_watch_relief_on_the_same_target():
    by, asg = run(
        [HOVER, vs("d3", None, None, status="ready"), vs("d4", None, None, status="ready")]
    )
    assert (by["d3"].play_id, by["d3"].target_id) == ("watch", "boat1") and by["d4"].play_id is None
    assert [a.reason for a in asg] == ["감시 교대 출발: d3 → d1"]


def test_no_relief_before_the_threshold():
    by, asg = run(
        [HOVER.model_copy(update={"battery_pct": 70}), vs("d3", None, None, status="ready")]
    )
    assert by["d3"].play_id is None and asg == []


def test_relief_within_500_m_sends_the_hovering_drone_home():
    start = Assignment(
        vehicle_id="d3", play_id="watch", since_ms=0, reason="감시 교대 출발: d3 → d1"
    )
    by, asg = run([HOVER, vs("d3", "watch", "w", 99, 5700, target="boat1")], [start])
    assert by["d1"].play_id == "go_home" and by["d3"].play_id == "watch"
    assert "감시 교대 완료: d3 ← d1" in [a.reason for a in asg]


def test_patrolling_drone_is_not_a_hover():
    by, asg = run([vs("d1", "coast_a", "patrol", 40, 6000), vs("d3", None, None, status="ready")])
    assert by["d3"].play_id is None and asg == []
