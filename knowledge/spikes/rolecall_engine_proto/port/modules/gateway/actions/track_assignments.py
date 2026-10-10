"""GW-05 track_assignments: Role이 바뀐 기체의 배정을 새 Role·시각·사유로 갈아 끼운다
SPEC: modules/gateway/SPEC.md#GW-05
"""

from contracts.models import Assignment, VehicleState


def track_assignments(
    assignments: list[Assignment],
    before: dict[str, str | None],
    states: list[VehicleState],
    t_ms: int,
    reason: str,
) -> list[Assignment]:
    changed = [s for s in states if s.role_id != before.get(s.id)]
    ids = {s.id for s in changed}
    keep = [a for a in assignments if a.vehicle_id not in ids]
    return keep + [
        Assignment(vehicle_id=s.id, role_id=s.role_id, since_ms=t_ms, reason=reason)
        for s in changed
    ]
