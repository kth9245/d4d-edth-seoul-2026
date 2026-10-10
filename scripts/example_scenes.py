"""Eight scene Frames of the 3-minute script, hand-computed from example_world, in the strike-phase
order (docs/superpowers/specs/2026-10-10-strike-phase-design.md section 2): s1 s2 s3 s5 s6 s4 s7 s8.

Positions and batteries follow the world's speeds and routes approximately; the real engine will differ
by metres. They exist so the map and card screens can be built before the engine runs. s5/s6 times and
points match modules/gateway/tests/test_demo_timeline.py. The strike plays (track_fast_sea, strike) are
only named here; their JSON is in the demo scenario (Part1-19).
"""

from example_world import LANDING, MIN, PLAYS, SPECS, START_MS, gp

from contracts.models import (
    Assignment,
    Block,
    Choice,
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
# Observed risk in s7 (decisions 0039/0040, sensing fills it in the engine): fast1 scanned, emitting and fast.
BOAT_RISK = {"threat": 50, "threat_reasons": ["kind_boat", "inside_watch_radius"]}
FAST_RISK = {
    "threat": 100,
    "threat_reasons": ["kind_fast_boat", "rf_emission", "speed"],
    "rf_detected": True,
}


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


def boat(t, lat, seen):
    return Target(
        id="boat1",
        kind="boat",
        pos=gp(lat, 124.70),
        vel_east_mps=0,
        vel_north_mps=-1.0,
        first_seen_ms=at(11, 10),
        last_seen_ms=t,
        seen_by=seen,
    )


def fast(t, lat, lon, seen, hit=None):
    # fast1 runs east along the north coast from boat1 (decision 0033 item 6); struck = stopped.
    return Target(
        id="fast1",
        kind="fast_boat",
        pos=gp(lat, lon),
        vel_east_mps=0.0 if hit else 6.3,
        vel_north_mps=0.0,
        first_seen_ms=at(23),
        last_seen_ms=t,
        seen_by=seen,
        neutralized_ms=hit,
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


def pick(vid, t, decided, dec):
    choices = [Choice(id="fast1", label="fast1 fast_boat"), Choice(id="boat1", label="boat1 boat")]
    return Report(
        id=f"rep-{vid}-{t}",
        t_ms=t,
        kind="target_select",
        vehicle_id=vid,
        text=f"추적할 표적 선택({vid})",
        choices=choices,
        resolved_ms=decided,
        decision_id=dec,
    )


def strike_card(vid, t, dist):
    # '타격 승인 요청' of step ask in track_fast / track_fast_sea: one card per tracker (decision 0033).
    choices = [
        Choice(id=f"strike_{vid}", label="이 기체로 타격", play_by_vehicle={vid: "strike"}),
        Choice(
            id="strike_both", label="함께 타격", play_by_vehicle={"d2": "strike", "usv": "strike"}
        ),
    ]
    return Report(
        id=f"rep-{vid}-{t}",
        t_ms=t,
        kind="target_detected",
        vehicle_id=vid,
        target_id="fast1",
        text=f"타격 승인 요청 · {vid} 센서 탐지 · fast1(고속정) · {dist} m",
        choices=choices,
    )


# fmt: off
T1, T2, T3, T5, T6, T4 = at(11, 10), at(11, 30), at(19, 0), at(20, 0), at(20, 30), at(23, 30)
T7, HIT, T8 = at(25, 40), at(26, 15), at(26, 30)
START = [assign(v, p, START_MS, "작전 배정") for v, p in [("d1", "patrol_a"), ("d2", "standby"), ("d3", "standby"), ("usv", "standby"), ("ugv", "standby")]]
REP1 = Report(id=f"rep-d1-{T1}", t_ms=T1, kind="target_detected", vehicle_id="d1", target_id="boat1", text="미식별 선박 접근", choices=PLAYS["patrol_a"].steps[1].report.choices)
REP1_DONE = REP1.model_copy(update={"resolved_ms": T2, "decision_id": "dec-1"})
REP2 = Report(id=f"rep-d3-{T3}", t_ms=T3, kind="vehicle_gap", vehicle_id="d3", text="d1 귀환, 예비 d3 투입: 감시 공백")
REP2_DONE = REP2.model_copy(update={"resolved_ms": at(23, 0)})
AFTER_DECISION = [assign("d1", "watch", T2, "결정 dec-1"), assign("usv", "approach", T2, "결정 dec-1"), assign("ugv", "landing", T2, "결정 dec-1"), assign("d2", "patrol_b", T2, "결정 dec-1"), assign("d3", "standby", START_MS, "작전 배정")]
AFTER_TAKEOVER = [*AFTER_DECISION[:4], assign("d3", "watch", T3, "예비 투입: d1 대신")]
# s5/s6: patrolling d2 sent past the NLL (zone block, alternative taken at 20:05), then to the far
# south-east corner (battery block). Alternatives lie on the line from d2 to the requested point.
ALT1, ALT2 = gp(37.9995, 124.6768), gp(37.9196, 124.7652)
BLK1 = Block(command_id=f"cmd-d2-{T5}", vehicle_id="d2", reason="outside_zone", detail="작전 구역 밖(38.0500, 124.6600)", alternative=cmd("d2", "move", {"target": ALT1.model_dump()}, T5, source="operator_direct", operator_id="op1"), t_ms=T5)
BLK2 = Block(command_id=f"cmd-d2-{T6}", vehicle_id="d2", reason="battery_insufficient", detail="필요 2210s > 가용 1490s", alternative=cmd("d2", "move", {"target": ALT2.model_dump()}, T6, source="operator_direct", operator_id="op1"), t_ms=T6)
REP4 = Report(id=f"rep-d2-{T5}", t_ms=T5, kind="command_blocked", vehicle_id="d2", text="구역 밖 차단: d2 → 38.0500, 124.6600")
REP5 = Report(id=f"rep-d2-{T6}", t_ms=T6, kind="command_blocked", vehicle_id="d2", text="배터리 차단: d2 → 37.9050, 124.8350")
# s4: the operator presses '고속 보트 추적' (op.switches track_fast): d2 and the USV in one approval.
INJ = Injection(id="inj-1", t_ms=at(23, 20), label="고속 보트 추적", play_by_vehicle={"d2": "track_fast", "usv": "track_fast_sea"}, switch_id="track_fast")
REP3 = Report(id=f"rep-d2-{at(23, 20)}-i", t_ms=at(23, 20), kind="injection_pending", vehicle_id="d2", text="전환 승인 대기: 고속 보트 추적")
AFTER_SWITCH = [AFTER_TAKEOVER[0], assign("usv", "track_fast_sea", at(24), "전환 inj-1"), AFTER_TAKEOVER[2], assign("d2", "track_fast", at(24), "전환 inj-1"), AFTER_TAKEOVER[4]]
# s7/s8: a target pick per tracker, then a strike approval card each; '함께 타격' on d2's card.
PICKS = [pick("d2", at(24), at(24, 10), "dec-2"), pick("usv", at(24), at(24, 15), "dec-3")]
ASK_D2, ASK_USV = strike_card("d2", at(25), 300), strike_card("usv", at(25, 20), 420)
AFTER_STRIKE = [AFTER_TAKEOVER[0], assign("usv", "strike", at(25, 50), "결정 dec-4"), AFTER_TAKEOVER[2], assign("d2", "strike", at(25, 50), "결정 dec-4"), AFTER_TAKEOVER[4]]
HIT_CARD = Report(id=f"rep-d2-{HIT}", t_ms=HIT, kind="target_neutralized", vehicle_id="d2", target_id="fast1", text="fast1 무력화(d2)")


def scenes() -> dict[str, Frame]:
    ugv_go = cmd("ugv", "move", {"target": LANDING.model_dump()}, T2, "landing", "move")
    usv_go = cmd("usv", "keep_distance", {"target_id": "boat1", "distance_m": 200}, T2, "approach", "approach")
    d2_patrol = cmd("d2", "follow_route", PLAYS["patrol_b"].steps[0].do.params, T2, "patrol_b", "patrol")
    d3_watch = cmd("d3", "orbit", {"target_id": "boat1", "distance_m": 150}, T3, "watch", "watch")
    d2_alt = cmd("d2", "move", {"target": ALT1.model_dump()}, at(20, 5), source="operator_direct", operator_id="op1")
    d2_ask = cmd("d2", "orbit", {"target_id": "fast1", "distance_m": 300}, at(25), "track_fast", "ask")
    usv_ask = cmd("usv", "keep_distance", {"target_id": "fast1", "distance_m": 300}, at(25, 20), "track_fast_sea", "ask")
    aim = {"distance_m": 0, "target_id": "fast1", "target": gp(37.9812, 124.7155).model_dump()}
    d2_hit = cmd("d2", "strike", aim, at(25, 50), "strike", "strike", decision_id="dec-4")
    usv_hit = cmd("usv", "strike", aim, at(25, 50), "strike", "strike", decision_id="dec-4")
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

    def d1(t):  # back home since about 19:50
        return vs("d1", t, SPECS["d1"].home, 11.2, "maintenance", "watch", "return", cmd("d1", "return_home", {}, T3, "watch", "return"), waypoint_idx=-1)

    def d3(t, lat):
        return vs("d3", t, gp(lat, 124.70), 88.8, "active", "watch", "watch", d3_watch, target_id="boat1")

    def usv_boat1(t, lat):
        return vs("usv", t, gp(lat, 124.7012), 96.9, "active", "approach", "approach", usv_go, target_id="boat1", waypoint_idx=-1)

    def ugv(t):
        return vs("ugv", t, LANDING, 95.4, "active", "landing", "move", ugv_go, waypoint_idx=-1)

    d2_resume = {"resume_play_id": "patrol_b", "resume_step_id": "patrol"}
    s5 = frame(T5, [d1(T5), vs("d2", T5, gp(37.93, 124.70), 79.0, "active", "patrol_b", "patrol", d2_patrol, waypoint_idx=1),
                    d3(T5, 37.9655), usv_boat1(T5, 37.9790), ugv(T5)],
               [boat(T5, 37.97675, ["usv"])], [REP1_DONE, REP2, REP4], AFTER_TAKEOVER,
               Metrics(operator_actions=2, decisions=1, manual_baseline_actions=11, open_reports_max=1, commands_sent=8, blocked_commands=1, vehicle_gap_ms=60000),
               ["[계산] 21:20:00 직접 조종 dir-1 d2", "[계산] 21:20:00 차단 d2 outside_zone"], blocks=[BLK1])
    s6 = frame(T6, [d1(T6), vs("d2", T6, gp(37.9334, 124.6989), 77.8, "active", "patrol_b", "patrol", d2_alt, **d2_resume),
                    d3(T6, 37.9700), usv_boat1(T6, 37.9787), ugv(T6)],
               [boat(T6, 37.97645, ["usv"])], [REP1_DONE, REP2, REP4, REP5], AFTER_TAKEOVER,
               Metrics(operator_actions=4, decisions=1, manual_baseline_actions=12, open_reports_max=1, commands_sent=9, blocked_commands=2, vehicle_gap_ms=90000),
               ["[계산] 21:20:30 직접 조종 dir-3 d2", "[계산] 21:20:30 차단 d2 battery_insufficient"], blocks=[BLK1, BLK2])
    s4 = frame(T4, [d1(T4), vs("d2", T4, gp(37.9612, 124.6893), 70.0, "active", "patrol_b", "patrol", d2_alt, **d2_resume),
                    d3(T4, 37.9796), usv_boat1(T4, 37.9768), ugv(T4)],
               [boat(T4, 37.97465, ["d3", "usv"]), fast(T4, 37.9790, 124.7020, ["d3", "usv"])], [REP1_DONE, REP2_DONE, REP4, REP5, REP3], AFTER_TAKEOVER,
               Metrics(operator_actions=5, decisions=1, manual_baseline_actions=13, open_reports_max=1, commands_sent=9, blocked_commands=2, vehicle_gap_ms=240000),
               ["[대본] 21:23:00 적 등장 fast1", "[계산] 21:23:20 전환 inj-1 pending"], blocks=[BLK1, BLK2], injections=[INJ])
    before = [*s4.reports[:4], REP3.model_copy(update={"resolved_ms": at(24)})]
    approved = [INJ.model_copy(update={"status": "approved"})]
    s7 = frame(T7, [d1(T7), vs("d2", T7, gp(37.9839, 124.7128), 66.0, "active", "track_fast", "ask", d2_ask, target_id="fast1", pending_report_id=ASK_D2.id),
                    d3(T7, 37.9790),
                    vs("usv", T7, gp(37.9790, 124.7088), 96.1, "active", "track_fast_sea", "ask", usv_ask, target_id="fast1", pending_report_id=ASK_USV.id),
                    ugv(T7)],
               [boat(T7, 37.97335, ["d3"]).model_copy(update=BOAT_RISK),
                fast(T7, 37.9812, 124.7135, ["d2", "usv"]).model_copy(update=FAST_RISK)], [*before, *PICKS, ASK_D2, ASK_USV], AFTER_SWITCH,
               Metrics(operator_actions=8, decisions=3, manual_baseline_actions=21, open_reports_max=2, commands_sent=13, blocked_commands=2, vehicle_gap_ms=240000),
               ["[계산] 21:25:20 결정 dec-3 → fast1"], blocks=[BLK1, BLK2], injections=approved)
    asked = [r.model_copy(update={"resolved_ms": at(25, 50), "decision_id": "dec-4"}) for r in (ASK_D2, ASK_USV)]
    s8 = frame(T8, [d1(T8), vs("d2", T8, gp(37.9817, 124.7171), 64.9, "active", "strike", "strike", d2_hit, target_id="fast1", decision_id="dec-4"),
                    d3(T8, 37.9789),
                    vs("usv", T8, gp(37.9805, 124.7140), 95.9, "active", "strike", "strike", usv_hit, target_id="fast1", decision_id="dec-4"),
                    ugv(T8)],
               [boat(T8, 37.97285, ["d3"]), fast(T8, 37.9815, 124.7185, ["d2", "usv"], hit=HIT)], [*before, *PICKS, *asked, HIT_CARD], AFTER_STRIKE,
               Metrics(operator_actions=9, decisions=4, manual_baseline_actions=24, open_reports_max=2, commands_sent=15, blocked_commands=2, vehicle_gap_ms=240000, mission_success=True),
               ["[계산] 21:25:50 타격 명령 통과: d2 → fast1, 운용자 결정 dec-4 확인", "[계산] 21:25:50 타격 명령 통과: usv → fast1, 운용자 결정 dec-4 확인",
                "[계산] 21:26:15 fast1 무력화(d2)"], blocks=[BLK1, BLK2], injections=approved)
    return {"s1_report_wait": s1, "s2_after_decision": s2, "s3_takeover": s3, "s4_switch_pending": s4,
            "s5_zone_block": s5, "s6_battery_block": s6, "s7_strike_approval": s7, "s8_neutralized": s8}
# fmt: on
