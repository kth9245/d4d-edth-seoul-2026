"""TRK-01 predict_tracks: 등속 모델로 t_ms 시점 위치 예측
SPEC: modules/tracking/SPEC.md#TRK-01
"""

from contracts.models import Track
from shared.geo import offset_latlon


def predict_tracks(tracks: list[Track], t_ms: int) -> list[Track]:
    out = []
    for t in tracks:
        dt = (t_ms - t.t_ms) / 1000
        lat, lon = offset_latlon(t.lat, t.lon, t.vel_east_mps * dt, t.vel_north_mps * dt)
        out.append(t.model_copy(update={"lat": lat, "lon": lon, "t_ms": t_ms}))
    return out
