"""GW-10 score_targets: 표적마다 sensing score_target을 불러 threat·threat_reasons·rf_detected·threat_accum을 쓴다
종류는 한 번도 스캔되지 않았으면(seen_by가 비고 first_seen_ms가 0) unknown(스캔 판별, 결정 0040). 한 번 식별되면 지금 안 보여도 유지. 무력화된 표적은 그대로 둔다.
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
    ir = [(s.pos, specs[s.id].ir_range_m) for s in states if s.status in LIVE]  # decision 0071
    sound = [(s.pos, specs[s.id].acoustic_range_m) for s in states if s.status in LIVE]
    watch = [(w.pos, w.radius_m) for w in watch_points]
    out = []
    for tg in targets:
        if tg.neutralized_ms is not None:
            out.append(tg)
            continue
        observed = bool(tg.seen_by)
        identified = observed or tg.first_seen_ms != 0  # once scanned, the kind stays known
        r = score_target(
            tg.kind.value if identified else "unknown",
            tg.pos,
            hypot(tg.vel_east_mps, tg.vel_north_mps),
            observed,
            tg.emitting,
            receivers,
            watch,
            tg.threat_accum,
            tick_ms,
            heat=tg.heat,
            noise=tg.noise,
            ir_receivers=ir,
            sound_receivers=sound,
        )
        out.append(tg.model_copy(update={"threat": r.score, "threat_reasons": r.reasons,
                                         "rf_detected": r.rf_detected, "threat_accum": r.accum,
                                         "ir_detected": r.ir_detected,
                                         "sound_detected": r.sound_detected}))  # fmt: skip
    return out
