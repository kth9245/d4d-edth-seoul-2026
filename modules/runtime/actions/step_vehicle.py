"""RT-01 step_vehicle: 기체 하나의 현재 step을 한 틱 진행 (결정 0006 단순형, 0015 두 층)
아직 안 들어갔으면 enter_step, 들어갔으면 on을 앞에서부터 봐 첫 참인 go_step으로.
결정 대기(pending_report_id)·ready/active 아님이면 그대로. 직접 조종 도착이면 resume step으로 복귀.
SPEC: modules/runtime/SPEC.md#RT-01
"""

from contracts.models import (
    Command,
    Condition,
    ConditionKind,
    Play,
    Report,
    Target,
    VehicleSpec,
    VehicleState,
)
from modules.runtime.actions.enter_step import enter_step


def _true(cond: Condition, st: VehicleState, targets: list[Target]) -> bool:
    if cond.kind == ConditionKind.target_found:  # decision 0036: my target, else a new contact
        if st.target_id:
            return any(tg.id == st.target_id and st.id in tg.seen_by for tg in targets)
        return any(st.id in tg.seen_by and tg.reported_by is None for tg in targets)
    if cond.kind == ConditionKind.arrived:
        return st.waypoint_idx < 0
    if cond.kind == ConditionKind.battery_below:
        return st.battery_pct < float(cond.params.get("pct", 30))
    return False  # time_elapsed·operator_choice·signal_received: 시연 플레이에서 안 씀


def step_vehicle(
    st: VehicleState, spec: VehicleSpec, play: Play | None, targets: list[Target], t_ms: int
) -> tuple[VehicleState, Command | None, Report | None]:
    if st.step_id is None and st.resume_step_id and st.waypoint_idx < 0:  # direct control arrived
        back = {"step_id": st.resume_step_id, "entered_step": False}
        return (
            st.model_copy(update={**back, "resume_play_id": None, "resume_step_id": None}),
            None,
            None,
        )
    step = next((s for s in play.steps if s.id == st.step_id), None) if play else None
    if step is None or st.status.value not in ("ready", "active") or st.pending_report_id:
        return st, None, None
    if not st.entered_step:
        return enter_step(st, spec, play, step, targets, t_ms)
    for ex in step.on:
        if _true(ex.cond, st, targets):
            return st.model_copy(update={"step_id": ex.go_step, "entered_step": False}), None, None
    return st, None, None
