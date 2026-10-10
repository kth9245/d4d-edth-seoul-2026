"""RT-07 apply_emergency: 기체의 현재 Role 비상 규칙(배터리 부족)에 걸리면 지정 step으로
틱에서 step_vehicle 바로 앞에 부른다. 시연 Role은 감시 Role의 on(battery_below)으로 귀환한다.
SPEC: modules/runtime/SPEC.md#RT-07
"""

from contracts.models import EmergencyKind, Role, VehicleState, VehicleStatus

LIVE = (VehicleStatus.ready, VehicleStatus.active)


def apply_emergency(states: list[VehicleState], roles: dict[str, Role]) -> list[VehicleState]:
    out = []
    for s in states:
        rule = roles[s.role_id].emergency if s.role_id in roles else None
        low = rule and s.status in LIVE and s.battery_pct < rule.battery_low_pct
        if low and rule.battery_low_step and s.step_id != rule.battery_low_step:
            upd = {"step_id": rule.battery_low_step, "entered_step": False}
            s = s.model_copy(update={**upd, "emergency": EmergencyKind.battery_low})
        out.append(s)
    return out
