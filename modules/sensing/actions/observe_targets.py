"""SNS-02 observe_targets: 센서 범위 안 표적의 seen_by·last_seen_ms 갱신. 공개 API 이름은 observe.
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
        if seen:
            upd |= {"last_seen_ms": t_ms, "first_seen_ms": tg.first_seen_ms or t_ms}
        out.append(tg.model_copy(update=upd))
    return out
