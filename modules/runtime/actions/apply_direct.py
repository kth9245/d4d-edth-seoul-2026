"""RT-06 apply_direct: 운용자 직접 조종 → operator_direct move 명령, 기체는 step을 비우고 resume에 보관
도착하면 step_vehicle이 resume step으로 되돌린다. 차단되면 틱 루프가 이 기체 상태를 되돌린다(run_checks).
SPEC: modules/runtime/SPEC.md#RT-06
"""

from contracts.models import Command, DirectControl, Provenance, VehicleState


def apply_direct(
    states: list[VehicleState], direct: DirectControl, t_ms: int
) -> tuple[list[VehicleState], Command]:
    prov = Provenance(source="operator_direct", operator_id="op1", issued_ms=t_ms)
    cmd = Command(id=f"cmd-{direct.vehicle_id}-{t_ms}", vehicle_id=direct.vehicle_id, kind="move",
                  params={"target": direct.target.model_dump()}, provenance=prov)  # fmt: skip

    def mark(s: VehicleState) -> VehicleState:
        if s.id != direct.vehicle_id:
            return s
        keep = s.step_id is None  # already under direct control: keep the first resume point
        role, step = (s.resume_role_id, s.resume_step_id) if keep else (s.role_id, s.step_id)
        return s.model_copy(update={"step_id": None, "entered_step": True, "waypoint_idx": 0,
                                    "resume_role_id": role, "resume_step_id": step})  # fmt: skip

    return [mark(s) for s in states], cmd
