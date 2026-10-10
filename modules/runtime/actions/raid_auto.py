"""RT-21 raid_auto: 운용자 카드 없이 일어나는 적 대응(사용자 10/11, 전수 점검 10/11).
auto_watch: 멸공에서 공중의 대기·복귀 기체가 아무도 안 맡은 적을 보면 바로 감시. raid_held: 멸공에서 짝 기체가 결정·자동
감시로 떠 있으면 빈 순찰은 ④ 대체 순찰까지 비움. done_return: 다른 작전에서 무력화된 표적에 붙어 있던 기체는 순찰로, 순찰이 없으면 기지로(멸공은 RT-20 카드).
SPEC: modules/runtime/SPEC.md#RT-21"""

from collections.abc import Sequence

from contracts.models import Assignment, Operation, Polygon, Role, Target, VehicleSpec, VehicleState
from modules.runtime.actions.raid_cards import TRACK_ROLE
from modules.runtime.actions.switch_role import switch_role
from modules.runtime.actions.target_domain import target_domain

TK = ("watch_target", "approach_target", "strike_target")


def auto_watch(states: list[VehicleState], targets: list[Target], specs: dict[str, VehicleSpec],
               land: Sequence[Polygon], roles: dict[str, Role]) -> list[VehicleState]:  # fmt: skip
    """24h: an idle vehicle in the air (standby or going home, battery above 30%) that sees an enemy nobody has
    takes it at once, the patrol's own auto job (user 10/11). Drones take any, usv only sea, ugv only ground."""
    if "focus_orbit" not in roles:
        return states
    taken, out = {s.target_id for s in states if s.target_id}, []
    for s in states:
        dom = specs[s.id].domain.value if s.id in specs else None
        tg = next((t for t in targets if s.id in t.seen_by and t.neutralized_ms is None and t.id not in taken
                   and dom in ("air", target_domain(t, land))), None)  # fmt: skip
        if (tg and s.role_id in ("standby", "go_home") and s.status.value in ("active", "returning")
                and s.target_id is None and s.battery_pct > 30):  # fmt: skip
            s = switch_role(s, roles[TRACK_ROLE[dom]]).model_copy(update={"target_id": tg.id, "status": type(s.status).active, "active": None})  # stop the trip home  # fmt: skip
            taken.add(tg.id)
        out.append(s)
    return out


def raid_held(p: str, op: Operation, by: dict[str, VehicleState], assignments: list[Assignment],
              roles: dict[str, Role]) -> bool:  # fmt: skip
    """24h: coast p waits for the ④ cover card while a pool drone is out on a decision or an auto watch (user 10/11)."""
    why = {a.vehicle_id: a.reason for a in assignments}
    return "focus_orbit" in roles and any(by[w].status.value in ("active", "returning") and why.get(w, "").startswith(("결정", "자동 감시")) for w in op.rotation_pools.get(p) or op.rotation if w in by)  # fmt: skip


def done_return(
    states: list[VehicleState], targets: list[Target], roles: dict[str, Role]
) -> list[VehicleState]:
    """Not the 24h raid: a vehicle watching, approaching or striking a target that is down, on a step with no
    target_neutralized exit of its own (decision 0066), goes back to its patrol, or home if its role has none. Nobody
    loiters over a dead target and no card is left waiting; the operator can point it again (brute force 10/11)."""
    if "focus_orbit" in roles or "go_home" not in roles:
        return states
    down, out = {t.id for t in targets if t.neutralized_ms is not None}, []
    for s in states:
        role = roles.get(s.role_id or "")
        step = next((x for x in role.steps if x.id == s.step_id), None) if role else None
        if (step and s.target_id in down and s.status.value == "active" and step.do.kind.value in TK
                and not any(e.cond.kind.value == "target_neutralized" for e in step.on)):  # fmt: skip
            first = next(x for x in role.steps if x.id == role.entry)
            s = (s.model_copy(update={"step_id": role.entry, "entered_step": False, "target_id": None})
                 if first.do.kind.value == "patrol_route" else switch_role(s, roles["go_home"]))  # fmt: skip
        out.append(s)
    return out
