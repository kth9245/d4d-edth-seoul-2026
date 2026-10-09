"""Two-layer engine spike (decisions 0015-0018). Every tick function is named and shaped as in
contracts/API.md §3 and runs the 3-minute script on demo/scenarios/baengnyeong_night.json with a
scripted operator. Porting source for Part2 (sim, sensing, safety, runtime) and the tick loop (Part2-17).
Run: uv run python knowledge/spikes/rolecall_engine_proto/engine_proto.py
"""
import math
import sys
import time
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT), str(HERE)]

from contracts.models import (Assignment, Block, Command, CommandKind, Decision, DirectControl,  # noqa: E402
                              EmergencyKind, Frame, GeoPoint, Injection, Metrics, PassedCommand,
                              Provenance, Report, RunState, Scenario, Target, TargetKind, TickInputs,
                              TickOutcome, VehicleState, VehicleStatus)
from geo import M_PER_DEG_LAT, dist_m, lerp, m_per_deg_lon, move_toward, point_in_polygon  # noqa: E402
from step_vehicle import step_vehicle  # noqa: E402

SCENARIO = ROOT / "demo/scenarios/baengnyeong_night.json"
RULES = ["no_provenance", "outside_zone", "battery_insufficient"]
LIVE = (VehicleStatus.ready, VehicleStatus.active)
GONE = (VehicleStatus.returning, VehicleStatus.lost, VehicleStatus.maintenance)


def kst(t_ms: int) -> str:
    return (datetime.fromtimestamp(t_ms / 1000, timezone.utc) + timedelta(hours=9)).strftime("%H:%M:%S")


# ---------- sim.apply_events (Part2-5) ----------
def apply_events(scenario, states, targets, t_ms, dt_ms):
    start = scenario.operation.started_ms
    for ev in scenario.events:
        if not (t_ms - dt_ms < start + ev.offset_ms <= t_ms):
            continue
        p = ev.params
        if ev.kind == "spawn_target":
            targets = [*targets, Target(id=p["id"], kind=p["kind"], pos=GeoPoint(**p["pos"]), vel_east_mps=p.get("ve", 0),
                                        vel_north_mps=p.get("vn", 0), first_seen_ms=0, last_seen_ms=0)]
        elif ev.kind == "split_target":
            src = next(t for t in targets if t.id == p["id"])
            targets = [*targets, src.model_copy(update={"id": p["new_id"], "kind": TargetKind(p.get("kind", src.kind)),
                                                        "vel_east_mps": p["ve"], "vel_north_mps": p["vn"],
                                                        "seen_by": [], "first_seen_ms": 0})]
        elif ev.kind == "target_move":
            targets = [t.model_copy(update={"vel_east_mps": p["ve"], "vel_north_mps": p["vn"]}) if t.id == p["id"] else t
                       for t in targets]
        elif ev.kind == "vehicle_battery_set":
            states = [s.model_copy(update={"battery_pct": float(p["pct"])}) if s.id == p["id"] else s for s in states]
        elif ev.kind == "vehicle_link_lost":
            states = [s.model_copy(update={"status": VehicleStatus.lost}) if s.id == p["id"] else s for s in states]
    dt = dt_ms / 1000
    targets = [t.model_copy(update={"pos": GeoPoint(lat=t.pos.lat + t.vel_north_mps * dt / M_PER_DEG_LAT,
                                                    lon=t.pos.lon + t.vel_east_mps * dt / m_per_deg_lon(t.pos.lat))})
               for t in targets]
    return states, targets


# ---------- sensing.observe (Part2-6) ----------
def observe(states, specs, targets, t_ms):
    out = []
    for tg in targets:
        seen = [s.id for s in states if s.status in LIVE and dist_m(s.pos, tg.pos) <= specs[s.id].sensor_range_m]
        upd = {"seen_by": seen}
        if seen:
            upd |= {"last_seen_ms": t_ms, "first_seen_ms": tg.first_seen_ms or t_ms}
        out.append(tg.model_copy(update=upd))
    return out


# ---------- runtime: switching plays (Part2-12, 2-14, 2-15, 2-16, 2-11) ----------
def _switch(s: VehicleState, play) -> VehicleState:
    return s.model_copy(update={"play_id": play.id, "step_id": play.entry, "entered_step": False, "target_id": None,
                                "pending_report_id": None, "waypoint_idx": 0, "resume_play_id": None,
                                "resume_step_id": None})


