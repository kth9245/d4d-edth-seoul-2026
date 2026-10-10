"""RT-10 rotate_patrols: 해안 순찰 교대(결정 0037, 초소 근무 교대)
순찰 기체가 교대 기준 배터리에 닿으면 충전된 대기 기체가 출발해 경로점 m에서 만나 넘겨받고 나간 기체는 귀환.
하한선(귀환 뒤 30%)이 교대보다 먼저. op.rotation·rotation_plays가 비면 아무것도 하지 않는다.
SPEC: modules/runtime/SPEC.md#RT-10
"""

import re

from contracts.models import Assignment, Operation, Play, VehicleSpec, VehicleState
from modules.runtime.actions.switch_play import switch_play
from shared.geo import dist_m

FLOOR, START, MEET_M = 30.0, 35.0, 500.0  # landing floor %, relief start % (floor + 5), handover m
OUT = re.compile(r"교대 출발: (\S+) → (\S+) @(\d+)")


def _back(st: VehicleState, spec: VehicleSpec) -> float:  # battery % to fly home from here
    return 100 / spec.endurance_min * dist_m(st.pos, spec.home) / spec.speed_mps / 60


def rotate_patrols(
    states: list[VehicleState],
    specs: dict[str, VehicleSpec],
    op: Operation,
    plays: dict[str, Play],
    assignments: list[Assignment],
    t_ms: int,
) -> tuple[list[VehicleState], list[Assignment]]:
    if not op.rotation or not op.rotation_plays:
        return states, assignments
    by, asg = {s.id: s for s in states}, list(assignments)

    def note(vid: str, play: str, reason: str) -> None:
        asg[:] = [a for a in asg if a.vehicle_id != vid]
        asg.append(Assignment(vehicle_id=vid, play_id=play, since_ms=t_ms, reason=reason))

    pairs = {m[2]: (m[1], int(m[3])) for a in asg if (m := OUT.fullmatch(a.reason))}  # S: (R, m)
    on = [v for v in op.rotation if by[v].status.value == "active"]
    on = [v for v in on if by[v].play_id in op.rotation_plays]
    for v in on:  # floor first: a patrol never trades its return battery for coverage
        if by[v].battery_pct - _back(by[v], specs[v]) <= FLOOR:
            by[v] = switch_play(by[v], plays["go_home"])
            note(v, "go_home", f"교대 귀환(하한선): {v}")
    for s, (r, m) in pairs.items():
        if by[s].play_id != by[r].play_id:  # relief or patrol left the play: drop the pair
            asg[:] = [a for a in asg if not (a.vehicle_id == r and OUT.fullmatch(a.reason))]
        elif dist_m(by[s].pos, by[r].pos) <= MEET_M:
            by[s] = switch_play(by[s], plays["go_home"])
            note(r, by[r].play_id, f"교대 완료: {r} ← {s}")
            note(s, "go_home", f"교대 귀환: {s}")
        else:  # both hold waypoint m until they meet (the patrol waits there)
            by[s] = by[s].model_copy(update={"waypoint_idx": m})
            by[r] = by[r].model_copy(update={"waypoint_idx": m})

    def free(after: str | None) -> str | None:  # first charged, idle rotation drone after `after`
        k = op.rotation.index(after) + 1 if after else 0
        order = op.rotation[k:] + op.rotation[:k]
        ok = [w for w in order if by[w].status.value == "ready" and by[w].battery_pct >= 99.9]
        return next((w for w in ok if by[w].play_id not in op.rotation_plays), None)

    busy = set(pairs) | {r for r, _ in pairs.values()}
    for v in (v for v in on if v not in busy and by[v].play_id in op.rotation_plays):
        st, spec = by[v], specs[v]
        alone = sum(by[w].play_id == st.play_id for w in on) == 1
        if alone and st.battery_pct - 2 * _back(st, spec) <= START and (r := free(v)):
            by[r] = switch_play(by[r], plays[st.play_id])
            note(r, st.play_id, f"교대 출발: {r} → {v} @{max(st.waypoint_idx, 0)}")

    def held(p: str) -> bool:
        return any(
            by[w].play_id == p and by[w].status.value in ("ready", "active") for w in op.rotation
        )

    engaged = any(held(p) for p in op.rotation_plays)  # rotation runs once a patrol is out
    for p in op.rotation_plays:  # a coast nobody holds (a patrol went home at the floor)
        if engaged and not held(p) and (r := free(None)):
            by[r] = switch_play(by[r], plays[p])
            note(r, p, f"교대 투입(빈 순찰): {r} → {p}")
    return [by[s.id] for s in states], asg
