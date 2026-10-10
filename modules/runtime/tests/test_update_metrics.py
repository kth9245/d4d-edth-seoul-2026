from contracts.models import (
    Action,
    Assignment,
    Block,
    Choice,
    Command,
    Decision,
    DirectControl,
    GeoPoint,
    Injection,
    Metrics,
    Provenance,
    Report,
    Role,
    Step,
    Target,
    TickInputs,
    TickOutcome,
    VehicleState,
)
from modules.runtime.actions.update_metrics import update_metrics

G = GeoPoint(lat=37, lon=126)
WATCH = Role(id="watch", name="w", domains=["air"], entry="s1",
             steps=[Step(id="s1", name="s1", do=Action(kind="watch_target"))])  # fmt: skip


def vs(vid: str, t_ms: int = 5000) -> VehicleState:
    return VehicleState(id=vid, t_ms=t_ms, pos=G, heading_deg=0, battery_pct=90,
                        status="active", role_id="watch", step_id="s1")  # fmt: skip


def cmd(source: str) -> Command:
    return Command(id=f"c-{source}", vehicle_id="d1", kind="move",
                   provenance=Provenance(source=source, issued_ms=0))  # fmt: skip


def report(rid: str, choices: bool = True, resolved: int | None = None) -> Report:
    ch = [Choice(id="a", label="a")] if choices else []
    return Report(
        id=rid, t_ms=0, kind="target_detected", text="x", choices=ch, resolved_ms=resolved
    )


def boat(seen_by: list[str]) -> Target:
    return Target(id="boat1", kind="boat", pos=G, vel_east_mps=0, vel_north_mps=0,
                  first_seen_ms=0, last_seen_ms=0, seen_by=seen_by)  # fmt: skip


def test_operator_actions_count_decisions_direct_and_injections():
    inp = TickInputs(
        decisions=[Decision(id="dec1", t_ms=0, report_id="r1", choice_id="a")],
        direct=[DirectControl(id="dc1", vehicle_id="d1", target=G, t_ms=0)],
        injections=[Injection(id="inj1", t_ms=0, label="x", role_by_vehicle={})],
    )
    m = update_metrics(Metrics(operator_actions=2), TickOutcome(inputs=inp))
    assert (m.operator_actions, m.decisions) == (5, 1)


def test_manual_baseline_counts_plan_commands_and_new_reports():
    out = TickOutcome(
        commands=[cmd("role_step"), cmd("emergency"), cmd("operator_direct")],
        new_reports=[report("r1")],
    )
    assert update_metrics(Metrics(), out).manual_baseline_actions == 3


def test_open_reports_max_keeps_the_peak_of_waiting_cards():
    out = TickOutcome(reports=[report("r1"), report("r2"), report("r3", resolved=1),
                               report("r4", choices=False)])  # fmt: skip
    assert update_metrics(Metrics(), out).open_reports_max == 2
    assert update_metrics(Metrics(open_reports_max=5), out).open_reports_max == 5


def test_blocked_and_sent_commands():
    blk = Block(command_id="c", vehicle_id="d1", reason="outside_zone", detail="x", t_ms=0)
    m = update_metrics(Metrics(), TickOutcome(blocks=[blk, blk]))
    assert (m.blocked_commands, m.commands_sent) == (2, 0)


def test_vehicle_gap_runs_from_reserve_start_until_the_reserve_sees_the_target():
    gap = Assignment(vehicle_id="d3", role_id="watch", since_ms=1000, reason="예비 투입: d1 대신")
    base = dict(assignments=[gap], states=[vs("d3")], roles={"watch": WATCH})
    m = update_metrics(Metrics(), TickOutcome(**base, targets=[boat([])]))
    assert m.vehicle_gap_ms == 4000
    later = TickOutcome(**{**base, "states": [vs("d3", 9000)]}, targets=[boat(["d3"])])
    assert update_metrics(m, later).vehicle_gap_ms == 4000


def test_mission_succeeds_once_a_target_is_neutralized():
    struck = Target(id="fast1", kind="fast_boat", pos=G, vel_east_mps=0, vel_north_mps=0,
                    first_seen_ms=0, last_seen_ms=0, neutralized_ms=5000)  # fmt: skip
    m = update_metrics(Metrics(), TickOutcome(states=[vs("d2")], targets=[struck]))
    assert m.mission_success is True
    assert update_metrics(Metrics(), TickOutcome(states=[vs("d2")])).mission_success is None
