from contracts.models import (
    Action,
    Command,
    GeoPoint,
    Operation,
    Polygon,
    Provenance,
    Role,
    Step,
    VehicleSpec,
    VehicleState,
)
from modules.gateway.actions.run_checks import run_checks


def P(lat: float, lon: float) -> GeoPoint:
    return GeoPoint(lat=lat, lon=lon)


ZONE = Polygon(points=[P(37.0, 126.0), P(37.0, 126.1), P(37.1, 126.1), P(37.1, 126.0)])
OP = Operation(id="op1", name="op", area=ZONE, zone=ZONE, vehicle_ids=["d1", "d2"])
SPECS = {v: VehicleSpec(id=v, name=v, domain="air", speed_mps=15, endurance_min=40,
                        sensor_range_m=800, capabilities=[], home=P(37.05, 126.05))
         for v in ("d1", "d2")}  # fmt: skip
ROLES = {"p": Role(id="p", name="p", domains=["air"], entry="s", approved=True,
                   steps=[Step(id="s", name="s", do=Action(kind="hold"))])}  # fmt: skip


def vs(vid: str, **kw) -> VehicleState:
    base = dict(id=vid, t_ms=0, pos=P(37.05, 126.05), heading_deg=0, battery_pct=90,
                status="active", role_id="p", step_id="s")  # fmt: skip
    return VehicleState(**{**base, **kw})


def cmd(vid: str, target: GeoPoint, source: str | None = "role_step") -> Command:
    prov = Provenance(source=source, role_id="p", step_id="s", issued_ms=0) if source else None
    return Command(id=f"c-{vid}", vehicle_id=vid, kind="move",
                   params={"target": target.model_dump()}, provenance=prov)  # fmt: skip


def run(cmds, states, before=None):
    return run_checks(cmds, before or {}, states, SPECS, OP, ROLES, [], 5000)


def test_passing_commands_go_through_safety():
    states = [vs("d1"), vs("d2")]
    out, passed, blocks, cards = run([cmd("d1", P(37.06, 126.05))], states)
    assert [p.command.id for p in passed] == ["c-d1"] and passed[0].passed_ms == 5000
    assert blocks == cards == [] and out == states


def test_blocked_command_makes_a_card():
    _, passed, blocks, cards = run([cmd("d1", P(37.06, 126.05), source=None)], [vs("d1")])
    assert passed == [] and [b.reason for b in blocks] == ["no_provenance"]
    (card,) = cards
    assert (card.kind, card.vehicle_id, card.t_ms) == ("command_blocked", "d1", 5000)
    assert "no_provenance" in card.text


def test_blocked_direct_control_restores_the_vehicle():
    before = vs("d2", step_id="s", entered_step=True)
    during = vs("d2", step_id=None, resume_role_id="p", resume_step_id="s")
    direct = cmd("d2", P(37.5, 126.05), source="operator_direct")
    out, _, blocks, _ = run([direct], [vs("d1"), during], {"c-d2": before})
    assert [b.reason for b in blocks] == ["outside_zone"] and blocks[0].alternative is not None
    assert out == [vs("d1"), before]
