"""SNS-04 identify_target: 증거(RF·스캔·다중 관측·관측 지속)로 식별 상태와 신뢰도(0.01 단위)를 낸다
위협 점수(score_target)와 별개다: 이쪽은 "이것이 적 거점인가, 얼마나 확신하는가". 수치는 모두 임의 초안(설계 7.1절, 결정 0063).
SPEC: modules/sensing/SPEC.md#SNS-04
"""

from typing import NamedTuple

RF_PTS, SCAN_PTS, MULTI_PTS, SUSTAINED_MAX_PTS = 25, 40, 15, 20
SCAN_DECAY_PER_S = 1  # the scan evidence fades one point per second after the target was lost
SUSTAINED_PER_S = 1  # unbroken observation: one point per second, up to SUSTAINED_MAX_PTS
IR_PTS, SOUND_PTS = (
    10,
    10,
)  # decision 0071: a heat or noise clue from an infrared or acoustic receiver
IDENTIFIED_AT = 70
GRACE_MS = 1000  # a gap shorter than this keeps the sustained time, so one missed tick does not flip the state


class Ident(NamedTuple):
    state: str
    confidence: int
    reasons: list[str]
    observed_ms: int


def identify_target(
    rf_detected: bool,
    seen_count: int,
    age_ms: int | None,
    observed_ms: int,
    tick_ms: int,
    *,
    ir_detected: bool = False,
    sound_detected: bool = False,
) -> Ident:
    seen = seen_count > 0
    brief_gap = not seen and age_ms is not None and age_ms < GRACE_MS
    observed = (
        observed_ms + tick_ms if seen else (observed_ms if brief_gap else 0)
    )  # a longer gap resets it
    never_scanned = age_ms is None and not seen
    lost_s = 0 if seen else (age_ms or 0) // 1000
    scan = 0 if never_scanned else max(0, SCAN_PTS - lost_s * SCAN_DECAY_PER_S)
    rf = RF_PTS if rf_detected else 0
    ir = IR_PTS if ir_detected else 0
    sound = SOUND_PTS if sound_detected else 0
    multi = MULTI_PTS if seen_count >= 2 else 0
    sustained = min(SUSTAINED_MAX_PTS, observed // 1000 * SUSTAINED_PER_S)
    confidence = min(100, rf + ir + sound + scan + multi + sustained)
    parts = [
        ("rf_emission", rf),
        ("ir_signature", ir),
        ("sound", sound),
        ("scan", scan),
        ("multi_observer", multi),
        ("sustained", sustained),
    ]
    reasons = [name for name, pts in parts if pts]
    if scan == 0:
        state = "rf_only" if (rf or ir or sound) else "undetected"  # a clue without a scan
    else:
        state = "identified" if confidence >= IDENTIFIED_AT else "identifying"
    return Ident(state, confidence, reasons, observed)
