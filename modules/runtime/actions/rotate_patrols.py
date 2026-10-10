"""RT-10 rotate_patrols: 해안 순찰 교대(결정 0037). 교대 시점은 relief_due(RT-14), 그때 대기 기체 출발, 경로점 m에 닿으면 인계·나간 기체 귀환(그 전까지 순찰 계속). 하한선 우선, rotation_pools 짝 안에서만, 비면 아무것도 안 함. 멸공은 짝 기체가 결정·자동 감시로 떠 있으면 빈 순찰을 ④ 대체 순찰까지 비워 둠(사용자 10/11).
SPEC: modules/runtime/SPEC.md#RT-10
"""

import re

from contracts.models import Assignment, GeoPoint, Operation, Role, VehicleSpec, VehicleState
from modules.runtime.actions.raid_idle import raid_held
from modules.runtime.actions.relief_due import FLOOR, _back, relief_due
from modules.runtime.actions.switch_role import switch_role
from shared.geo import dist_m

MEET_M = 500.0  # handover m; FLOOR and START live in relief_due
OUT = re.compile(r"교대 출발: (\S+) → (\S+) @(\d+)")


def _point(role: Role, m: int) -> GeoPoint:  # route point m of the patrol (it wraps)
    route = role.steps[0].do.params["route"]
    return GeoPoint(**route[m % len(route)])


def rotate_patrols(
    states: list[VehicleState],
    specs: dict[str, VehicleSpec],
    op: Operation,
    roles: dict[str, Role],
    assignments: list[Assignment],
    t_ms: int,
) -> tuple[list[VehicleState], list[Assignment]]:
    if not op.rotation or not op.rotation_roles:
        return states, assignments
    by, asg = {s.id: s for s in states}, list(assignments)

    def note(vid: str, role: str, reason: str) -> None:
        asg[:] = [a for a in asg if a.vehicle_id != vid]
        asg.append(Assignment(vehicle_id=vid, role_id=role, since_ms=t_ms, reason=reason))

    pairs = {m[2]: (m[1], int(m[3])) for a in asg if (m := OUT.fullmatch(a.reason))}  # S: (R, m)
    on = [v for v in op.rotation if by[v].status.value == "active" and by[v].role_id in op.rotation_roles]  # fmt: skip
    for v in on:  # floor first: a patrol never trades its return battery for coverage
        if by[v].battery_pct - _back(by[v], specs[v]) <= FLOOR:
            by[v] = switch_role(by[v], roles["go_home"])
            note(v, "go_home", f"교대 귀환(하한선): {v}")
    for s, (r, m) in pairs.items():
        if by[s].role_id != by[r].role_id:  # relief or patrol left the role: drop the pair
            asg[:] = [a for a in asg if not (a.vehicle_id == r and OUT.fullmatch(a.reason))]
        elif dist_m(by[r].pos, _point(roles[by[r].role_id], m)) <= MEET_M:  # relief on the coast
            by[s] = switch_role(by[s], roles["go_home"])
            note(r, by[r].role_id, f"교대 완료: {r} ← {s}")
            note(s, "go_home", f"교대 귀환: {s}")
        else:  # the patrol keeps patrolling; the relief flies to route point m
            by[r] = by[r].model_copy(update={"waypoint_idx": m})

    def free(after: str | None, role: str) -> str | None:  # first charged idle drone of the pool
        pool = op.rotation_pools.get(role) or op.rotation
        k = pool.index(after) + 1 if after in pool else 0
        order = pool[k:] + pool[:k]
        ok = [w for w in order if by[w].status.value == "ready" and by[w].battery_pct >= 99.9]
        return next((w for w in ok if by[w].role_id not in op.rotation_roles), None)

    busy = set(pairs) | {r for r, _ in pairs.values()}
    for v in (v for v in on if v not in busy and by[v].role_id in op.rotation_roles):
        st, spec = by[v], specs[v]
        alone = sum(by[w].role_id == st.role_id for w in on) == 1 and st.step_id == roles[st.role_id].entry  # fmt: skip
        if alone and (r := free(v, st.role_id)):
            m = max(st.waypoint_idx, 0)
            fly = dist_m(by[r].pos, _point(roles[st.role_id], m)) / specs[r].speed_mps / 60  # fmt: skip
            if relief_due(st, spec, fly):
                by[r] = switch_role(by[r], roles[st.role_id])
                note(r, st.role_id, f"교대 출발: {r} → {v} @{m}")

    def held(p: str) -> bool:
        return any(by[w].role_id == p and by[w].status.value in ("ready", "active") for w in op.rotation)  # fmt: skip

    engaged = any(held(p) for p in op.rotation_roles)  # rotation runs once a patrol is out
    for p in op.rotation_roles:  # a coast nobody holds (a patrol went home at the floor)
        if engaged and not held(p) and not raid_held(p, op, by, asg, roles) and (r := free(None, p)):  # fmt: skip
            by[r] = switch_role(by[r], roles[p])
            note(r, p, f"교대 투입(빈 순찰): {r} → {p}")
    return [by[s.id] for s in states], asg
