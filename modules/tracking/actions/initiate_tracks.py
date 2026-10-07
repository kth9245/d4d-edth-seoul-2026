"""TRK-04 initiate_tracks: 짝 없는 탐지마다 새 표적 생성
SPEC: modules/tracking/SPEC.md#TRK-04
"""

from contracts.models import Detection, Track


def initiate_tracks(detections: list[Detection], t_ms: int) -> list[Track]:
    return [
        Track(
            id=f"T-{d.id.split('@')[0]}",
            t_ms=t_ms,
            lat=d.lat,
            lon=d.lon,
            alt_m=d.alt_m,
            hits=1,
            last_seen_ms=t_ms,
        )
        for d in detections
    ]
