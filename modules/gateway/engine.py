"""gateway engine (Part2-17): tick = contracts/API.md §3 call order only. No logic here.

`init_engine(scenario)` makes the start state; `tick(state, inputs)` advances one tick_ms.
"""

from dataclasses import replace

from contracts.models import Frame, TickInputs, TickOutcome
from modules.gateway.actions.build_frame_v2 import build_frame_v2
from modules.gateway.actions.init_engine import init_engine
from modules.gateway.actions.mark_reported import mark_reported
from modules.gateway.actions.record_injections import record_injections
from modules.gateway.actions.run_checks import run_checks
from modules.gateway.actions.score_targets import score_targets
from modules.gateway.actions.tick_log import tick_log
from modules.gateway.actions.track_assignments import track_assignments
from modules.gateway.engine_state import EngineState
from modules.runtime import (
    apply_decision,
    apply_direct,
    apply_emergency,
    apply_injection,
    apply_reserves,
    fleet_choices,
    relieve_hover,
    rotate_patrols,
    spot_reports,
    step_vehicle,
    update_metrics,
)
from modules.sensing import observe
from modules.sim import (
    advance,
    apply_events,
    resolve_strikes,
    spawn_enemies,
    steer_enemies,
    update_emission,
)
from shared.log import get_logger

__all__ = ["EngineState", "init_engine", "tick"]
log = get_logger("gateway.engine")


def tick(es: EngineState, inputs: TickInputs) -> tuple[EngineState, Frame]:
    sc, dt, roles, specs = es.scenario, es.scenario.tick_ms, es.roles, es.specs
    t = es.t_ms + dt
    states, targets = apply_events(sc, es.states, es.targets, t, dt)  # 1
    targets = steer_enemies(
        sc.enemies, roles, spawn_enemies(sc, targets, t, dt), t, dt, sc.land
    )  # 1.5 (0032; boats round islands 0034)
    targets = update_emission(sc, targets, t)  # 1.6 (0039)
    targets = observe(states, specs, targets, t)  # 2
    targets = score_targets(states, specs, targets, sc.watch_points, dt)  # 2.5 (0039, 0040)
    reports, assigns = list(es.reports), list(es.assignments)  # 3 operator inputs
    for d in inputs.decisions:
        before = {s.id: s.role_id for s in states}
        states, reports = apply_decision(states, roles, d, reports)
        assigns = track_assignments(assigns, before, states, t, f"결정 {d.id}")
    injections, reports, new_reports, approved = record_injections(
        es.injections, reports, inputs.injections, t
    )
    for inj in approved:
        before = {s.id: s.role_id for s in states}
        states = apply_injection(states, roles, inj)
        assigns = track_assignments(assigns, before, states, t, f"전환 {inj.id}")
    before_direct, cmds = {}, []
    for dc in inputs.direct:
        pre = next(s for s in states if s.id == dc.vehicle_id)
        states, cmd = apply_direct(states, dc, t)
        before_direct[cmd.id] = pre
        cmds.append(cmd)
    states = apply_emergency(states, roles)  # 4
    states, assigns = rotate_patrols(states, specs, sc.operation, roles, assigns, t)  # 4.5 (0037)
    states, assigns = relieve_hover(states, specs, sc.operation, roles, assigns, t)  # 4.6
    stepped = []
    for s in states:  # 5
        s, cmd, rep = step_vehicle(
            s, specs[s.id], roles.get(s.role_id), targets, t, sc.operation.started_ms
        )  # 0045: at_time
        targets = mark_reported(targets, [rep] if rep else [])  # 5.1 decision 0036
        stepped.append(s)
        cmds += [cmd] if cmd else []
        new_reports += [rep] if rep else []
    spotted = spot_reports(stepped, targets, roles, sc.operation, t)  # 5.15 decision 0057
    targets = mark_reported(targets, spotted)
    new_reports += spotted
    raid = (targets, sc.land, specs)  # 24h raid choices (decision 0055)
    new_reports = [
        fleet_choices(r, stepped, sc.operation, roles, *raid) for r in new_reports
    ]  # 5.2
    reports = [
        fleet_choices(r, stepped, sc.operation, roles, *raid)
        if r.kind == "target_detected" and not r.resolved_ms
        else r
        for r in reports
    ]  # 5.3 open cards follow the fleet (decision 0046)
    states, assigns, gap = apply_reserves(stepped, sc.operation, roles, assigns, t)  # 6
    new_reports += [gap] if gap else []
    states, passed, blocks, cards = run_checks(  # 7
        cmds, before_direct, states, specs, sc.operation, roles, injections, t
    )
    states = advance(states, specs, passed, dt, targets, sc.land)  # 8 (sea round islands 0034)
    targets, hits = resolve_strikes(states, targets, t)  # 8.5 decision 0033
    new_reports += cards + hits
    reports += new_reports
    outcome = TickOutcome(inputs=inputs, commands=cmds, passed=passed, blocks=blocks,
                          new_reports=new_reports, assignments=assigns, states=states,
                          targets=targets, roles=roles, reports=reports)  # fmt: skip
    es = replace(es, t_ms=t, states=states, targets=targets, reports=reports, assignments=assigns,
                 blocks=es.blocks + blocks, injections=injections,
                 decisions=es.decisions + list(inputs.decisions), commands=es.commands + cmds,
                 passed=es.passed + passed,  # decision 0038: history for the object graph
                 metrics=update_metrics(es.metrics, outcome))  # 9  # fmt: skip
    log.debug("tick t=%d cmds=%d passed=%d blocks=%d new_reports=%d",
              t, len(cmds), len(passed), len(blocks), len(new_reports))  # fmt: skip
    return es, build_frame_v2(es, tick_log(sc, t, dt, inputs, blocks, passed, hits))  # 10
