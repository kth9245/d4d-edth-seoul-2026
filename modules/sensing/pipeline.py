"""sensing pipeline: calls actions in order. No logic here."""

from contracts.models import Detection
from modules.sensing.actions.drop_invalid_detections import drop_invalid_detections


def normalize(detections: list[Detection]) -> list[Detection]:
    return drop_invalid_detections(detections)
