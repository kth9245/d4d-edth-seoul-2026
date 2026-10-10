"""GW-10 score_targets: 표적마다 sensing score_target을 불러 threat·threat_reasons·rf_detected·threat_accum을 쓴다
종류는 seen_by가 비어 있으면 unknown(스캔 판별, 결정 0040). 무력화된 표적은 그대로 둔다.
SPEC: modules/gateway/SPEC.md#GW-10
"""

from math import hypot

from contracts.models import Target, VehicleSpec, VehicleState, VehicleStatus, WatchPoint
from modules.sensing import score_target

LIVE = (VehicleStatus.ready, VehicleStatus.active)


def score_targets(
    states: list[VehicleState],
    specs: dict[str, VehicleSpec],
    targets: list[Target],
    watch_points: list[WatchPoint],
    tick_ms: int,
) -> list[Target]:
    receivers = [(s.pos, specs[s.id].rf_range_m) for s in states if s.status in LIVE]
    watch = [(w.pos, w.radius_m) for w in watch_points]
    out = []
    for tg in targets:
        if tg.neutralized_ms is not None:
            out.append(tg)
            continue
        observed = bool(tg.seen_by)
        r = score_target(
            tg.kind.value if observed else "unknown",
            tg.pos,
            hypot(tg.vel_east_mps, tg.vel_north_mps),
            observed,
            tg.emitting,
            receivers,
            watch,
            tg.threat_accum,
            tick_ms,
        )
        out.append(tg.model_copy(update={"threat": r.score, "threat_reasons": r.reasons,
                                         "rf_detected": r.rf_detected, "threat_accum": r.accum}))  # fmt: skip
    return out
