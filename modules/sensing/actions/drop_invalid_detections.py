"""SNS-01 drop_invalid_detections: 위경도 범위 밖·음수 고도 탐지 제거
SPEC: modules/sensing/SPEC.md#SNS-01
"""

from contracts.models import Detection


def drop_invalid_detections(detections: list[Detection]) -> list[Detection]:
    return [d for d in detections if -90 <= d.lat <= 90 and -180 <= d.lon <= 180 and d.alt_m >= 0]