def apply_decision(states, plays, decision, reports):
    rep = next(r for r in reports if r.id == decision.report_id)
    ch = next(c for c in rep.choices if c.id == decision.choice_id)
    reports = [r.model_copy(update={"resolved_ms": decision.t_ms, "decision_id": decision.id}) if r.id == rep.id else r
               for r in reports]
    out = []
    for s in states:
        if rep.kind == "target_select" and s.id == rep.vehicle_id:
            s = s.model_copy(update={"target_id": ch.id, "pending_report_id": None, "entered_step": False})
        elif s.id in ch.play_by_vehicle:
            s = _switch(s, plays[ch.play_by_vehicle[s.id]])
        elif s.id == rep.vehicle_id:
            s = s.model_copy(update={"pending_report_id": None})
        out.append(s)
    return out, reports


def apply_injection(states, plays, injection):
    return [_switch(s, plays[injection.play_by_vehicle[s.id]]) if s.id in injection.play_by_vehicle else s
            for s in states]


def apply_direct(states, direct, t_ms):
    cmd = Command(id=f"cmd-{direct.vehicle_id}-{t_ms}", vehicle_id=direct.vehicle_id, kind=CommandKind.move,
                  params={"target": direct.target.model_dump()},
                  provenance=Provenance(source="operator_direct", operator_id="op1", issued_ms=t_ms))

    def mark(s):
        if s.id != direct.vehicle_id:
            return s
        resume = (s.resume_play_id, s.resume_step_id) if s.step_id is None else (s.play_id, s.step_id)
        return s.model_copy(update={"step_id": None, "entered_step": True, "waypoint_idx": 0,
                                    "resume_play_id": resume[0], "resume_step_id": resume[1]})
    return [mark(s) for s in states], cmd


def apply_emergency(states, plays):
    out = []
    for s in states:
        rule = plays[s.play_id].emergency if s.play_id in plays else None
        if (rule and rule.battery_low_step and s.status in LIVE and s.step_id != rule.battery_low_step
                and s.battery_pct < rule.battery_low_pct):
            s = s.model_copy(update={"step_id": rule.battery_low_step, "entered_step": False,
                                     "emergency": EmergencyKind.battery_low})
        out.append(s)
    return out


def apply_reserves(states, op, plays, assignments, t_ms):
    """A reserve restarts the departed vehicle's play from its entry step (decision 0016)."""
    by = {s.id: s for s in states}
    for vid, reserves in op.reserve.items():
        reason = f"예비 투입: {vid} 대신"
        gone = by.get(vid)
        if gone is None or gone.status not in GONE or any(a.reason == reason for a in assignments):
            continue
        nxt = next((r for r in reserves if by[r].status in LIVE), None)
        if nxt is None:
            continue
        by[nxt] = _switch(by[nxt], plays[gone.play_id])
        assignments = [a for a in assignments if a.vehicle_id != nxt] + [
            Assignment(vehicle_id=nxt, play_id=gone.play_id, since_ms=t_ms, reason=reason)]
        rep = Report(id=f"rep-{nxt}-{t_ms}", t_ms=t_ms, kind="vehicle_gap", vehicle_id=nxt,
                     text=f"{vid} 이탈, 예비 {nxt} 투입: 공백 측정 중")
        return [by[s.id] for s in states], assignments, rep
    return states, assignments, None


# ---------- safety (Part2-7, 2-8, 2-9) ----------
def return_feasible(state, spec, dest):
    have_s = spec.endurance_min * 60 * state.battery_pct / 100 * 0.8

    def need_s(p):
        return (dist_m(state.pos, p) + dist_m(p, spec.home)) / spec.speed_mps
    if need_s(dest) <= have_s:
        return True, None
    for k in range(200):  # walk back from the destination toward the vehicle
        cand = lerp(state.pos, dest, 1 - k / 200)
        if need_s(cand) <= have_s:
            return False, cand
    return False, None


def check_command(cmd, state, spec, op, plays, injections):
    p, t = cmd.provenance, state.t_ms

    def block(reason, detail, alt=None):
        return Block(command_id=cmd.id, vehicle_id=cmd.vehicle_id, reason=reason, detail=detail,
                     alternative=alt, t_ms=t)

    def alt(point):
        return cmd.model_copy(update={"id": cmd.id + "-alt", "params": {**cmd.params, "target": point.model_dump()}})
    if (p is None or (p.source == "play_step" and not plays[p.play_id].approved)
            or (p.source == "injected_plan"
                and not any(i.id == p.injection_id and i.status == "approved" for i in injections))):
        return block("no_provenance", "출처 없음")
    dests = ([GeoPoint(**cmd.params["target"])] if "target" in cmd.params
             else [GeoPoint(**q) for q in cmd.params.get("route", [])])
    for d in dests:
        if not point_in_polygon(d, op.zone):
            inside = next((lerp(state.pos, d, 1 - k / 200) for k in range(1, 201)
                           if point_in_polygon(lerp(state.pos, d, 1 - k / 200), op.zone)), None)
            return block("outside_zone", f"작전 구역 밖({d.lat:.4f}, {d.lon:.4f})",
                         alt(move_toward(inside, state.pos, 50)) if inside else None)
    if dests:
        ok, point = return_feasible(state, spec, dests[-1])
        if not ok:
            return block("battery_insufficient", f"귀환 배터리 부족({dests[-1].lat:.4f}, {dests[-1].lon:.4f})",
                         alt(point) if point else None)
    return PassedCommand(command=cmd, checks=RULES, passed_ms=t)


