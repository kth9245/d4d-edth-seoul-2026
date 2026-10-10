"""RT-09 switch_play: 기체를 다른 플레이의 첫 step으로 옮긴다 (결정·전환 승인·예비 이어받기가 쓴다)
원래 플레이는 끝나고 자동 복귀는 없다(결정 0016).
SPEC: modules/runtime/SPEC.md#RT-09
"""

from contracts.models import Play, VehicleState


def switch_play(st: VehicleState, play: Play) -> VehicleState:
    return st.model_copy(
        update={
            "play_id": play.id,
            "step_id": play.entry,
            "entered_step": False,
            "target_id": None,
            "pending_report_id": None,
            "waypoint_idx": 0,
            "resume_play_id": None,
            "resume_step_id": None,
            "decision_id": None,
        }
    )
