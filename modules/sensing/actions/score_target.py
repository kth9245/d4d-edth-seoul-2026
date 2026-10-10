"""SNS-03 score_target: 표적 위협 점수(종류·반경·RF·속도, 정수 0.01)와 기준치 이상 누적(결정 0039)
SPEC: modules/sensing/SPEC.md#SNS-03
"""

from typing import NamedTuple

from contracts.models import GeoPoint
from shared.geo import dist_m

BASE = {"fast_boat": 40, "boat": 20, "person": 30, "unknown": 30}
INSIDE, NEAR, RF, SPEED_CAP, SPEED_PER_MPS, CAP, THRESHOLD = 30, 15, 30, 30, 5, 100, 40
CARD_ACCUM = 450 * 1000  # threat_accum that lets a contact card go up: score 1.0 for 4.5 s (0042)


class ThreatScore(NamedTuple):
    score: int  # 0.01 단위 정수
    reasons: list[str]
    rf_detected: bool
    accum: int  # 점수(0.01 단위) × ms. 카드 기준은 450 × 1000


def score_target(
    kind: str,
    pos: GeoPoint,
    speed_mps: float,
    observed: bool,
    emitting: bool,
    receivers: list[tuple[GeoPoint, float]],
    watch_points: list[tuple[GeoPoint, float]],
    accum: int,
    tick_ms: int,
) -> ThreatScore:
    score, reasons = BASE[kind], [f"kind_{kind}"]
    rf = emitting and any(r > 0 and dist_m(p, pos) <= r for p, r in receivers)
    gaps = [dist_m(c, pos) / radius for c, radius in watch_points]
    if any(g <= 1 for g in gaps):
        score, reasons = score + INSIDE, reasons + ["inside_watch_radius"]
    elif any(g <= 3 for g in gaps):  # decisions 0041, 0042: approaching boats are not left out
        score, reasons = score + NEAR, reasons + ["near_watch_radius"]
    if rf:
        score, reasons = score + RF, reasons + ["rf_emission"]
    speed = min(SPEED_CAP, int(speed_mps * SPEED_PER_MPS)) if observed else 0
    if speed:
        score, reasons = score + speed, reasons + ["speed"]
    score = min(CAP, score)
    grown = accum + score * tick_ms if observed and score >= THRESHOLD else 0
    return ThreatScore(score, reasons, rf, grown)
