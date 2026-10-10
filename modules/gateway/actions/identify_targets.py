"""GW-12 identify_targets: unknown 종류 표적마다 sensing identify_target을 불러 ident_* 필드를 쓴다(2단계, 결정 0063)
다른 종류와 무력화된 표적은 그대로 둬서 야간·24시간 작전의 프레임이 바뀌지 않는다.
마지막으로 본 뒤 시간은 last_seen_ms로 계산하고, 한 번도 스캔된 적 없으면(first_seen_ms == 0) None.
SPEC: modules/gateway/SPEC.md#GW-12
"""

from contracts.models import Target
from modules.sensing import identify_target


def identify_targets(targets: list[Target], t_ms: int, tick_ms: int) -> list[Target]:
    out = []
    for tg in targets:
        if tg.kind.value != "unknown" or tg.neutralized_ms is not None:
            out.append(tg)
            continue
        scanned = bool(tg.seen_by) or tg.first_seen_ms != 0
        age = None if not scanned else max(0, t_ms - tg.last_seen_ms)
        r = identify_target(
            tg.rf_detected,
            len(tg.seen_by),
            age,
            tg.ident_observed_ms,
            tick_ms,
            ir_detected=tg.ir_detected,  # decision 0069
            sound_detected=tg.sound_detected,
        )
        out.append(tg.model_copy(update={"ident_state": r.state, "ident_confidence": r.confidence,
                                         "ident_reasons": r.reasons,
                                         "ident_observed_ms": r.observed_ms}))  # fmt: skip
    return out
