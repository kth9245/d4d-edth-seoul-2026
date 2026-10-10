"""SIM-07 orbit_or_keep: 표적 주위 선회(orbit) 또는 거리 유지(keep_distance)
멀리 있으면 먼저 날아간다(옛 스파이크는 원 위로 순간 이동해 이어받기 공백이 안 생겼다).
land(해상 기체만 받음)가 있고 표적까지 직선이 섬을 지나면 sea_aim 점으로 먼저 돌아간다(결정 0034).
SPEC: modules/sim/SPEC.md#SIM-07
"""

import math
from collections.abc import Sequence

from contracts.models import (
    CommandKind,
    GeoPoint,
    PassedCommand,
    Polygon,
    Target,
    VehicleSpec,
    VehicleState,
)
from modules.sim.actions.sea_aim import sea_aim
from shared.geo import dist_m, move_toward, offset_latlon
from shared.land import blocked


def orbit_or_keep(
    st: VehicleState,
    spec: VehicleSpec,
    pc: PassedCommand,
    targets: list[Target],
    dt_ms: int,
    land: Sequence[Polygon] = (),
) -> VehicleState:
    cmd = pc.command
    tg = next((t for t in targets if t.id == cmd.params.get("target_id")), None)
    if tg is None:
        return st
    r, step_m = float(cmd.params.get("distance_m", 150)), spec.speed_mps * dt_ms / 1000
    d = dist_m(st.pos, tg.pos)
    if cmd.kind == CommandKind.orbit and d <= r * 1.5:
        ang = math.radians(st.heading_deg) + step_m / r
        lat, lon = offset_latlon(tg.pos.lat, tg.pos.lon, r * math.sin(ang), r * math.cos(ang))
        pos = GeoPoint(lat=lat, lon=lon, alt_m=st.pos.alt_m)
        return st.model_copy(update={"heading_deg": math.degrees(ang) % 360, "pos": pos})
    if blocked(st.pos, tg.pos, land):  # round the island first (decision 0034)
        aim = sea_aim(st.pos, tg.pos, land)
        return st.model_copy(update={"pos": move_toward(st.pos, aim, step_m)})
    return st.model_copy(update={"pos": move_toward(st.pos, tg.pos, min(step_m, max(d - r, 0)))})
