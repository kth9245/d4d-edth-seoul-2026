from contracts.models import Detection
from modules.tracking.actions.initiate_tracks import initiate_tracks


def test_new_track_per_detection():
    d = Detection(
        id="drone-a@1500", sensor="radar", t_ms=1500, lat=37.5, lon=127.0, alt_m=90, strength=0.5
    )
    (t,) = initiate_tracks([d], t_ms=1500)
    assert t.id == "T-drone-a" and t.hits == 1 and t.last_seen_ms == 1500
    assert (t.lat, t.lon, t.alt_m) == (37.5, 127.0, 90)