# ---------- sim.advance (Part2-1..2-4) ----------
def advance(states, specs, passed, dt_ms, targets):
    by_v = {pc.command.vehicle_id: pc for pc in passed}
    out = []
    for st in states:
        spec, pc = specs[st.id], by_v.get(st.id) or st.active
        new = st.model_copy(update={"t_ms": st.t_ms + dt_ms})
        if pc is None or st.status in (VehicleStatus.lost, VehicleStatus.maintenance):
            out.append(new)
            continue
        cmd, step_m, upd = pc.command, spec.speed_mps * dt_ms / 1000, {"active": pc}
        if cmd.kind == CommandKind.hold and dist_m(st.pos, spec.home) < 1:  # on the ground at base
            out.append(new.model_copy(update=upd))
            continue
        if cmd.kind in (CommandKind.move, CommandKind.return_home):
            tgt = spec.home if cmd.kind == CommandKind.return_home else GeoPoint(**cmd.params["target"])
            upd["pos"] = move_toward(st.pos, tgt, step_m)
            if dist_m(upd["pos"], tgt) < 1:
                upd["waypoint_idx"] = -1
                if cmd.kind == CommandKind.return_home:
                    upd["status"] = VehicleStatus.maintenance
        elif cmd.kind == CommandKind.follow_route:
            route = [GeoPoint(**q) for q in cmd.params["route"]]
            i = max(st.waypoint_idx, 0) % len(route)
            upd["pos"] = move_toward(st.pos, route[i], step_m)
            if dist_m(upd["pos"], route[i]) < 1:
                upd["waypoint_idx"] = i + 1
        elif cmd.kind in (CommandKind.orbit, CommandKind.keep_distance):
            tg = next((t for t in targets if t.id == cmd.params.get("target_id")), None)
            r = float(cmd.params.get("distance_m", 150))
            if tg and cmd.kind == CommandKind.orbit and dist_m(st.pos, tg.pos) <= r * 1.5:
                ang = math.radians(st.heading_deg) + step_m / r
                upd |= {"heading_deg": math.degrees(ang) % 360,
                        "pos": GeoPoint(lat=tg.pos.lat + r * math.cos(ang) / M_PER_DEG_LAT,
                                        lon=tg.pos.lon + r * math.sin(ang) / m_per_deg_lon(tg.pos.lat),
                                        alt_m=st.pos.alt_m)}
            elif tg:  # fly in first (the old spike teleported onto the orbit, so no takeover gap appeared)
                upd["pos"] = move_toward(st.pos, tg.pos, min(step_m, max(dist_m(st.pos, tg.pos) - r, 0)))
        upd["battery_pct"] = max(st.battery_pct - 100 / spec.endurance_min * dt_ms / 60000, 0)
        if st.status == VehicleStatus.ready:
            upd["status"] = VehicleStatus.active
        out.append(new.model_copy(update=upd))
    return out


# ---------- runtime.update_metrics (Part2-13; definitions: contracts/API.md §2) ----------
def _reached(vid, outcome):
    st = next(s for s in outcome.states if s.id == vid)
    play = outcome.plays.get(st.play_id)
    step = next((s for s in play.steps if s.id == st.step_id), None) if play else None
    kind = step.do.kind.value if step else None
    if kind in ("watch_target", "approach_target"):
        return any(vid in t.seen_by for t in outcome.targets)
    if kind in ("move_to", "patrol_route"):
        return st.waypoint_idx < 0 or st.waypoint_idx >= 1
    return st.active is not None


