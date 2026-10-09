"""SIM-08 advance_vehicles: 이번 틱 통과 명령(없으면 active)대로 모든 기체를 1틱 진행, 배터리 소모
기지에서 hold면 배터리가 줄지 않고 ready를 유지한다. 공개 API 이름은 advance.
SPEC: modules/sim/SPEC.md#SIM-08
"""

from contracts.models import (
    CommandKind,
    PassedCommand,
    Target,
    VehicleSpec,
    VehicleState,
    VehicleStatus,
)
from modules.sim.actions.follow_route import follow_route
from modules.sim.actions.move_straight import move_straight
from modules.sim.actions.orbit_or_keep import orbit_or_keep
from shared.geo import dist_m

K = CommandKind


def advance_vehicles(
    states: list[VehicleState],
    specs: dict[str, VehicleSpec],
    passed: list[PassedCommand],
    dt_ms: int,
    targets: list[Target],
) -> list[VehicleState]:
    by_v = {pc.command.vehicle_id: pc for pc in passed}
    out = []
    for st in states:
        spec, pc = specs[st.id], by_v.get(st.id) or st.active
        st = st.model_copy(update={"t_ms": st.t_ms + dt_ms})
        if pc is None or st.status in (VehicleStatus.lost, VehicleStatus.maintenance):
            out.append(st)
            continue
        st = st.model_copy(update={"active": pc})
        kind = pc.command.kind
        if kind == K.hold and dist_m(st.pos, spec.home) < 1:  # on the ground at base
            out.append(st)
            continue
        if kind in (K.orbit, K.keep_distance):
            st = orbit_or_keep(st, spec, pc, targets, dt_ms)
        elif kind == K.follow_route:
            st = follow_route(st, spec, pc, dt_ms)
        elif kind in (K.move, K.return_home, K.hold):
            st = move_straight(st, spec, pc, dt_ms)
        drain = 100 / spec.endurance_min * dt_ms / 60000
        upd: dict = {"battery_pct": max(st.battery_pct - drain, 0)}
        if st.status == VehicleStatus.ready:
            upd["status"] = VehicleStatus.active
        out.append(st.model_copy(update=upd))
    return out
