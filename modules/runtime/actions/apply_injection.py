"""RT-05 apply_injection: 승인된 전환(전체 전환 버튼·일부 전환)을 role_by_vehicle대로 적용 (사건 4)
SPEC: modules/runtime/SPEC.md#RT-05
"""

from contracts.models import Injection, Role, VehicleState
from modules.runtime.actions.switch_role import switch_role


def apply_injection(
    states: list[VehicleState], roles: dict[str, Role], injection: Injection
) -> list[VehicleState]:
    to = injection.role_by_vehicle
    return [switch_role(s, roles[to[s.id]]) if s.id in to else s for s in states]