def update_metrics(metrics, outcome):
    m, inp = metrics.model_copy(), outcome.inputs
    m.operator_actions += len(inp.decisions) + len(inp.direct) + len(inp.injections)
    m.decisions += len(inp.decisions)
    m.commands_sent += len(outcome.passed)
    m.blocked_commands += len(outcome.blocks)
    m.manual_baseline_actions += len(outcome.new_reports) + sum(
        1 for c in outcome.commands if c.provenance and c.provenance.source in ("play_step", "emergency"))
    m.open_reports_max = max(m.open_reports_max, sum(1 for r in outcome.reports if r.choices and not r.resolved_ms))
    now = outcome.states[0].t_ms if outcome.states else 0
    for a in outcome.assignments:
        if a.reason.startswith("예비 투입") and not _reached(a.vehicle_id, outcome):
            m.vehicle_gap_ms = max(m.vehicle_gap_ms, now - a.since_ms)
    return m


# ---------- gateway engine.py: state and tick (Part2-17, 2-18) ----------
@dataclass
class EngineState:
    t_ms: int
    scenario: Scenario
    specs: dict
    plays: dict
    states: list
    targets: list
    reports: list
    assignments: list
    blocks: list
    injections: list
    metrics: Metrics
    run: RunState


def init_state(scenario: Scenario) -> EngineState:
    op, plays = scenario.operation, {p.id: p for p in scenario.plays}
    states = [VehicleState(id=v.id, t_ms=op.started_ms, pos=v.home, heading_deg=0, battery_pct=100, status="ready",
                           play_id=op.assign.get(v.id), step_id=plays[op.assign[v.id]].entry if v.id in op.assign else None)
              for v in scenario.vehicles]
    assigns = [Assignment(vehicle_id=v, play_id=p, since_ms=op.started_ms, reason="작전 배정") for v, p in op.assign.items()]
    return EngineState(op.started_ms, scenario, {v.id: v for v in scenario.vehicles}, plays, states, [], [], assigns,
                       [], [], Metrics(), RunState(status="running"))


def _reassign(assignments, before, states, t_ms, reason):
    changed = [s for s in states if s.play_id != before.get(s.id)]
    keep = [a for a in assignments if a.vehicle_id not in {s.id for s in changed}]
    return keep + [Assignment(vehicle_id=s.id, play_id=s.play_id, since_ms=t_ms, reason=reason) for s in changed]


def tick(es: EngineState, inputs: TickInputs) -> tuple[EngineState, Frame]:
    sc, dt = es.scenario, es.scenario.tick_ms
    t = es.t_ms + dt
    log = [f"[대본] {kst(t)} {ev.kind} {ev.params.get('id', '')}" for ev in sc.events
           if t - dt < sc.operation.started_ms + ev.offset_ms <= t]
    states, targets = apply_events(sc, es.states, es.targets, t, dt)
    targets = observe(states, es.specs, targets, t)
    reports, injections, assigns, new_reports = list(es.reports), list(es.injections), list(es.assignments), []
    for d in inputs.decisions:
        before = {s.id: s.play_id for s in states}
        states, reports = apply_decision(states, es.plays, d, reports)
        assigns = _reassign(assigns, before, states, t, f"결정 {d.id}")
        log.append(f"[계산] {kst(t)} 결정 {d.id} → {d.choice_id}")
    for inj in inputs.injections:  # gateway: new request -> pending card; approve/reject -> status change
        if inj.status == "pending":
            new_reports.append(Report(id=f"rep-{next(iter(inj.play_by_vehicle))}-{t}", t_ms=t, kind="injection_pending",
                                      text=f"전환 승인 대기: {inj.label}"))
        reports = [r.model_copy(update={"resolved_ms": t}) if r.kind == "injection_pending" and not r.resolved_ms
                   and inj.status != "pending" else r for r in reports]
        injections = [i for i in injections if i.id != inj.id] + [inj]
        if inj.status == "approved":
            before = {s.id: s.play_id for s in states}
            states = apply_injection(states, es.plays, inj)
            assigns = _reassign(assigns, before, states, t, f"전환 {inj.id}")
        log.append(f"[계산] {kst(t)} 전환 {inj.id} {inj.status}")
    direct = []
    for dc in inputs.direct:
        pre = next(s for s in states if s.id == dc.vehicle_id)
        states, cmd = apply_direct(states, dc, t)
        direct.append((cmd, pre))
    states = apply_emergency(states, es.plays)
    cmds, stepped = [], []
    for s in states:
        s2, cmd, rep = step_vehicle(s, es.specs[s.id], es.plays.get(s.play_id), targets, t)
        stepped.append(s2)
        cmds += [cmd] if cmd else []
        new_reports += [rep] if rep else []
    states, assigns, gap = apply_reserves(stepped, sc.operation, es.plays, assigns, t)
    new_reports += [gap] if gap else []
    passed, blocks, pre_of = [], [], {c.id: pre for c, pre in direct}
    for cmd in [*cmds, *(c for c, _ in direct)]:
        st = next(s for s in states if s.id == cmd.vehicle_id).model_copy(update={"t_ms": t})
        res = check_command(cmd, st, es.specs[cmd.vehicle_id], sc.operation, es.plays, injections)
        if isinstance(res, Block):
            blocks.append(res)
            new_reports.append(Report(id=f"rep-{cmd.vehicle_id}-{t}-b", t_ms=t, kind="command_blocked",
                                      vehicle_id=cmd.vehicle_id, text=f"차단 {res.reason.value}: {res.detail}"))
            if cmd.id in pre_of:  # a blocked direct control leaves the vehicle as it was
                states = [pre_of[cmd.id] if s.id == cmd.vehicle_id else s for s in states]
            log.append(f"[계산] {kst(t)} 차단 {cmd.vehicle_id} {res.reason.value}")
        else:
            passed.append(res)
    states = advance(states, es.specs, passed, dt, targets)
    reports += new_reports
    outcome = TickOutcome(inputs=inputs, commands=[*cmds, *(c for c, _ in direct)], passed=passed, blocks=blocks,
                          new_reports=new_reports, assignments=assigns, states=states, targets=targets,
                          plays=es.plays, reports=reports)
    es = replace(es, t_ms=t, states=states, targets=targets, reports=reports, assignments=assigns,
                 blocks=es.blocks + blocks, injections=injections, metrics=update_metrics(es.metrics, outcome))
    return es, Frame(t_ms=t, run=es.run, vehicles=states, targets=targets, reports=reports, assignments=assigns,
                     blocks=es.blocks, injections=injections, metrics=es.metrics, log=log)


