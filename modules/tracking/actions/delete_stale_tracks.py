"""TRK-05 delete_stale_tracks: 마지막 탐지 후 max_age_ms 지난 표적 삭제
SPEC: modules/tracking/SPEC.md#TRK-05
"""

from contracts.models import Track


def delete_stale_tracks(tracks: list[Track], t_ms: int, max_age_ms: int = 3000) -> list[Track]:
    return [t for t in tracks if t_ms - t.last_seen_ms <= max_age_ms]
