"""SIM-03 emit_detections: 실제 위치에 잡음을 더한 레이더 탐지 생성 (재현 가능)
SPEC: modules/sim/SPEC.md#SIM-03
"""

import random

from contracts.models import Detection, SensorType
from modules.sim.types import TruthPoint
from shared.geo import offset_latlon

NOISE_M = 3.0


def emit_detections(truth: list[TruthPoint], t_ms: int, seed: int) -> list[Detection]:
    rng = random.Random(f"{seed}:{t_ms}")
    out = []
    for p in truth:
        lat, lon = offset_latlon(p.lat, p.lon, rng.gauss(0, NOISE_M), rng.gauss(0, NOISE_M))
        out.append(
            Detection(
                id=f"{p.object_id}@{t_ms}",
                sensor=SensorType.RADAR,
                t_ms=t_ms,
                lat=lat,
                lon=lon,
                alt_m=max(0.0, p.alt_m + rng.gauss(0, 2)),
                strength=round(rng.uniform(0.4, 1.0), 3),
            )
        )
    return out
