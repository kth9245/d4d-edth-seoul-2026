from contracts.models import Detection
from modules.sensing.actions.drop_invalid_detections import drop_invalid_detections


def det(**kw) -> Detection:
    base = dict(id="d", sensor="radar", t_ms=0, lat=37.5, lon=127.0, alt_m=50, strength=0.5)
    return Detection(**(base | kw))


def test_keeps_valid_and_drops_invalid():
    good = det()
    out = drop_invalid_detections([good, det(lat=95), det(lon=-200), det(alt_m=-1)])
    assert out == [good]
