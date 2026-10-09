"""SIM-06 follow_route: 경로점을 차례로 돌고 끝나면 처음으로
SPEC: modules/sim/SPEC.md#SIM-06
"""

from contracts.models import GeoPoint, PassedCommand, VehicleSpec, VehicleState
from shared.geo import dist_m, move_toward


def follow_route(
    st: VehicleState, spec: VehicleSpec, pc: PassedCommand, dt_ms: int
) -> VehicleState:
    route = [GeoPoint(**q) for q in pc.command.params["route"]]
    i = max(st.waypoint_idx, 0) % len(route)
    pos = move_toward(st.pos, route[i], spec.speed_mps * dt_ms / 1000)
    upd: dict = {"pos": pos}
    if dist_m(pos, route[i]) < 1:
        upd["waypoint_idx"] = i + 1
    return st.model_copy(update=upd)
