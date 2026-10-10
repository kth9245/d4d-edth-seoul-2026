"""RT-05 apply_injection: 승인된 전환(전체 전환 버튼·일부 전환)을 role_by_vehicle대로 적용 (사건 4)
지도에서 표적을 지목한 전환은 target_by_vehicle의 표적을 그 기체의 표적으로 둔다(결정 0048).
SPEC: modules/runtime/SPEC.md#RT-05
"""

from contracts.models import Injection, Role, VehicleState
from modules.runtime.actions.switch_role import switch_role


def apply_injection(
    states: list[VehicleState], roles: dict[str, Role], injection: Injection
) -> list[VehicleState]:
    to, tgt = injection.role_by_vehicle, injection.target_by_vehicle
    out = []
    for s in states:
        if s.id in to:
            s = switch_role(s, roles[to[s.id]])
            if s.id in tgt:  # pointed at a target on the map (decision 0048)
                s = s.model_copy(update={"target_id": tgt[s.id]})
        out.append(s)
    return out
