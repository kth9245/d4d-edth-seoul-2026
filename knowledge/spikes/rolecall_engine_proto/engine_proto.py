"""Skeleton engine following docs/research/09 literally, plus ONE contract addition under test:
VehicleState.active: PassedCommand | None  (the command the vehicle is currently executing).
Run the Baengnyeong 5-event script (events 1,2,3,6; event 4 injection stubbed) and report."""
import math, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models09 import *

ACTIVE_FIELD = "--no-active" not in sys.argv  # flip to reproduce the kill shot
M_PER_DEG_LAT = 111_320.0
def m_per_deg_lon(lat): return 111_320.0 * math.cos(math.radians(lat))
def dist_m(a: GeoPoint, b: GeoPoint) -> float:
    dx = (b.lon - a.lon) * m_per_deg_lon(a.lat); dy = (b.lat - a.lat) * M_PER_DEG_LAT
    return math.hypot(dx, dy)
def move_toward(p: GeoPoint, q: GeoPoint, step_m: float) -> GeoPoint:
    d = dist_m(p, q)
    if d <= step_m: return q.model_copy()
    f = step_m / d
    return GeoPoint(lat=p.lat + (q.lat - p.lat) * f, lon=p.lon + (q.lon - p.lon) * f, alt_m=p.alt_m)
def point_in_polygon(p: GeoPoint, poly: Polygon) -> bool:
    pts = poly.points; inside = False; j = len(pts) - 1
    for i in range(len(pts)):
        yi, xi, yj, xj = pts[i].lat, pts[i].lon, pts[j].lat, pts[j].lon
        if (yi > p.lat) != (yj > p.lat) and p.lon < (xj - xi) * (p.lat - yi) / (yj - yi + 1e-12) + xi: inside = not inside
        j = i
    return inside

# ---------- sim.advance : one tick of movement for every vehicle ----------
def advance(states, specs, passed, dt_ms, targets):
    out = []
    by_v = {pc.command.vehicle_id: pc for pc in passed}
    for st in states:
        spec = specs[st.id]
        pc = by_v.get(st.id) or (st.active if ACTIVE_FIELD else None)
        new = st.model_copy(update={"t_ms": st.t_ms + dt_ms})
        if pc is None or st.status == VehicleStatus.lost:
            out.append(new); continue
        cmd = pc.command; step_m = spec.speed_mps * dt_ms / 1000
        upd = {"active": pc} if ACTIVE_FIELD else {}
        if cmd.kind in (CommandKind.move, CommandKind.return_home):
            tgt = spec.home if cmd.kind == CommandKind.return_home else GeoPoint(**cmd.params["target"])
            pos = move_toward(st.pos, tgt, step_m); upd["pos"] = pos
            if dist_m(pos, tgt) < 1: upd["waypoint_idx"] = -1  # arrived
            if cmd.kind == CommandKind.return_home and dist_m(pos, tgt) < 1: upd["status"] = VehicleStatus.maintenance
        elif cmd.kind == CommandKind.follow_route:
            route = [GeoPoint(**p) for p in cmd.params["route"]]; i = max(st.waypoint_idx, 0) % len(route)
            pos = move_toward(st.pos, route[i], step_m); upd["pos"] = pos
            if dist_m(pos, route[i]) < 1: upd["waypoint_idx"] = i + 1
        elif cmd.kind in (CommandKind.orbit, CommandKind.keep_distance):
            tg = next((t for t in targets if t.id == cmd.params.get("target_id")), None)
            if tg:
                r = float(cmd.params.get("distance_m", 150))
                if cmd.kind == CommandKind.orbit:
                    ang = math.radians(st.heading_deg + (spec.speed_mps * dt_ms / 1000) / r * 57.3)
                    upd["heading_deg"] = math.degrees(ang) % 360
                    upd["pos"] = GeoPoint(lat=tg.pos.lat + r * math.cos(ang) / M_PER_DEG_LAT, lon=tg.pos.lon + r * math.sin(ang) / m_per_deg_lon(tg.pos.lat), alt_m=st.pos.alt_m)
                else:
                    d = dist_m(st.pos, tg.pos)
                    upd["pos"] = move_toward(st.pos, tg.pos, min(step_m, max(d - r, 0))) if d > r else st.pos
        drain = 100 / spec.endurance_min * dt_ms / 60000
        upd["battery_pct"] = max(st.battery_pct - drain, 0)
        if st.status == VehicleStatus.ready: upd["status"] = VehicleStatus.active
        out.append(new.model_copy(update=upd))
    return out

