"""RT-01 step_vehicle: 기체 하나의 현재 step을 한 틱 진행 (결정 0006 단순형, 0015 두 층)
아직 안 들어갔으면 enter_step, 들어갔으면 on을 앞에서부터 봐 첫 참인 go_step으로.
결정 대기(pending_report_id)·ready/active 아님이면 그대로. 직접 조종 도착이면 resume step으로 복귀.
SPEC: modules/runtime/SPEC.md#RT-01
"""

from contracts.models import (
    Command,
    ConditionKind,
    Report,
    Role,
    Target,
    VehicleSpec,
    VehicleState,
)
from modules.runtime.actions.enter_step import TARGET_ACTIONS, enter_step
from modules.runtime.conditions import condition_true, resighted


def step_vehicle(
    st: VehicleState,
    spec: VehicleSpec,
    role: Role | None,
    targets: list[Target],
    t_ms: int,
    started_ms: int | None = None,
) -> tuple[VehicleState, Command | None, Report | None]:
    if st.step_id is None and st.resume_step_id and st.waypoint_idx < 0:  # direct control arrived
        back = {"step_id": st.resume_step_id, "entered_step": False}
        return (
            st.model_copy(update={**back, "resume_role_id": None, "resume_step_id": None}),
            None,
            None,
        )
    step = next((s for s in role.steps if s.id == st.step_id), None) if role else None
    if step is None or st.status.value not in ("ready", "active") or st.pending_report_id:
        return st, None, None
    if not st.entered_step:
        out, cmd, rep = enter_step(st, spec, role, step, targets, t_ms)
        if step.do.kind.value == "patrol_route" and st.patrol_step_id == step.id:  # decision 0066
            out = out.model_copy(
                update={"waypoint_idx": st.patrol_idx, "patrol_step_id": None, "patrol_idx": 0}
            )
        return out, cmd, rep  # coming back to a patrol continues from where it was left
    tracking = step.do.kind.value in TARGET_ACTIONS
    for ex in step.on:
        if condition_true(ex.cond, st, targets, tracking, t_ms, started_ms):
            upd = {"step_id": ex.go_step, "entered_step": False}
            if (
                ex.cond.kind == ConditionKind.target_resighted
            ):  # decision 0066 draft: watch that site
                upd["target_id"] = resighted(st, targets).id
            if step.do.kind.value == "patrol_route":  # decision 0066: remember where it was left
                upd |= {"patrol_step_id": step.id, "patrol_idx": max(st.waypoint_idx, 0)}
            return st.model_copy(update=upd), None, None
    return st, None, None
