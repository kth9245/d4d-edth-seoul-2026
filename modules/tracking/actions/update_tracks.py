"""TRK-03 update_tracks: 짝지어진 탐지로 위치·hits 갱신, 속도는 β 평활
SPEC: modules/tracking/SPEC.md#TRK-03
"""

from contracts.models import Detection, Track
from shared.geo import enu_delta_m

BETA = 0.3


def update_tracks(tracks: list[Track], assigned: dict[str, Detection], t_ms: int) -> list[Track]:
    out = []
    for t in tracks:
        d = assigned.get(t.id)
        if d is None:
            out.append(t)
            continue
        dt = max((t_ms - t.last_seen_ms) / 1000, 1e-3)
        east, north = enu_delta_m(t.lat, t.lon, d.lat, d.lon)
        beta = 1.0 if t.hits == 1 else BETA
        out.append(
            t.model_copy(
                update={
                    "lat": d.lat,
                    "lon": d.lon,
                    "alt_m": d.alt_m,
                    "t_ms": t_ms,
                    "last_seen_ms": t_ms,
                    "hits": t.hits + 1,
                    "vel_east_mps": t.vel_east_mps + beta * east / dt,
                    "vel_north_mps": t.vel_north_mps + beta * north / dt,
                }
            )
        )
    return out