# ---------- sim.apply_events / sensing.observe ----------
def apply_events(events, states, targets, t_ms, dt_ms, log):
    for ev in events:
        if not (t_ms - dt_ms < ev.t_ms <= t_ms): continue
        if ev.kind == "spawn_target":
            targets = targets + [Target(id=ev.params["id"], kind=ev.params["kind"], pos=GeoPoint(**ev.params["pos"]), vel_east_mps=ev.params.get("ve", 0), vel_north_mps=ev.params.get("vn", 0), first_seen_ms=0, last_seen_ms=0)]
        elif ev.kind == "vehicle_battery_set":
            states = [s.model_copy(update={"battery_pct": ev.params["pct"]}) if s.id == ev.params["id"] else s for s in states]
        log.append(f"[대본] t={t_ms//60000}m {ev.kind} {ev.params.get('id','')}")
    # targets drift
    nt = []
    for tg in targets:
        nt.append(tg.model_copy(update={"pos": GeoPoint(lat=tg.pos.lat + tg.vel_north_mps * dt_ms / 1000 / M_PER_DEG_LAT, lon=tg.pos.lon + tg.vel_east_mps * dt_ms / 1000 / m_per_deg_lon(tg.pos.lat))}))
    return states, nt
def observe(states, specs, targets, t_ms):
    out = []
    for tg in targets:
        seen = [s.id for s in states if s.status in (VehicleStatus.active, VehicleStatus.ready) and dist_m(s.pos, tg.pos) <= specs[s.id].sensor_range_m]
        upd = {"seen_by": seen}
        if seen: upd["last_seen_ms"] = t_ms; upd["first_seen_ms"] = tg.first_seen_ms or t_ms
        out.append(tg.model_copy(update=upd))
    return out

# ---------- safety.check_command ----------
def check_command(cmd, st, spec, op, play_approved=True) -> PassedCommand | Block:
    p = cmd.provenance
    if p is None or (p.source == CommandSource.play_step and not play_approved):
        return Block(command_id=cmd.id, vehicle_id=cmd.vehicle_id, reason=BlockReason.no_provenance, detail="출처 없음", t_ms=st.t_ms)
    dests = []
    if "target" in cmd.params: dests = [GeoPoint(**cmd.params["target"])]
    if "route" in cmd.params: dests = [GeoPoint(**q) for q in cmd.params["route"]]
    for d in dests:
        if not point_in_polygon(d, op.zone):
            # alternative: walk back along the line until inside, then 50 m more
            alt = d
            for k in range(1, 201):
                f = 1 - k / 200; cand = GeoPoint(lat=st.pos.lat + (d.lat - st.pos.lat) * f, lon=st.pos.lon + (d.lon - st.pos.lon) * f)
                if point_in_polygon(cand, op.zone): alt = move_toward(cand, st.pos, 50); break
            altc = cmd.model_copy(update={"id": cmd.id + "-alt", "params": {**cmd.params, "target": alt.model_dump()}})
            return Block(command_id=cmd.id, vehicle_id=cmd.vehicle_id, reason=BlockReason.outside_zone, detail="작전 구역 밖", alternative=altc, t_ms=st.t_ms)
    if dests:
        d = dests[-1]; need_s = (dist_m(st.pos, d) + dist_m(d, spec.home)) / spec.speed_mps
        have_s = spec.endurance_min * 60 * st.battery_pct / 100 * 0.8
        if need_s > have_s:
            return Block(command_id=cmd.id, vehicle_id=cmd.vehicle_id, reason=BlockReason.battery_insufficient, detail=f"필요 {need_s:.0f}s > 가용 {have_s:.0f}s", t_ms=st.t_ms)
    return PassedCommand(command=cmd, checks=["no_provenance", "outside_zone", "battery_insufficient"], passed_ms=st.t_ms)

