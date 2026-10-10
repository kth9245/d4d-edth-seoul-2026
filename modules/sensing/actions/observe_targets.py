"""SNS-02 observe_targets: 센서 범위 안 표적의 seen_by·last_seen_ms(와 그때 위치·속도, 결정 0047) 갱신. 공개 API 이름은 observe.
SPEC: modules/sensing/SPEC.md#SNS-02
"""

from contracts.models import Target, VehicleSpec, VehicleState, VehicleStatus
from shared.geo import dist_m

LIVE = (VehicleStatus.ready, VehicleStatus.active)


def observe_targets(
    states: list[VehicleState], specs: dict[str, VehicleSpec], targets: list[Target], t_ms: int
) -> list[Target]:
    out = []
    for tg in targets:
        seen = [
            s.id
            for s in states
            if s.status in LIVE and dist_m(s.pos, tg.pos) <= specs[s.id].sensor_range_m
        ]
        upd: dict = {"seen_by": seen}
        if seen:  # where and how fast it was last seen: the board draws a lost target there (decision 0047)
            upd |= {"last_seen_ms": t_ms, "first_seen_ms": tg.first_seen_ms or t_ms,
                    "last_seen_pos": tg.pos, "last_seen_vel_east_mps": tg.vel_east_mps,
                    "last_seen_vel_north_mps": tg.vel_north_mps}  # fmt: skip
        out.append(tg.model_copy(update=upd))
    return out
