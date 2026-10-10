"""RT-02 apply_reserves: 빠진 기체(returning·lost·maintenance)의 op.reserve 첫 가용 기체가
그 기체의 Role을 첫 step부터 시작한다(결정 0016·0022). 배정 사유 "예비 투입: <id> 대신", vehicle_gap 카드.
SPEC: modules/runtime/SPEC.md#RT-02
"""

from contracts.models import Assignment, Operation, Report, Role, VehicleState, VehicleStatus
from modules.runtime.actions.switch_role import switch_role

LIVE = (VehicleStatus.ready, VehicleStatus.active)
GONE = (VehicleStatus.returning, VehicleStatus.lost, VehicleStatus.maintenance)


def apply_reserves(
    states: list[VehicleState],
    op: Operation,
    roles: dict[str, Role],
    assignments: list[Assignment],
    t_ms: int,
) -> tuple[list[VehicleState], list[Assignment], Report | None]:
    by = {s.id: s for s in states}
    for vid, reserves in op.reserve.items():
        reason, gone = f"예비 투입: {vid} 대신", by.get(vid)
        if gone is None or gone.status not in GONE or any(a.reason == reason for a in assignments):
            continue
        nxt = next((r for r in reserves if by[r].status in LIVE), None)
        if nxt is None:
            continue
        by[nxt] = switch_role(by[nxt], roles[gone.role_id])
        new = Assignment(vehicle_id=nxt, role_id=gone.role_id, since_ms=t_ms, reason=reason)
        assignments = [a for a in assignments if a.vehicle_id != nxt] + [new]
        rep = Report(id=f"rep-{nxt}-{t_ms}", t_ms=t_ms, kind="vehicle_gap", vehicle_id=nxt,
                     text=f"{vid} 이탈, 예비 {nxt} 투입: 공백 측정 중")  # fmt: skip
        return [by[s.id] for s in states], assignments, rep
    return states, assignments, None