# ---------- runtime ----------
from step_vehicle import step_vehicle
def assign_roles(play, states):
    out = []
    by = {s.id: s for s in states}
    for r in play.roles:
        v = next((vid for vid in r.vehicles if by[vid].status in (VehicleStatus.ready, VehicleStatus.active)), None)
        if v: out.append(Assignment(role_id=r.id, vehicle_id=v, since_ms=0, reason="계획 담당 지정"))
    return out

# ---------- scenario ----------
def gp(lat, lon): return GeoPoint(lat=lat, lon=lon)
zone = Polygon(points=[gp(37.90, 124.56), gp(37.90, 124.84), gp(38.00, 124.84), gp(38.00, 124.56)])  # north edge 38.00 = NLL stand-in
op = Operation(id="op1", name="백령도 야간 해안 경계", purpose="", area=zone, zone=zone, vehicle_ids=["d1", "d2", "d3", "usv", "ugv"])
home = gp(37.95, 124.70)
specs = {s.id: s for s in [
    VehicleSpec(id="d1", name="드론1", domain="air", speed_mps=15, endurance_min=40, sensor_range_m=800, capabilities=list(ActionKind), home=home),
    VehicleSpec(id="d2", name="드론2", domain="air", speed_mps=15, endurance_min=40, sensor_range_m=800, capabilities=list(ActionKind), home=home),
    VehicleSpec(id="d3", name="드론3", domain="air", speed_mps=15, endurance_min=40, sensor_range_m=800, capabilities=list(ActionKind), home=home),
    VehicleSpec(id="usv", name="수상정", domain="sea", speed_mps=8, endurance_min=720, sensor_range_m=500, capabilities=list(ActionKind), home=gp(37.94, 124.71)),
    VehicleSpec(id="ugv", name="지상로봇", domain="ground", speed_mps=5, endurance_min=480, sensor_range_m=300, capabilities=list(ActionKind), home=gp(37.955, 124.72)),
]}
routeA = [gp(37.98, 124.66).model_dump(), gp(37.98, 124.74).model_dump()]
routeB = [gp(37.93, 124.60).model_dump(), gp(37.93, 124.80).model_dump()]
ch = Choice(id="approach", label="근접 확인", step_by_role={"air": "A_watch", "sea": "S_approach", "ground": "G_landing", "air2": "A2_patrolA"})
play = Play(id="coast", name="해안 경계", approved=True, entry={"air": "A_patrol", "sea": "S_wait", "ground": "G_wait", "air2": "A2_wait"},
  roles=[Role(id="air", name="공중 순찰", domains=["air"], required=["patrol_route", "watch_target"], vehicles=["d1", "d3"]),
         Role(id="sea", name="해상 확인", domains=["sea"], required=["approach_target"], vehicles=["usv"]),
         Role(id="ground", name="상륙 감시", domains=["ground"], required=["move_to"], vehicles=["ugv"]),
         Role(id="air2", name="공중 예비", domains=["air"], required=["patrol_route"], vehicles=["d2"])],
  steps=[
    Step(id="A_patrol", role_id="air", name="순찰", lines=[Line(kind="patrol_route", params={"route": routeA}), Line(kind="if_cond", cond=Condition(kind="target_found"), then_step="A_report")]),
    Step(id="A_report", role_id="air", name="보고", lines=[Line(kind="report", params={"text": "미식별 선박"})], choices=[ch]),
    Step(id="A_watch", role_id="air", name="감시", lines=[Line(kind="watch_target", params={"target_id": "boat1", "distance_m": 150}), Line(kind="if_cond", cond=Condition(kind="battery_below", params={"pct": 30}), then_step="A_return")]),
    Step(id="A_return", role_id="air", name="귀환", lines=[Line(kind="return_home")]),
    Step(id="S_wait", role_id="sea", name="대기", lines=[Line(kind="wait", cond=Condition(kind="operator_choice"))]),
    Step(id="S_approach", role_id="sea", name="근접", lines=[Line(kind="approach_target", params={"target_id": "boat1", "distance_m": 200})]),
    Step(id="G_wait", role_id="ground", name="대기", lines=[Line(kind="wait", cond=Condition(kind="operator_choice"))]),
    Step(id="G_landing", role_id="ground", name="상륙지점", lines=[Line(kind="move_to", params={"target": gp(37.975, 124.70).model_dump()})]),
    Step(id="A2_wait", role_id="air2", name="대기", lines=[Line(kind="wait", cond=Condition(kind="operator_choice"))]),
    Step(id="A2_patrolA", role_id="air2", name="구역A 순찰", lines=[Line(kind="patrol_route", params={"route": routeB})]),
  ])
