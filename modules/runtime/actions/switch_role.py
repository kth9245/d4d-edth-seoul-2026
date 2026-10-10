"""RT-09 switch_role: 기체를 다른 Role의 첫 step으로 옮긴다 (결정·전환 승인·예비 이어받기가 쓴다)
원래 Role은 끝나고 자동 복귀는 없다(결정 0016).
SPEC: modules/runtime/SPEC.md#RT-09
"""

from contracts.models import Role, VehicleState


def switch_role(st: VehicleState, role: Role) -> VehicleState:
    return st.model_copy(
        update={
            "role_id": role.id,
            "step_id": role.entry,
            "entered_step": False,
            "target_id": None,
            "pending_report_id": None,
            "waypoint_idx": 0,
            "resume_role_id": None,
            "resume_step_id": None,
            "patrol_step_id": None,  # decision 0066: step ids repeat across roles
            "patrol_idx": 0,
            "decision_id": None,
        }
    )
