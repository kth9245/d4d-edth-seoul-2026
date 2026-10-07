from contracts.models import Detection, Track
from modules.tracking.actions.initiate_tracks import initiate_tracks
from modules.tracking.pipeline import update


def test_new_track_per_detection():
    d = Detection(
        id="drone-a@1500", sensor="radar", t_ms=1500, lat=37.5, lon=127.0, alt_m=90, strength=0.5
    )
    (t,) = initiate_tracks([d], t_ms=1500)
    assert t.id == "T-drone-a" and t.hits == 1 and t.last_seen_ms == 1500
    assert (t.lat, t.lon, t.alt_m) == (37.5, 127.0, 90)


def test_existing_id_gets_suffix():
    d = Detection(
        id="drone-a@1500", sensor="radar", t_ms=1500, lat=37.5, lon=127.0, alt_m=90, strength=0.5
    )
    (t,) = initiate_tracks([d], t_ms=1500, existing_ids={"T-drone-a"})
    assert t.id == "T-drone-a-2"


def test_same_object_multiple_detections_in_call():
    d1 = Detection(
        id="drone-a@1500", sensor="radar", t_ms=1500, lat=37.5, lon=127.0, alt_m=90, strength=0.5
    )
    d2 = Detection(
        id="drone-a@1501", sensor="radar", t_ms=1501, lat=37.6, lon=127.1, alt_m=91, strength=0.6
    )
    tracks = initiate_tracks([d1, d2], t_ms=1500)
    assert len(tracks) == 2
    ids = {t.id for t in tracks}
    assert len(ids) == 2 and ids == {"T-drone-a", "T-drone-a-2"}


def test_reappearing_track_outside_gate():
    existing_track = Track(
        id="T-drone-a", t_ms=0, lat=37.5, lon=127.0, alt_m=100, hits=3, last_seen_ms=0
    )
    detection_far = Detection(
        id="drone-a@2000", sensor="radar", t_ms=2000, lat=37.0, lon=127.0, alt_m=95, strength=0.5
    )
    result = update([existing_track], [detection_far], t_ms=2000)
    ids = [t.id for t in result]
    assert len(set(ids)) == len(ids), f"Duplicate IDs found: {ids}"
