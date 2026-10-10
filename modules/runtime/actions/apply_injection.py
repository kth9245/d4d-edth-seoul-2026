"""RT-05 apply_injection: 승인된 전환(전체 전환 버튼·일부 전환)을 play_by_vehicle대로 적용 (사건 4)
SPEC: modules/runtime/SPEC.md#RT-05
"""

from contracts.models import Injection, Play, VehicleState
from modules.runtime.actions.switch_play import switch_play


def apply_injection(
    states: list[VehicleState], plays: dict[str, Play], injection: Injection
) -> list[VehicleState]:
    to = injection.play_by_vehicle
    return [switch_play(s, plays[to[s.id]]) if s.id in to else s for s in states]
