"""RT-01 step_vehicle: 기체 하나의 현재 step을 한 틱 진행한다 (결정 0006 단순형).
step에 처음 들어가면 do 행동을 Command 하나로 내고(있으면 report 카드도), 그 뒤 매 틱 on 조건을 순서대로 봐
첫 참인 것의 go_step으로 옮긴다. 보고에 선택지가 있으면 Decision이 올 때까지 머문다.
SPEC: modules/runtime/SPEC.md#RT-01
"""
from models09 import (ActionKind, Command, CommandKind, CommandSource, ConditionKind, Play, Provenance,
                      Report, ReportKind, Step, Target, VehicleState)

_EXPAND = {ActionKind.move_to: CommandKind.move, ActionKind.patrol_route: CommandKind.follow_route,
           ActionKind.watch_target: CommandKind.orbit, ActionKind.approach_target: CommandKind.keep_distance,
           ActionKind.return_home: CommandKind.return_home, ActionKind.hold: CommandKind.hold}


def _cond_true(cond, st: VehicleState, targets: list[Target], t_ms: int) -> bool:
    if cond.kind == ConditionKind.target_found:
        return any(st.id in tg.seen_by for tg in targets)
    if cond.kind == ConditionKind.arrived:
        return st.waypoint_idx < 0  # sim이 현재 명령의 목적지에 닿으면 -1로 둔다
    if cond.kind == ConditionKind.battery_below:
        return st.battery_pct < float(cond.params.get("pct", 30))
    if cond.kind == ConditionKind.time_elapsed:
        return t_ms >= float(cond.params.get("until_ms", 0))
    return False  # operator_choice·signal_received는 Decision/신호 처리 액션이 옮긴다


def _find_step(play: Play, step_id: str | None) -> Step | None:
    return next((s for s in play.steps if s.id == step_id), None)


def step_vehicle(st: VehicleState, play: Play, targets: list[Target], t_ms: int
                 ) -> tuple[VehicleState, Command | None, Report | None]:
    step = _find_step(play, st.step_id)
    if step is None or st.status.value not in ("ready", "active") or st.pending_report_id:
        return st, None, None
    if not st.entered_step:  # step 진입: 명령 한 번, 보고 한 번
        prov = Provenance(source=CommandSource.play_step, play_id=play.id, step_id=step.id, issued_ms=t_ms)
        kind = _EXPAND.get(step.do.kind)
        cmd = None if kind is None else Command(id=f"c-{st.id}-{t_ms}", vehicle_id=st.id, kind=kind,
                                                params=dict(step.do.params), provenance=prov)
        rep, upd = None, {"entered_step": True, "waypoint_idx": 0}
        if step.report:
            seen = next((tg.id for tg in targets if st.id in tg.seen_by), None)
            rep = Report(id=f"rp-{st.id}-{t_ms}", t_ms=t_ms, kind=ReportKind.target_detected, vehicle_id=st.id,
                         target_id=seen, role_id=st.role_id, text=step.report.text, choices=step.report.choices)
            if step.report.choices:
                upd["pending_report_id"] = rep.id  # 결정을 기다린다
        return st.model_copy(update=upd), cmd, rep
    for ex in step.on:  # 탈출 조건: 첫 참인 것으로 전이
        if _cond_true(ex.cond, st, targets, t_ms):
            return st.model_copy(update={"step_id": ex.go_step, "entered_step": False}), None, None
    return st, None, None
