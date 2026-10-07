from contracts.models import ObjectClass, Track
from modules.assess.actions.score_threat import score_threat
from shared.geo import offset_latlon

P = (37.5665, 126.978)


def track_at(east: float, vel_east: float) -> Track:
    lat, lon = offset_latlon(*P, east, 0)
    return Track(
        id="x",
        t_ms=0,
        lat=lat,
        lon=lon,
        alt_m=100,
        vel_east_mps=vel_east,
        vel_north_mps=0,
        hits=5,
        last_seen_ms=0,
    )


def test_close_approaching_drone_is_high():
    score, reason = score_threat(track_at(-300, 15), ObjectClass.DRONE, *P)
    assert score >= 0.8 and "m" in reason


def test_receding_drone_is_lower_than_approaching():
    near, _ = score_threat(track_at(-300, 15), ObjectClass.DRONE, *P)
    away, _ = score_threat(track_at(-300, -15), ObjectClass.DRONE, *P)
    assert away < near


def test_bird_is_low_and_score_in_range():
    score, _ = score_threat(track_at(-50, 10), ObjectClass.BIRD, *P)
    assert 0.0 <= score <= 0.3
