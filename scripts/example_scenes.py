"""Six scene Frames of the 3-minute script (08 5.4), hand-computed from example_world.

Positions and batteries follow the world's speeds and routes approximately; the real engine will differ
by metres. They exist so the map and card screens can be built before the engine runs.
"""

from example_world import LANDING, MIN, PLAYS, SPECS, START_MS, gp

from contracts.models import (
    Assignment,
    Block,
    Command,
    Frame,
    Injection,
    Metrics,
    PassedCommand,
    Provenance,
    Report,
    RunState,
    Target,
    VehicleState,
)

CHECKS = ["no_provenance", "outside_zone", "battery_insufficient"]


def at(m: int, s: int = 0) -> int:
    return START_MS + m * MIN + s * 1000


def cmd(vid, kind, params, t, play=None, step=None, source="play_step", **prov) -> Command:
    p = Provenance(source=source, play_id=play, step_id=step, issued_ms=t, **prov)
    return Command(id=f"cmd-{vid}-{t}", vehicle_id=vid, kind=kind, params=params, provenance=p)


def vs(vid, t, pos, bat, status, play, step, active=None, **kw) -> VehicleState:
    pc = (
        PassedCommand(command=active, checks=CHECKS, passed_ms=active.provenance.issued_ms)
        if active
        else None
    )
    return VehicleState(
        id=vid,
        t_ms=t,
        pos=pos,
        heading_deg=0,
        battery_pct=bat,
        status=status,
        play_id=play,
        step_id=step,
        entered_step=True,
        active=pc,
        **kw,
    )


def standby(vid, t):
    return vs(vid, t, SPECS[vid].home, 100, "ready", "standby", "wait")


def assign(vid, play, since, reason):
    return Assignment(vehicle_id=vid, play_id=play, since_ms=since, reason=reason)


def boat(t, lat, seen, fast=False):
    tid, kind, ve, vn, first = (
        ("fast1", "fast_boat", -2.0, 6.0, at(23))
        if fast
        else ("boat1", "boat", 0, -1.0, at(11, 10))
    )
    return Target(
        id=tid,
        kind=kind,
        pos=gp(lat, 124.6993 if fast else 124.70),
        vel_east_mps=ve,
        vel_north_mps=vn,
        first_seen_ms=first,
        last_seen_ms=t,
        seen_by=seen,
    )


def frame(t, vehicles, targets, reports, assignments, metrics, log, blocks=(), injections=()):
    return Frame(
        t_ms=t,
        run=RunState(status="running", speed=1.0),
        vehicles=vehicles,
        targets=targets,
        reports=reports,
        assignments=assignments,
        blocks=list(blocks),
        injections=list(injections),
        metrics=metrics,
        log=log,
    )


# fmt: off
T1, T2, T3, T4, T5, T6 = at(11, 10), at(11, 30), at(19, 0), at(23, 30), at(31, 0), at(31, 30)
START = [assign(v, p, START_MS, "작전 배정") for v, p in [("d1", "patrol_a"), ("d2", "standby"), ("d3", "standby"), ("usv", "standby"), ("ugv", "standby")]]
REP1 = Report(id=f"rep-d1-{T1}", t_ms=T1, kind="target_detected", vehicle_id="d1", target_id="boat1", text="미식별 선박 접근", choices=PLAYS["patrol_a"].steps[1].report.choices)
REP1_DONE = REP1.model_copy(update={"resolved_ms": T2, "decision_id": "dec-1"})
REP2 = Report(id=f"rep-d3-{T3}", t_ms=T3, kind="vehicle_gap", vehicle_id="d3", text="d1 귀환, 예비 d3 투입: 감시 공백")
REP2_DONE = REP2.model_copy(update={"resolved_ms": at(23, 0)})
INJ = Injection(id="inj-1", t_ms=at(23, 20), label="고속 보트 추적: d2", play_by_vehicle={"d2": "track_fast"})
REP3 = Report(id=f"rep-d2-{at(23, 20)}", t_ms=at(23, 20), kind="injection_pending", vehicle_id="d2", target_id="fast1", text="전환 승인 대기: 고속 보트 추적(d2)")
AFTER_DECISION = [assign("d1", "watch", T2, "결정 dec-1"), assign("usv", "approach", T2, "결정 dec-1"), assign("ugv", "landing", T2, "결정 dec-1"), assign("d2", "patrol_b", T2, "결정 dec-1"), assign("d3", "standby", START_MS, "작전 배정")]
AFTER_TAKEOVER = [*AFTER_DECISION[:4], assign("d3", "watch", T3, "예비 투입: d1 대신")]
AFTER_SWITCH = [*AFTER_TAKEOVER[:3], assign("d2", "track_fast", at(24), "전환 inj-1"), AFTER_TAKEOVER[4]]
ALT1 = gp(37.99955, 124.6903)
BLK1 = Block(command_id=f"cmd-d2-{T5}", vehicle_id="d2", reason="outside_zone", detail="작전 구역 밖(38.0500, 124.7000)", alternative=cmd("d2", "move", {"target": ALT1.model_dump()}, T5, source="operator_direct", operator_id="op1"), t_ms=T5)
BLK2 = Block(command_id=f"cmd-d2-{T6}", vehicle_id="d2", reason="battery_insufficient", detail="필요 1873s > 가용 960s", alternative=cmd("d2", "move", {"target": gp(37.9509, 124.6255).model_dump()}, T6, source="operator_direct", operator_id="op1"), t_ms=T6)
REP4 = Report(id=f"rep-d2-{T5}", t_ms=T5, kind="command_blocked", vehicle_id="d2", text="구역 밖 차단: d2 → 38.0500, 124.7000")
REP5 = Report(id=f"rep-d2-{T6}", t_ms=T6, kind="command_blocked", vehicle_id="d2", text="배터리 차단: d2 → 37.9050, 124.5650")


