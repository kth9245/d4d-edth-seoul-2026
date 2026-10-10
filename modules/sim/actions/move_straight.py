"""SIM-05 move_straight: move·return_home·hold 명령으로 1틱 직선 이동
SPEC: modules/sim/SPEC.md#SIM-05
"""

from contracts.models import (
    CommandKind,
    GeoPoint,
    PassedCommand,
    VehicleSpec,
    VehicleState,
    VehicleStatus,
)
from shared.geo import dist_m, move_toward


def move_straight(
    st: VehicleState, spec: VehicleSpec, pc: PassedCommand, dt_ms: int
) -> VehicleState:
    cmd = pc.command
    if cmd.kind == CommandKind.hold:
        return st
    home = cmd.kind == CommandKind.return_home
    tgt = spec.home if home else GeoPoint(**cmd.params["target"])
    pos = move_toward(st.pos, tgt, spec.speed_mps * dt_ms / 1000)
    upd: dict = {"pos": pos}
    if dist_m(pos, tgt) < 1:
        upd["waypoint_idx"] = -1  # arrived: the `arrived` exit condition reads this
        if home:
            upd["status"] = VehicleStatus.maintenance
    return st.model_copy(update=upd)
