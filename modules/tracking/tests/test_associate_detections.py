from contracts.models import Detection, Track
from modules.tracking.actions.associate_detections import associate_detections
from shared.geo import offset_latlon


def track(tid, east):
    lat, lon = offset_latlon(37.5, 127.0, east, 0)
    return Track(id=tid, t_ms=0, lat=lat, lon=lon, alt_m=50, last_seen_ms=0)


def det(did, east):
    lat, lon = offset_latlon(37.5, 127.0, east, 0)
    return Detection(id=did, sensor="radar", t_ms=0, lat=lat, lon=lon, alt_m=50, strength=0.5)


def test_nearest_within_gate_one_to_one():
    tracks = [track("T-a", 0), track("T-b", 100)]
    dets = [det("x", 5), det("y", 95), det("z", 500)]
    assigned, free = associate_detections(tracks, dets, gate_m=60)
    assert assigned["T-a"].id == "x" and assigned["T-b"].id == "y"
    assert [d.id for d in free] == ["z"]


def test_one_detection_not_shared_by_two_tracks():
    assigned, free = associate_detections([track("T-a", 0), track("T-b", 10)], [det("x", 4)])
    assert list(assigned) == ["T-a"] and free == []
