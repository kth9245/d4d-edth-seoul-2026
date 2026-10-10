"""RT-12 relieve_hover: 표적 위에서 감시(호버링) 중인 교대 드론의 교대(사용자 지시)
감시 드론 S가 교대 기준 배터리에 닿으면 같은 짝의 충전된 대기 드론 R이 같은 표적 감시로 출발하고,
R이 S에게서 500 m 안에 오면 S가 귀환한다. 감시가 끊기지 않는다.
SPEC: modules/runtime/SPEC.md#RT-12
"""

import re

from contracts.models import Assignment, Operation, Play, VehicleSpec, VehicleState
from modules.runtime.actions.fleet_choices import WATCH_PLAY, watching
from modules.runtime.actions.rotate_patrols import MEET_M, START, _back
from modules.runtime.actions.switch_play import switch_play
from shared.geo import dist_m

OUT = re.compile(r"감시 교대 출발: (\S+) → (\S+)")


def relieve_hover(
    states: list[VehicleState],
    specs: dict[str, VehicleSpec],
    op: Operation,
    plays: dict[str, Play],
    assignments: list[Assignment],
    t_ms: int,
) -> tuple[list[VehicleState], list[Assignment]]:
    if not op.rotation:
        return states, assignments
    by, asg = {s.id: s for s in states}, list(assignments)

    def note(vid: str, play: str, reason: str) -> None:
        asg[:] = [a for a in asg if a.vehicle_id != vid]
        asg.append(Assignment(vehicle_id=vid, play_id=play, since_ms=t_ms, reason=reason))

    pairs = {m[2]: m[1] for a in asg if (m := OUT.fullmatch(a.reason))}  # S: R
    for s, r in pairs.items():
        if not watching(by[s], plays) or by[r].play_id != WATCH_PLAY:  # gone: drop the pair
            asg[:] = [a for a in asg if not (a.vehicle_id == r and OUT.fullmatch(a.reason))]
        elif dist_m(by[r].pos, by[s].pos) <= MEET_M:
            by[s] = switch_play(by[s], plays["go_home"])
            note(r, WATCH_PLAY, f"감시 교대 완료: {r} ← {s}")
            note(s, "go_home", f"감시 교대 귀환: {s}")
    busy = set(pairs) | set(pairs.values())
    for v in (v for v in op.rotation if v in by):
        st = by[v]
        if v in busy or st.status.value != "active" or not watching(st, plays):
            continue
        if st.battery_pct - 2 * _back(st, specs[v]) > START:
            continue
        pool = next((p for p in op.rotation_pools.values() if v in p), op.rotation)
        idle = (w for w in pool if w != v and w in by and by[w].status.value == "ready")
        idle = (w for w in idle if by[w].battery_pct >= 99.9 and by[w].play_id not in (*op.rotation_plays, WATCH_PLAY))  # fmt: skip
        if r := next(idle, None):
            by[r] = switch_play(by[r], plays[WATCH_PLAY]).model_copy(
                update={"target_id": st.target_id}
            )
            note(r, WATCH_PLAY, f"감시 교대 출발: {r} → {v}")
    return [by[s.id] for s in states], asg
