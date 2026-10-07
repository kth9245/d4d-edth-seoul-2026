from contracts.models import Track
from modules.tracking.actions.delete_stale_tracks import delete_stale_tracks


def test_drops_tracks_not_seen_for_too_long():
    fresh = Track(id="a", t_ms=5000, lat=0, lon=0, alt_m=0, last_seen_ms=3000)
    stale = Track(id="b", t_ms=5000, lat=0, lon=0, alt_m=0, last_seen_ms=1000)
    assert delete_stale_tracks([fresh, stale], t_ms=5000, max_age_ms=3000) == [fresh]
