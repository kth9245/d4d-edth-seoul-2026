"""SIM-08 advance_vehicles: 이번 틱 통과 명령(없으면 active)대로 모든 기체를 1틱 진행, 배터리 소모
기지에서 hold면 배터리가 줄지 않고 ready를 유지한다. 정비 중 recharge_min > 0이면 충전 뒤 ready(결정 0037). 공개 API 이름은 advance.
land는 해상 기체에만 넘긴다(결정 0034).
SPEC: modules/sim/SPEC.md#SIM-08
"""

from collections.abc import Sequence

from contracts.models import (
    CommandKind,
    Domain,
    PassedCommand,
    Polygon,
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


def _recharge(st: VehicleState, spec: VehicleSpec, dt_ms: int) -> VehicleState:
    pct = st.battery_pct + 100 / spec.recharge_min * dt_ms / 60000
    if pct < 100:
        return st.model_copy(update={"battery_pct": pct})
    done = {"battery_pct": 100, "status": VehicleStatus.ready, "play_id": None, "step_id": None}
    return st.model_copy(update={**done, "active": None, "waypoint_idx": 0})


def advance_vehicles(
    states: list[VehicleState],
    specs: dict[str, VehicleSpec],
    passed: list[PassedCommand],
    dt_ms: int,
    targets: list[Target],
    land: Sequence[Polygon] = (),
) -> list[VehicleState]:
    by_v = {pc.command.vehicle_id: pc for pc in passed}
    out = []
    for st in states:
        spec, pc = specs[st.id], by_v.get(st.id) or st.active
        st = st.model_copy(update={"t_ms": st.t_ms + dt_ms})
        if st.status == VehicleStatus.maintenance and spec.recharge_min > 0:  # swap (0037)
            out.append(_recharge(st, spec, dt_ms))
            continue
        if pc is None or st.status in (VehicleStatus.lost, VehicleStatus.maintenance):
            out.append(st)
            continue
        st = st.model_copy(update={"active": pc})
        kind = pc.command.kind
        if kind == K.hold and dist_m(st.pos, spec.home) < 1:  # on the ground at base
            out.append(st)
            continue
        sea = land if spec.domain == Domain.sea else ()  # only boats go round islands (0034)
        if kind in (K.orbit, K.keep_distance, K.strike):  # strike: fly onto the target (0033)
            st = orbit_or_keep(st, spec, pc, targets, dt_ms, sea)
        elif kind == K.follow_route:
            st = follow_route(st, spec, pc, dt_ms, sea)
        elif kind in (K.move, K.return_home, K.hold):
            st = move_straight(st, spec, pc, dt_ms, sea)
        drain = 100 / spec.endurance_min * dt_ms / 60000
        upd: dict = {"battery_pct": max(st.battery_pct - drain, 0)}
        if st.status == VehicleStatus.ready:
            upd["status"] = VehicleStatus.active
        out.append(st.model_copy(update=upd))
    return out
