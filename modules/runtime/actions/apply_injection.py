"""RT-05 apply_injection: 승인된 전환(전체 전환 버튼·일부 전환)을 role_by_vehicle대로 적용 (사건 4)
지도·기체 메뉴에서 표적을 지목한 전환은 target_by_vehicle의 표적을 그 기체의 표적으로 두고(결정 0048),
그 전환 id를 기체의 결정 id로 적는다: 기체·표적·Role을 골라 누른 것이 그 표적에 대한 운용자 결정이라
타격 Role도 안전 규칙 1(출처)을 통과한다(결정 0058). 표적 없이 옮긴 기체는 결정 id가 없다.
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
            if s.id in tgt:  # pointed at a target (decisions 0048, 0058)
                s = s.model_copy(update={"target_id": tgt[s.id], "decision_id": injection.id})
        out.append(s)
    return out