def scenes() -> dict[str, Frame]:
    ugv_go = cmd("ugv", "move", {"target": LANDING.model_dump()}, T2, "landing", "move")
    usv_go = cmd("usv", "keep_distance", {"target_id": "boat1", "distance_m": 200}, T2, "approach", "approach")
    d2_patrol = cmd("d2", "follow_route", PLAYS["patrol_b"].steps[0].do.params, T2, "patrol_b", "patrol")
    d3_watch = cmd("d3", "orbit", {"target_id": "boat1", "distance_m": 150}, T3, "watch", "watch")
    d2_track = cmd("d2", "orbit", {"target_id": "fast1", "distance_m": 300}, at(24), "track_fast", "track")
    d2_alt = cmd("d2", "move", {"target": ALT1.model_dump()}, at(31, 10), source="operator_direct", operator_id="op1")
    s1 = frame(T1, [vs("d1", T1, gp(37.98, 124.695), 72.1, "active", "patrol_a", "report", cmd("d1", "hold", {}, T1, "patrol_a", "report"), pending_report_id=REP1.id),
                    standby("d2", T1), standby("d3", T1), standby("usv", T1), standby("ugv", T1)],
               [boat(T1, 37.98437, ["d1"])], [REP1], START,
               Metrics(manual_baseline_actions=3, open_reports_max=1, commands_sent=2),
               ["[대본] 21:11 spawn_target boat1", "[계산] 21:11 d1 표적 발견 → 보고 카드"])
    s2 = frame(T2, [vs("d1", T2, gp(37.9835, 124.7015), 71.3, "active", "watch", "watch", cmd("d1", "orbit", {"target_id": "boat1", "distance_m": 150}, T2, "watch", "watch"), target_id="boat1"),
                    vs("d2", T2, SPECS["d2"].home, 100, "active", "patrol_b", "patrol", d2_patrol), standby("d3", T2),
                    vs("usv", T2, gp(37.9405, 124.7098), 98.4, "active", "approach", "approach", usv_go, target_id="boat1"),
                    vs("ugv", T2, gp(37.9551, 124.7199), 97.6, "active", "landing", "move", ugv_go)],
               [boat(T2, 37.98419, ["d1"])], [REP1_DONE], AFTER_DECISION,
               Metrics(operator_actions=1, decisions=1, manual_baseline_actions=7, open_reports_max=1, commands_sent=6),
               ["[계산] 21:11 결정 dec-1 '근접 확인' → 기체 4대 플레이 전환"])
    s3 = frame(T3, [vs("d1", T3, gp(37.981, 124.701), 21.0, "returning", "watch", "return", cmd("d1", "return_home", {}, T3, "watch", "return")),
                    vs("d2", T3, gp(37.93, 124.72), 81.3, "active", "patrol_b", "patrol", d2_patrol, waypoint_idx=1),
                    vs("d3", T3, SPECS["d3"].home, 100, "active", "watch", "watch", d3_watch, target_id="boat1"),
                    vs("usv", T3, gp(37.977, 124.703), 97.4, "active", "approach", "approach", usv_go, target_id="boat1"),
                    vs("ugv", T3, gp(37.972, 124.703), 96.0, "active", "landing", "move", ugv_go)],
               [boat(T3, 37.9807, ["usv"])], [REP1_DONE, REP2], AFTER_TAKEOVER,
               Metrics(operator_actions=1, decisions=1, manual_baseline_actions=10, open_reports_max=1, commands_sent=8),
               ["[대본] 21:19 vehicle_battery_set d1 21%", "[계산] 21:19 d1 배터리 30% 미만 → 귀환", "[계산] 21:19 예비 투입 d3 ← d1(감시)"])
    s4 = frame(T4, [vs("d1", T4, SPECS["d1"].home, 11.2, "maintenance", "watch", "return", cmd("d1", "return_home", {}, T3, "watch", "return"), waypoint_idx=-1),
                    vs("d2", T4, gp(37.93, 124.62), 70.0, "active", "patrol_b", "patrol", d2_patrol, waypoint_idx=2),
                    vs("d3", T4, gp(37.9796, 124.70), 88.8, "active", "watch", "watch", d3_watch, target_id="boat1"),
                    vs("usv", T4, gp(37.9802, 124.7012), 96.8, "active", "approach", "approach", usv_go, target_id="boat1", waypoint_idx=-1),
                    vs("ugv", T4, LANDING, 95.1, "active", "landing", "move", ugv_go, waypoint_idx=-1)],
               [boat(T4, 37.97825, ["d3", "usv"]), boat(T4, 37.9799, ["d3", "usv"], fast=True)], [REP1_DONE, REP2_DONE, REP3], AFTER_TAKEOVER,
               Metrics(operator_actions=2, decisions=1, manual_baseline_actions=11, open_reports_max=1, commands_sent=8, vehicle_gap_ms=240000),
               ["[대본] 21:23 split_target boat1 → fast1", "[계산] 21:23 d3 표적 도달, 기체 공백 4분 0초", "[계산] 21:23 전환 요청 inj-1 승인 대기"], injections=[INJ])
    done = [REP1_DONE, REP2_DONE, REP3.model_copy(update={"resolved_ms": at(24)})]
    later = [s4.vehicles[0], s4.vehicles[2], s4.vehicles[3], s4.vehicles[4]]
    s5 = frame(T5, [*later[:1], vs("d2", T5, gp(37.998, 124.69), 51.3, "active", "track_fast", "track", d2_track, target_id="fast1"), *later[1:]],
               [boat(T5, 37.97375, ["d3", "usv"]), boat(T5, 38.0055, ["d2"], fast=True)], [*done, REP4], AFTER_SWITCH,
               Metrics(operator_actions=4, decisions=1, manual_baseline_actions=13, open_reports_max=1, commands_sent=9, blocked_commands=1, vehicle_gap_ms=240000),
               ["[계산] 21:31 직접 조종 dir-1 d2 → 38.0500, 124.7000", "[계산] 21:31 차단 outside_zone, 대안 37.9996, 124.6903"],
               blocks=[BLK1], injections=[INJ.model_copy(update={"status": "approved"})])
    s6 = frame(T6, [*later[:1], vs("d2", T6, gp(37.9993, 124.6905), 50.0, "active", "track_fast", "track", d2_alt, target_id="fast1", resume_play_id="track_fast", resume_step_id="track"), *later[1:]],
               [boat(T6, 37.9734, ["d3", "usv"]), boat(T6, 38.0073, [], fast=True)], [*done, REP4, REP5], AFTER_SWITCH,
               Metrics(operator_actions=6, decisions=1, manual_baseline_actions=14, open_reports_max=2, commands_sent=10, blocked_commands=2, vehicle_gap_ms=240000),
               ["[계산] 21:31 직접 조종 dir-2(대안) 통과", "[계산] 21:31 직접 조종 dir-3 차단 battery_insufficient, 대안 37.9509, 124.6255"],
               blocks=[BLK1, BLK2], injections=s5.injections)
    return {"s1_report_wait": s1, "s2_after_decision": s2, "s3_takeover": s3,
            "s4_switch_pending": s4, "s5_zone_block": s5, "s6_battery_block": s6}
# fmt: on
