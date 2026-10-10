from contracts.models import (
    Action,
    Assignment,
    GeoPoint,
    Operation,
    Polygon,
    Role,
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


def _role(pid: str, kind: str, **params) -> Role:
    step = Step(id="s", name="s", do=Action(kind=kind, params=params))
    return Role(id=pid, name=pid, domains=["air"], steps=[step], entry="s", approved=True)


ROLES = {
    "coast_a": _role("coast_a", "patrol_route", route=ROUTE),
    "coast_b": _role("coast_b", "patrol_route", route=ROUTE),
    "go_home": _role("go_home", "return_home"),
    "standby": _role("standby", "hold"),
}
SQ = Polygon(points=[GeoPoint(lat=37.9, lon=124.5), GeoPoint(lat=38.1, lon=124.5),
                     GeoPoint(lat=38.1, lon=124.9)])  # fmt: skip
OP = Operation(id="op", name="op", area=SQ, zone=SQ, vehicle_ids=["d1", "d2", "d3"],
               rotation=["d1", "d2", "d3"], rotation_roles=["coast_a", "coast_b"])  # fmt: skip


def _at(north_m: float) -> GeoPoint:
    lat, lon = offset_latlon(HOME.lat, HOME.lon, 0, north_m)
    return GeoPoint(lat=lat, lon=lon)


def vs(vid, role, battery=100.0, north_m=0.0, status="active", wp=0) -> VehicleState:
    return VehicleState(id=vid, t_ms=0, pos=_at(north_m), heading_deg=0, battery_pct=battery,
                        status=status, role_id=role, step_id="s", entered_step=True,
                        waypoint_idx=wp)  # fmt: skip


def fleet(d1_battery=49.0, d3_status="ready", d3_north=0.0, d3_role="standby", d1_wp=2):
    return [vs("d1", "coast_a", d1_battery, 6000, wp=d1_wp), vs("d2", "coast_b", 90, 3000),
            vs("d3", d3_role, 100, d3_north, d3_status)]  # fmt: skip


def run(states, assignments=(), op=OP):
    out, asg = rotate_patrols(states, SPECS, op, ROLES, list(assignments), 5000)
    return {s.id: s for s in out}, asg


START = Assignment(vehicle_id="d3", role_id="coast_a", since_ms=0, reason="교대 출발: d3 → d1 @2")


def test_no_rotation_returns_input():
    states = fleet()
    out, asg = rotate_patrols(states, SPECS, OP.model_copy(update={"rotation": []}), ROLES, [], 0)
    assert out == states and asg == []


def test_relief_starts_at_the_threshold():
    by, asg = run(fleet())
    assert by["d3"].role_id == "coast_a" and by["d1"].role_id == "coast_a"
    assert [a.reason for a in asg] == ["교대 출발: d3 → d1 @2"]


def test_no_relief_before_the_threshold():
    by, asg = run(fleet(d1_battery=60))
    assert by["d3"].role_id == "standby" and asg == []


def test_a_far_relief_starts_early_enough_to_meet_before_the_floor():  # user, 10/10: no floor return
    # d1 has 62%: above the 35% threshold, 23.6% over the floor. A relief 6 km south of base needs about
    # 15.6 min (17.3% + 7% spare) to point 2, more than that margin, so it leaves now; one at base
    # (9.4 min: 10.4% + 7%) waits.
    by, asg = run(fleet(d1_battery=62, d3_north=-6000))
    assert by["d3"].role_id == "coast_a" and [a.reason for a in asg] == ["교대 출발: d3 → d1 @2"]
    by, asg = run(fleet(d1_battery=62))
    assert by["d3"].role_id == "standby" and asg == []


def test_outgoing_keeps_patrolling_while_the_relief_flies_to_point_m():  # never stops (user)
    by, _ = run(fleet(d3_role="coast_a", d1_wp=3), [START])
    assert (by["d1"].waypoint_idx, by["d3"].waypoint_idx) == (3, 2)
    assert by["d1"].role_id == "coast_a"


def test_handover_when_the_relief_reaches_point_m_sends_outgoing_home():
    states = fleet(d3_role="coast_a", d1_wp=3)
    p2 = ROUTE[2]
    states[2] = states[2].model_copy(update={"pos": GeoPoint(lat=p2["lat"] - 0.003, lon=p2["lon"])})
    by, asg = run(states, [START])
    assert by["d1"].role_id == "go_home" and by["d3"].role_id == "coast_a"
    assert "교대 완료: d3 ← d1" in [a.reason for a in asg]
    assert not any(a.reason.startswith("교대 출발") for a in asg)


def test_no_ready_relief_keeps_patrolling():
    by, asg = run(fleet(d3_status="maintenance"))
    assert by["d1"].role_id == "coast_a" and asg == []


def test_no_relief_still_goes_home_at_the_floor():
    by, asg = run(fleet(d1_battery=36, d3_status="maintenance"))
    assert by["d1"].role_id == "go_home"
    assert [a.reason for a in asg] == ["교대 귀환(하한선): d1"]


def test_empty_patrol_role_gets_a_ready_drone():
    states = [vs("d1", "coast_a", 80, 6000), vs("d2", "go_home", 35, 3000, "returning"),
              vs("d3", None, 100, 0, "ready")]  # fmt: skip
    by, asg = run(states)
    assert by["d3"].role_id == "coast_b"
    assert [a.reason for a in asg] == ["교대 투입(빈 순찰): d3 → coast_b"]


def test_no_patrol_out_means_no_rotation_yet():  # demo: rotation waits for the "전 기체 순찰" button
    states = [vs("d1", "patrol_a", 80, 6000), vs("d2", "standby", 100, 0, "ready"),
              vs("d3", "standby", 100, 0, "ready")]  # fmt: skip
    by, asg = run(states)
    assert (by["d2"].role_id, by["d3"].role_id, asg) == ("standby", "standby", [])


def test_two_on_one_role_without_relief_record_is_not_a_handover():
    by, asg = run(fleet(d1_battery=90, d3_role="coast_a", d3_north=5900))
    assert by["d1"].role_id == "coast_a" and by["d3"].role_id == "coast_a" and asg == []


POOLS = OP.model_copy(update={"rotation": ["d1", "d2", "d3", "d4"],
                              "rotation_pools": {"coast_a": ["d1", "d3"], "coast_b": ["d2", "d4"]}})  # fmt: skip
SPECS["d4"] = SPECS["d3"].model_copy(update={"id": "d4", "name": "d4"})


def test_pool_relief_comes_from_the_same_coast_pair():  # north d1·d3, south d2·d4
    states = [vs("d1", "coast_a", 90, 6000), vs("d2", "coast_b", 49, 6000, wp=4),
              vs("d3", None, 100, 0, "ready"), vs("d4", None, 100, 0, "ready")]  # fmt: skip
    by, asg = run(states, op=POOLS)
    assert (by["d3"].role_id, by["d4"].role_id) == (None, "coast_b")
    assert [a.reason for a in asg] == ["교대 출발: d4 → d2 @4"]


def test_pool_without_a_ready_partner_does_not_borrow_the_other_coast():
    states = [vs("d1", "coast_a", 49, 6000, wp=2), vs("d2", "coast_b", 90, 6000),
              vs("d3", "go_home", 40, 0, "returning"), vs("d4", None, 100, 0, "ready")]  # fmt: skip
    by, asg = run(states, op=POOLS)
    assert by["d4"].role_id is None and asg == []