events = [ScenarioEvent(t_ms=11*60000, kind="spawn_target", params={"id": "boat1", "kind": "boat", "pos": gp(37.985, 124.70).model_dump(), "ve": 0, "vn": -1.0}),
          ScenarioEvent(t_ms=19*60000, kind="vehicle_battery_set", params={"id": "d1", "pct": 21})]
decision_script = {}  # t_ms -> (report_kind) resolved: operator answers 20s after report appears
direct_script = {31*60000: DirectControl(vehicle_id="d2", target=gp(38.05, 124.70), t_ms=31*60000)}  # north of NLL

def run(tick_ms=200, minutes=35):
    t = 0
    states = []
    for sid, sp in specs.items():
        states.append(VehicleState(id=sid, t_ms=0, pos=sp.home, heading_deg=0, battery_pct=100, status="ready"))
    assigns = assign_roles(play, states)
    role_of = {a.vehicle_id: a.role_id for a in assigns}
    states = [s.model_copy(update={"role_id": role_of.get(s.id), "play_id": play.id, "step_id": play.entry.get(role_of.get(s.id, ""), None)}) for s in states]
    targets, reports, blocks, log = [], [], [], []
    metrics = Metrics(); gap_start = None; handover_done = False; pending_decision_at = None
    frames = 0; t0 = time.perf_counter(); first_cmd_tick = {}; trace = []
    while t < minutes * 60000:
        t += tick_ms
        states, targets = apply_events(events, states, targets, t, tick_ms, log)
        targets = observe(states, specs, targets, t)
        # operator inputs (scripted): decide 20 s after the report card appears
        if pending_decision_at and t >= pending_decision_at:
            rep = next(r for r in reports if r.resolved_ms is None)
            rep.resolved_ms = t; metrics.operator_actions += 1; metrics.decisions += 1
            for a in assign_roles(play, states):
                tgt_step = ch.step_by_role.get(a.role_id)
                if tgt_step: states = [s.model_copy(update={"step_id": tgt_step, "line_idx": 0, "waypoint_idx": 0, "pending_report_id": None}) if s.id == a.vehicle_id else s for s in states]
            log.append(f"[계산] t={t//60000}m 결정 '근접 확인' → 역할 {len(assigns)}개 step 전이"); pending_decision_at = None
        cmds, direct = [], direct_script.pop(t, None)
        if direct:
            metrics.operator_actions += 1
            cmds.append(Command(id=f"dc-{t}", vehicle_id=direct.vehicle_id, kind="move", params={"target": direct.target.model_dump()}, provenance=Provenance(source="operator_direct", operator_id="op1", issued_ms=t)))
        new_states = []
        for s in states:
            s2, cmd, rep = step_vehicle(s, play, targets, t)
            if cmd: cmds.append(cmd)
            if rep: reports.append(rep); pending_decision_at = pending_decision_at or t + 20000; log.append(f"[계산] t={t//60000}m 보고 카드: {rep.text} by {rep.vehicle_id}")
            new_states.append(s2)
        states = new_states
        # handover (Role.vehicles order) when a vehicle leaves
        by = {s.id: s for s in states}
        for r in play.roles:
            cur = next((a for a in assigns if a.role_id == r.id), None)
            if cur and by[cur.vehicle_id].status in (VehicleStatus.returning, VehicleStatus.lost, VehicleStatus.maintenance) or (cur and by[cur.vehicle_id].step_id == "A_return"):
                nxt = next((v for v in r.vehicles if v != cur.vehicle_id and by[v].status in (VehicleStatus.ready, VehicleStatus.active)), None)
                if nxt and not handover_done:
                    handover_done = True
                    states = [s.model_copy(update={"role_id": r.id, "step_id": by[cur.vehicle_id].step_id if by[cur.vehicle_id].step_id != "A_return" else "A_watch", "line_idx": 0}) if s.id == nxt else s for s in states]
                    assigns = [Assignment(role_id=r.id, vehicle_id=nxt, since_ms=t, reason="예비 1번 투입") if a.role_id == r.id else a for a in assigns]
                    gap_start = t; log.append(f"[계산] t={t//60000}m 이어받기 {cur.vehicle_id}→{nxt}")
        passed = []
        for c in cmds:
            res = check_command(c, by[c.vehicle_id], specs[c.vehicle_id], op)
            if isinstance(res, Block):
                blocks.append(res); metrics.blocked_commands += 1; log.append(f"[계산] t={t//60000}m 차단 {res.reason.value} {res.detail}")
                if res.alternative:
                    res2 = check_command(res.alternative, by[c.vehicle_id], specs[c.vehicle_id], op)
                    if isinstance(res2, PassedCommand): passed.append(res2); log.append(f"[계산]   대안 적용 → {res2.command.params['target']}")
                    else: log.append(f"[계산]   대안도 차단 {res2.reason.value}")
            else:
                passed.append(res); metrics.commands_sent += 1
                if gap_start is not None and c.vehicle_id in [a.vehicle_id for a in assigns if a.reason.startswith("예비")]:
                    metrics.role_gap_ms += t - gap_start; gap_start = None
        if any(c.provenance.source in ("play_step",) for c in cmds): metrics.manual_baseline_actions += sum(1 for c in cmds if c.provenance.source == "play_step")
        states = advance(states, specs, passed, tick_ms, targets)
        metrics.open_reports_max = max(metrics.open_reports_max, sum(1 for r in reports if r.resolved_ms is None))
        if t % 60000 == 0 and t <= 20*60000:
            d1 = next(s for s in states if s.id == "d1"); tgd = min((dist_m(d1.pos, tg.pos) for tg in targets), default=-1)
            trace.append(f"  t={t//60000:2d}m d1 step={d1.step_id} line={d1.line_idx} wp={d1.waypoint_idx} dist_home={dist_m(d1.pos, specs['d1'].home):.0f} dist_tgt={tgd:.0f} bat={d1.battery_pct:.0f}")
        fr = Frame(t_ms=t, mode="role", vehicles=states, targets=targets, reports=reports, assignments=assigns, blocks=blocks, injections=[], metrics=metrics, log=log[-3:])
        fr.model_dump_json(); frames += 1
    el = time.perf_counter() - t0
    print(f"ACTIVE_FIELD={ACTIVE_FIELD} ticks={frames} wall={el:.2f}s per_tick={el/frames*1000:.3f}ms")
    for l in log[:25]: print(l)
    print("\n".join(trace))
    print("final:", {s.id: (s.step_id, s.status.value, round(s.battery_pct), round(dist_m(s.pos, specs[s.id].home))) for s in states})
    print("metrics:", metrics.model_dump())
run()
