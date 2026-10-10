"""SIM-05 move_straight: move·return_home·hold 명령으로 1틱 직선 이동
land(해상 기체만 받음)가 있으면 섬을 돌아간다: sea_aim 점을 향해 가고, 육지 위 목표는 해안 바다 점(결정 0034).
SPEC: modules/sim/SPEC.md#SIM-05
"""

from collections.abc import Sequence

from contracts.models import (
    CommandKind,
    GeoPoint,
    PassedCommand,
    Polygon,
    VehicleSpec,
    VehicleState,
    VehicleStatus,
)
from modules.sim.actions.sea_aim import sea_aim
from shared.geo import dist_m, move_toward
from shared.land import to_sea


def move_straight(
    st: VehicleState,
    spec: VehicleSpec,
    pc: PassedCommand,
    dt_ms: int,
    land: Sequence[Polygon] = (),
) -> VehicleState:
    cmd = pc.command
    if cmd.kind == CommandKind.hold:
        return st
    home = cmd.kind == CommandKind.return_home
    tgt = to_sea(spec.home if home else GeoPoint(**cmd.params["target"]), land)
    pos = move_toward(st.pos, sea_aim(st.pos, tgt, land), spec.speed_mps * dt_ms / 1000)
    upd: dict = {"pos": pos}
    if dist_m(pos, tgt) < 1:
        upd["waypoint_idx"] = -1  # arrived: the `arrived` exit condition reads this
        if home:
            upd["status"] = VehicleStatus.maintenance
    return st.model_copy(update=upd)
