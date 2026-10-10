"""SIM-06 follow_route: 경로점을 차례로 돌고 끝나면 처음으로
land(해상 기체만 받음)가 있으면 섬을 돌아가고, 육지 위 경로점은 해안 바다 점으로 본다(결정 0034).
SPEC: modules/sim/SPEC.md#SIM-06
"""

from collections.abc import Sequence

from contracts.models import GeoPoint, PassedCommand, Polygon, VehicleSpec, VehicleState
from modules.sim.actions.sea_aim import sea_aim
from shared.geo import dist_m, move_toward
from shared.land import to_sea


def follow_route(
    st: VehicleState,
    spec: VehicleSpec,
    pc: PassedCommand,
    dt_ms: int,
    land: Sequence[Polygon] = (),
) -> VehicleState:
    route = [GeoPoint(**q) for q in pc.command.params["route"]]
    i = max(st.waypoint_idx, 0) % len(route)
    wp = to_sea(route[i], land)
    pos = move_toward(st.pos, sea_aim(st.pos, wp, land), spec.speed_mps * dt_ms / 1000)
    upd: dict = {"pos": pos}
    if dist_m(pos, wp) < 1:
        upd["waypoint_idx"] = i + 1
    return st.model_copy(update=upd)
