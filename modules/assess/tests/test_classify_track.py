from contracts.models import ObjectClass, Track
from modules.assess.actions.classify_track import classify_track


def t(speed_e: float, alt: float, hits: int = 5) -> Track:
    return Track(
        id="x",
        t_ms=0,
        lat=0,
        lon=0,
        alt_m=alt,
        vel_east_mps=speed_e,
        vel_north_mps=0,
        hits=hits,
        last_seen_ms=0,
    )


def test_rules():
    assert classify_track(t(2, 900)) == ObjectClass.BALLOON
    assert classify_track(t(9, 40)) == ObjectClass.BIRD
    assert classify_track(t(15, 120)) == ObjectClass.DRONE
    assert classify_track(t(15, 120, hits=1)) == ObjectClass.UNKNOWN
