"""ASM-02 score_threat: 보호 지점까지 거리·접근 여부·분류로 위협도와 근거 계산
SPEC: modules/assess/SPEC.md#ASM-02
"""

from contracts.models import ObjectClass, Track
from shared.geo import distance_m, enu_delta_m

CLASS_WEIGHT = {
    ObjectClass.DRONE: 1.0,
    ObjectClass.UNKNOWN: 0.6,
    ObjectClass.BALLOON: 0.4,
    ObjectClass.BIRD: 0.1,
}


def score_threat(
    track: Track, object_class: ObjectClass, protected_lat: float, protected_lon: float
) -> tuple[float, str]:
    dist = distance_m(track.lat, track.lon, protected_lat, protected_lon)
    east, north = enu_delta_m(track.lat, track.lon, protected_lat, protected_lon)
    closing = (track.vel_east_mps * east + track.vel_north_mps * north) / max(dist, 1.0)
    proximity = max(0.0, 1.0 - dist / 3000)
    approach = 1.0 if closing > 1 else 0.5
    score = round(min(1.0, CLASS_WEIGHT[object_class] * (0.3 + 0.7 * proximity) * approach), 2)
    reason = f"{object_class.value}, 보호지점 {dist:.0f} m, 접근속도 {closing:.1f} m/s"
    return score, reason
