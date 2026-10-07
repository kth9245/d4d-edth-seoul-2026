"""TRK-02 associate_detections: 게이트 안 최근접 탐지를 표적에 1:1로 짝짓기
SPEC: modules/tracking/SPEC.md#TRK-02
"""

from contracts.models import Detection, Track
from shared.geo import distance_m


def associate_detections(
    tracks: list[Track], detections: list[Detection], gate_m: float = 60.0
) -> tuple[dict[str, Detection], list[Detection]]:
    pairs = sorted(
        (distance_m(t.lat, t.lon, d.lat, d.lon), i, j)
        for i, t in enumerate(tracks)
        for j, d in enumerate(detections)
    )
    assigned: dict[str, Detection] = {}
    used: set[int] = set()
    for dist, i, j in pairs:
        if dist > gate_m:
            break
        if tracks[i].id in assigned or j in used:
            continue
        assigned[tracks[i].id] = detections[j]
        used.add(j)
    free = [d for j, d in enumerate(detections) if j not in used]
    return assigned, free
