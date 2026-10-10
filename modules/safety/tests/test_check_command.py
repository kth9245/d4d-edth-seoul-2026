import re
from pathlib import Path

from contracts.models import (
    Action,
    Block,
    Command,
    GeoPoint,
    Injection,
    Operation,
    PassedCommand,
    Play,
    Polygon,
    Provenance,
    Step,
    VehicleSpec,
    VehicleState,
)
from modules.safety.actions.check_command import RULES, check_command
from modules.safety.actions.point_in_polygon import point_in_polygon

ROOT = Path(__file__).resolve().parents[3]


def P(lat: float, lon: float) -> GeoPoint:
    return GeoPoint(lat=lat, lon=lon)


ZONE = Polygon(points=[P(37.0, 126.0), P(37.0, 126.1), P(37.1, 126.1), P(37.1, 126.0)])
OP = Operation(id="op1", name="op", area=ZONE, zone=ZONE, vehicle_ids=["d1"])
CENTER = P(37.05, 126.05)
SPEC = VehicleSpec(id="d1", name="d1", domain="air", speed_mps=15, endurance_min=40,
                   sensor_range_m=800, capabilities=[], home=CENTER)  # fmt: skip
STEP = Step(id="s1", name="s1", do=Action(kind="move_to"))
PLAYS = {
    "ok": Play(id="ok", name="ok", domains=["air"], steps=[STEP], entry="s1", approved=True),
    "draft": Play(id="draft", name="d", domains=["air"], steps=[STEP], entry="s1"),
}


def state(battery: float = 100) -> VehicleState:
    return VehicleState(id="d1", t_ms=5000, pos=CENTER, heading_deg=0, battery_pct=battery,
                        status="active")  # fmt: skip


def cmd(target: GeoPoint | None = None, prov: Provenance | None = None, **params) -> Command:
    if target is not None:
        params["target"] = target.model_dump()
    return Command(id="c1", vehicle_id="d1", kind="move", params=params, provenance=prov)


def by_play(play_id: str = "ok") -> Provenance:
    return Provenance(source="play_step", play_id=play_id, step_id="s1", issued_ms=0)


def check(
    c: Command, battery: float = 100, injections: list[Injection] = ()
) -> PassedCommand | Block:
    return check_command(c, state(battery), SPEC, OP, PLAYS, list(injections))


def test_passes_all_three_rules_in_order():
    out = check(cmd(P(37.06, 126.05), by_play()))
    assert isinstance(out, PassedCommand)
    assert out.checks == RULES == ["no_provenance", "outside_zone", "battery_insufficient"]
    assert out.passed_ms == 5000 and out.command.id == "c1"


def test_rule1_no_provenance_blocks_without_alternative():
    out = check(cmd(P(37.06, 126.05)))
    assert isinstance(out, Block) and out.reason == "no_provenance" and out.alternative is None


def test_rule1_unapproved_play_is_no_provenance():
    assert check(cmd(P(37.06, 126.05), by_play("draft"))).reason == "no_provenance"


def test_rule1_injected_plan_needs_an_approved_injection():
    prov = Provenance(source="injected_plan", injection_id="inj1", issued_ms=0)
    inj = Injection(id="inj1", t_ms=0, label="x", play_by_vehicle={"d1": "ok"})
    assert check(cmd(P(37.06, 126.05), prov), injections=[inj]).reason == "no_provenance"
    approved = inj.model_copy(update={"status": "approved"})
    assert isinstance(check(cmd(P(37.06, 126.05), prov), injections=[approved]), PassedCommand)


def test_rule1_operator_direct_has_provenance():
    prov = Provenance(source="operator_direct", operator_id="op1", issued_ms=0)
    assert isinstance(check(cmd(P(37.06, 126.05), prov)), PassedCommand)


def test_rule1_is_checked_before_rule2():
    assert check(cmd(P(37.2, 126.05))).reason == "no_provenance"


def test_rule2_outside_zone_blocks_with_alternative_inside():
    out = check(cmd(P(37.2, 126.05), by_play()))
    assert isinstance(out, Block) and out.reason == "outside_zone"
    alt = out.alternative
    assert alt is not None and alt.id == "c1-alt" and alt.kind == "move"
    pt = GeoPoint(**alt.params["target"])
    assert point_in_polygon(pt, ZONE)
    slice_m = (37.2 - 37.05) * 111_195 / 200
    assert 50 <= (37.1 - pt.lat) * 111_195 <= 50 + slice_m  # 50 m back from the first inside slice


def test_rule2_checks_every_route_point():
    route = [P(37.06, 126.05).model_dump(), P(37.05, 126.2).model_dump()]
    out = check(cmd(prov=by_play(), route=route))
    assert isinstance(out, Block) and out.reason == "outside_zone"


def test_rule3_battery_insufficient_offers_a_closer_point():
    out = check(cmd(P(37.068, 126.05), by_play()), battery=1)
    assert isinstance(out, Block) and out.reason == "battery_insufficient"
    pt = GeoPoint(**out.alternative.params["target"])
    assert CENTER.lat < pt.lat < 37.068


def test_command_without_destination_skips_rules_2_and_3():
    out = check(Command(id="c1", vehicle_id="d1", kind="hold", provenance=by_play()), battery=1)
    assert isinstance(out, PassedCommand)


def test_only_check_command_creates_passed_command():
    me = ROOT / "modules" / "safety" / "actions" / "check_command.py"
    hits = [
        p
        for p in (ROOT / "modules").rglob("*.py")
        if p != me and "tests" not in p.parts and re.search(r"PassedCommand\(", p.read_text())
    ]
    assert hits == []
