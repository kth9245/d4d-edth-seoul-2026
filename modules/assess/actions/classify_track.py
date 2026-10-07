"""ASM-01 classify_track: 속도·고도 규칙으로 drone/balloon/bird/unknown 분류
SPEC: modules/assess/SPEC.md#ASM-01
"""

import math

from contracts.models import ObjectClass, Track


def classify_track(track: Track) -> ObjectClass:
    if track.hits < 3:
        return ObjectClass.UNKNOWN
    speed = math.hypot(track.vel_east_mps, track.vel_north_mps)
    if speed < 4 and track.alt_m > 300:
        return ObjectClass.BALLOON
    if speed < 12 and track.alt_m < 60:
        return ObjectClass.BIRD
    return ObjectClass.DRONE
