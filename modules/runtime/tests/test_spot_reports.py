from contracts.models import (
    Action,
    Condition,
    Exit,
    GeoPoint,
    Operation,
    Polygon,
    ReportSpec,
    Role,
    Step,
    Switch,
    Target,
    VehicleState,
)
from modules.runtime.actions.spot_reports import spot_reports

T = 1_791_635_000_000
HOME = GeoPoint(lat=37.98, lon=124.70)
SQ = Polygon(points=[GeoPoint(lat=37.9, lon=124.6), GeoPoint(lat=37.9, lon=124.8),
                     GeoPoint(lat=38.0, lon=124.8), GeoPoint(lat=38.0, lon=124.6)])  # fmt: skip


def _role(rid: str, kind: str, target: str | None = "operator", domains=("air",)) -> Role:
    params = {"target": target} if target else {}
    return Role(id=rid, name=rid, domains=list(domains), entry="s", approved=True,
                steps=[Step(id="s", name="s", do=Action(kind=kind, params=params))])  # fmt: skip


ROLES = {
    "watch": _role("watch", "watch_target"),
    "track_fast": _role("track_fast", "watch_target"),
    "track_fast_sea": _role("track_fast_sea", "watch_target", domains=("sea",)),
    "go_home": _role("go_home", "return_home", None, ("air", "sea")),
    "coast_a": Role(id="coast_a", name="coast_a", domains=["air"], entry="s", approved=True, steps=[
        Step(id="s", name="s", do=Action(kind="patrol_route"),
             on=[Exit(cond=Condition(kind="target_found"), go_step="r")]),
        Step(id="r", name="r", do=Action(kind="watch_target", params={"target": "nearest"}),
             report=ReportSpec(text="미식별 선박 접근", auto_choices=True))]),
}  # fmt: skip
OP = Operation(id="op", name="op", area=SQ, zone=SQ, vehicle_ids=["d1", "d2", "d3", "d4", "usv"],
               rotation=["d1", "d2", "d3", "d4"], rotation_roles=["coast_a"],
               switches=[Switch(id="all_home", label="전 기체 귀환", role_by_vehicle={"d1": "go_home", "usv": "go_home"}),
                         Switch(id="track_fast", label="고속 보트 추적",
                                role_by_vehicle={"d2": "track_fast", "usv": "track_fast_sea"})])  # fmt: skip


def vs(
    vid, role=None, status="active", target=None, battery=100.0, pending=None, step="s"
) -> VehicleState:
    return VehicleState(id=vid, t_ms=T, pos=HOME, heading_deg=0, battery_pct=battery, status=status,
                        role_id=role, step_id=step if role else None, entered_step=True, target_id=target,
                        pending_report_id=pending)  # fmt: skip


def tg(
    tid="fast1", kind="fast_boat", seen=("d3",), accum=450_000, reported=None, struck=None
) -> Target:
    return Target(id=tid, kind=kind, pos=HOME, vel_east_mps=0, vel_north_mps=0, first_seen_ms=T,
                  last_seen_ms=T, seen_by=list(seen), threat_accum=accum, reported_by=reported,
                  neutralized_ms=struck)  # fmt: skip


FLEET = [vs("d1", "go_home", "returning", battery=20), vs("d2", "coast_a"), vs("d3", "watch", target="boat1"),
         vs("d4", None, "ready"), vs("usv", "watch", target="boat2")]  # fmt: skip


def test_a_watching_drone_raises_a_card_for_a_new_enemy_with_target_switches_then_standby_drones():
    # decision 0056: d3 keeps watching boat1 and asks who to send to fast1
    (rep,) = spot_reports(FLEET, [tg("boat1", "boat", reported="d1"), tg()], ROLES, OP, T)
    assert (rep.id, rep.kind, rep.vehicle_id, rep.target_id) == (
        f"rep-d3-{T}-s",
        "target_detected",
        "d3",
        "fast1",
    )
    assert rep.text.startswith("새 적 탐지 · d3 센서 탐지 · fast1(고속정)")
    track, watch = rep.choices
    assert (track.id, track.label, track.role_by_vehicle, track.target_by_vehicle) == (
        "switch_track_fast", "고속 보트 추적", {"d2": "track_fast", "usv": "track_fast_sea"},
        {"d2": "fast1", "usv": "fast1"})  # fmt: skip
    assert (watch.label, watch.role_by_vehicle, watch.target_by_vehicle) == (
        "d4 → fast1 감시", {"d4": "watch"}, {"d4": "fast1"})  # fmt: skip


def test_no_card_before_the_threat_builds_up_or_once_reported_worked_or_struck():
    for t in (tg(accum=449_999), tg(reported="d2"), tg(struck=T), tg(seen=())):
        assert spot_reports(FLEET, [t], ROLES, OP, T) == []
    on_it = [*FLEET[:3], vs("d4", "watch", target="fast1"), FLEET[4]]  # someone already works fast1
    assert spot_reports(on_it, [tg()], ROLES, OP, T) == []


def test_keep_when_no_target_switch_and_no_standby_drone():
    op = OP.model_copy(update={"switches": OP.switches[:1]})
    busy = [*FLEET[:3], vs("d4", "coast_a"), FLEET[4]]
    (rep,) = spot_reports(busy, [tg()], ROLES, op, T)
    assert [c.id for c in rep.choices] == ["keep"]


def test_a_patrolling_drone_leaves_the_card_to_its_own_report_step():
    # decision 0036: the patrol's report step raises it (a tick after target_found); spot cards are for the rest
    for step in ("s", "r"):
        fleet = [vs("d2", "coast_a", step=step), FLEET[3]]
        assert spot_reports(fleet, [tg(seen=("d2",))], ROLES, OP, T) == []