# ---------- scripted operator (stands in for the screen) ----------
class Operator:
    def __init__(self, start):
        self.start, self.n = start, {"dec": 0, "dir": 0}

    def _id(self, kind):
        self.n[kind] += 1
        return f"{kind}-{self.n[kind]}"

    def inputs(self, es, t) -> TickInputs:
        decisions, direct, inj = [], [], []
        for r in es.reports:  # answer a card 20 s after it appears (target pick: 10 s)
            wait = 10_000 if r.kind == "target_select" else 20_000
            if r.choices and not r.resolved_ms and t == r.t_ms + wait:
                pick = "fast1" if any(c.id == "fast1" for c in r.choices) else r.choices[0].id
                decisions.append(Decision(id=self._id("dec"), t_ms=t, report_id=r.id, choice_id=pick))
        off = t - self.start
        if off == 23 * 60_000 + 20_000:
            inj.append(Injection(id="inj-1", t_ms=t, label="고속 보트 추적: d2", play_by_vehicle={"d2": "track_fast"}))
        if off == 24 * 60_000:
            inj.append(next(i for i in es.injections if i.id == "inj-1").model_copy(update={"status": "approved"}))
        goals = {31 * 60_000: GeoPoint(lat=38.05, lon=124.70), 31 * 60_000 + 30_000: GeoPoint(lat=37.905, lon=124.565)}
        if off == 31 * 60_000 + 5_000 and es.blocks and es.blocks[-1].alternative:  # press "대안 지점으로"
            goals[off] = GeoPoint(**es.blocks[-1].alternative.params["target"])
        if off in goals:
            direct.append(DirectControl(id=self._id("dir"), vehicle_id="d2", target=goals[off], t_ms=t))
        return TickInputs(decisions=decisions, direct=direct, injections=inj)


def run(minutes=35, path=SCENARIO, every=25):
    sc = Scenario.model_validate_json(Path(path).read_text(encoding="utf-8"))
    es, op = init_state(sc), Operator(sc.operation.started_ms)
    frames, log = [], []
    for i in range(minutes * 60_000 // sc.tick_ms):
        es, fr = tick(es, op.inputs(es, es.t_ms + sc.tick_ms))
        log += fr.log
        if i % every == 0:
            frames.append(fr)
    frames.append(fr)
    return {"start_ms": sc.operation.started_ms, "frames": frames, "log": log, "metrics": es.metrics}


if __name__ == "__main__":
    t0 = time.perf_counter()
    out = run()
    print(f"{len(out['frames'])} frames kept, {time.perf_counter() - t0:.2f}s")
    print("\n".join(out["log"]))
    print("metrics:", out["metrics"].model_dump())
    last = out["frames"][-1]
    print("final:", {v.id: (v.play_id, v.step_id, v.status.value, round(v.battery_pct)) for v in last.vehicles})
