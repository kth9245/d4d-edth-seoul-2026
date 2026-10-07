"""TRK-04 initiate_tracks: 짝 없는 탐지마다 새 표적, 기존·동시 생성 id와 겹치면 -2,-3 접미사
SPEC: modules/tracking/SPEC.md#TRK-04
"""

from contracts.models import Detection, Track


def initiate_tracks(
    detections: list[Detection], t_ms: int, existing_ids: set[str] | None = None
) -> list[Track]:
    existing_ids = existing_ids or set()
    used = set(existing_ids)
    out = []
    for d in detections:
        base_id = f"T-{d.id.split('@')[0]}"
        track_id = base_id
        counter = 2
        while track_id in used:
            track_id = f"{base_id}-{counter}"
            counter += 1
        used.add(track_id)
        out.append(
            Track(
                id=track_id,
                t_ms=t_ms,
                lat=d.lat,
                lon=d.lon,
                alt_m=d.alt_m,
                hits=1,
                last_seen_ms=t_ms,
            )
        )
    return out
