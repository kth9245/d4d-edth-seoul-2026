"""RT-07 apply_emergency: 기체의 현재 Role 비상 규칙(배터리 부족)에 걸리면 지정 step으로
틱에서 step_vehicle 바로 앞에 부른다. 지정 step이 없으면 그 Role의 귀환 step, 그것도 없으면 go_home Role로(전수 점검 10/11). 시연 Role은 감시 Role의 on(battery_below)으로 귀환한다.
SPEC: modules/runtime/SPEC.md#RT-07
"""

from contracts.models import EmergencyKind, Role, VehicleState, VehicleStatus
from modules.runtime.actions.switch_role import switch_role

LIVE = (VehicleStatus.ready, VehicleStatus.active)


def apply_emergency(states: list[VehicleState], roles: dict[str, Role]) -> list[VehicleState]:
    out = []
    for s in states:
        role = roles.get(s.role_id or "")
        rule = role.emergency if role else None
        low = rule and s.status in LIVE and s.battery_pct < rule.battery_low_pct
        # its own step, else the role's return step (a reserve takes over, 0016), else the go_home role
        step = (rule.battery_low_step or next((x.id for x in role.steps if x.do.kind.value == "return_home"), None)
                if low else None)  # fmt: skip
        if low and step and s.step_id != step:
            upd = {"step_id": step, "entered_step": False}
            s = s.model_copy(update={**upd, "emergency": EmergencyKind.battery_low})
        elif low and not step and s.role_id != "go_home" and "go_home" in roles:
            s = switch_role(s, roles["go_home"]).model_copy(
                update={"emergency": EmergencyKind.battery_low}
            )
        out.append(s)
    return out
