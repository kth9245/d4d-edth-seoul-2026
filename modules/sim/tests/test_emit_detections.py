from contracts.models import Detection
from modules.sim.actions.emit_detections import emit_detections
from modules.sim.types import TruthPoint
from shared.geo import distance_m

TRUTH = [TruthPoint(object_id="d1", kind="drone", lat=37.5665, lon=126.978, alt_m=100)]


def test_one_detection_per_object_near_truth():
    dets = emit_detections(TRUTH, t_ms=5000, seed=1)
    assert len(dets) == 1 and isinstance(dets[0], Detection)
    assert dets[0].id == "d1@5000" and dets[0].sensor == "radar" and dets[0].t_ms == 5000
    assert distance_m(37.5665, 126.978, dets[0].lat, dets[0].lon) < 30


def test_reproducible_with_same_seed():
    assert emit_detections(TRUTH, 5000, 1) == emit_detections(TRUTH, 5000, 1)
    assert emit_detections(TRUTH, 5000, 1) != emit_detections(TRUTH, 5000, 2)
