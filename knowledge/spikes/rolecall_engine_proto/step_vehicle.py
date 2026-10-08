"""RT-01 step_vehicle: 기체 하나의 (play, step, line_idx)를 한 틱 진행해 Command 0~1개와 Report 0~1개를 만든다.
SPEC: modules/runtime/SPEC.md#RT-01
"""
from models09 import (ActionKind, Command, CommandKind, CommandSource, ConditionKind, Line, Play, Provenance,
                      Report, ReportKind, Step, Target, VehicleState)

_EXPAND = {ActionKind.move_to: CommandKind.move, ActionKind.patrol_route: CommandKind.follow_route,
           ActionKind.watch_target: CommandKind.orbit, ActionKind.approach_target: CommandKind.keep_distance,
           ActionKind.return_home: CommandKind.return_home}


def _cond_true(cond, st: VehicleState, targets: list[Target], t_ms: int) -> bool:
    if cond is None:
        return True
    if cond.kind == ConditionKind.target_found:
        return any(st.id in tg.seen_by for tg in targets)
    if cond.kind == ConditionKind.arrived:
        return st.waypoint_idx < 0  # sim sets -1 when the current command's destination is reached
    if cond.kind == ConditionKind.battery_below:
        return st.battery_pct < float(cond.params.get("pct", 30))
    if cond.kind == ConditionKind.time_elapsed:
        return t_ms >= float(cond.params.get("until_ms", 0))
    return False  # operator_choice·signal_received: 결정/신호 액션이 따로 처리


def _find_step(play: Play, step_id: str | None) -> Step | None:
    return next((s for s in play.steps if s.id == step_id), None)


def _advance(st: VehicleState, step: Step) -> VehicleState:
    if st.line_idx + 1 < len(step.lines):
        return st.model_copy(update={"line_idx": st.line_idx + 1})
    return st.model_copy(update={"step_id": step.next_step, "line_idx": 0})


def step_vehicle(st: VehicleState, play: Play, targets: list[Target], t_ms: int
                 ) -> tuple[VehicleState, Command | None, Report | None]:
    step = _find_step(play, st.step_id)
    if step is None or st.status.value not in ("ready", "active") or st.pending_report_id:
        return st, None, None
    line: Line = step.lines[st.line_idx]
    if not _cond_true(line.cond, st, targets, t_ms):
        return st, None, None  # 조건이 거짓이면 그 줄에 머문다
    prov = Provenance(source=CommandSource.play_step, play_id=play.id, step_id=step.id, line_idx=st.line_idx, issued_ms=t_ms)
    if line.kind == ActionKind.if_cond:
        nxt = st.model_copy(update={"step_id": line.then_step, "line_idx": 0})
        return nxt, None, None
    if line.kind in (ActionKind.report, ActionKind.require_approval):
        seen = next((tg.id for tg in targets if st.id in tg.seen_by), None)
        rep = Report(id=f"rp-{st.id}-{t_ms}", t_ms=t_ms, kind=ReportKind.target_detected, vehicle_id=st.id,
                     target_id=seen, role_id=st.role_id, text=str(line.params.get("text", "")), choices=step.choices)
        # 보고 줄은 기체를 멈춘다: Decision이 pending_report_id를 지울 때까지 어떤 줄도 진행하지 않는다
        return st.model_copy(update={"pending_report_id": rep.id}), None, rep
    kind = _EXPAND.get(line.kind)
    if kind is None:
        return _advance(st, step), None, None  # 뒤쪽 7종: 이번 통합에서는 건너뛴다
    cmd = Command(id=f"c-{st.id}-{t_ms}", vehicle_id=st.id, kind=kind, params=dict(line.params), provenance=prov)
    return _advance(st, step), cmd, None
