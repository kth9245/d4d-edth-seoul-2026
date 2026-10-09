from contracts.models import LegacyFrame, Track
from modules.gateway.actions.build_frame import build_frame


def test_build_frame():
    t = Track(id="T-a", t_ms=1, lat=0, lon=0, alt_m=0, last_seen_ms=1)
    f = build_frame(1, [t], [], [])
    assert isinstance(f, LegacyFrame) and f.t_ms == 1 and f.tracks == [t]
