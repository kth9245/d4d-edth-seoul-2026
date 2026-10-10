from contracts.models import GeoPoint, Target
from modules.gateway.actions.identify_targets import identify_targets

POS = GeoPoint(lat=37.982, lon=124.722)


def site(**kw) -> Target:
    base = dict(id="site_a", kind="unknown", pos=POS, vel_east_mps=0, vel_north_mps=0,
                first_seen_ms=0, last_seen_ms=0, seen_by=[], rf_detected=True)  # fmt: skip
    return Target(**(base | kw))


def test_an_rf_only_site_is_not_confirmed_yet():
    t = identify_targets([site()], 10_000, 200)[0]
    assert (t.ident_state, t.ident_confidence, t.ident_reasons) == ("rf_only", 25, ["rf_emission"])


def test_a_scanned_site_climbs_tick_by_tick_and_keeps_its_observed_time():
    t = site(seen_by=["d1"], first_seen_ms=9_000, last_seen_ms=10_000)
    t1 = identify_targets([t], 10_000, 200)[0]
    t2 = identify_targets([t1], 10_200, 200)[0]
    assert (t1.ident_confidence, t1.ident_observed_ms) == (65, 200)
    assert t2.ident_observed_ms == 400


def test_a_lost_site_fades_from_its_last_seen_time():
    t = site(seen_by=[], first_seen_ms=9_000, last_seen_ms=10_000, ident_observed_ms=6000)
    r = identify_targets([t], 40_000, 200)[0]  # 30 s later
    assert (r.ident_state, r.ident_confidence, r.ident_observed_ms) == ("identifying", 35, 0)


def test_other_kinds_and_neutralized_sites_are_left_alone():
    boat = site(id="b1", kind="boat", seen_by=["d1"], first_seen_ms=1)
    dead = site(id="site_b", seen_by=["d1"], first_seen_ms=1, neutralized_ms=5)
    out = identify_targets([boat, dead], 10_000, 200)
    assert out == [boat, dead]


def test_the_detected_clues_reach_the_identification():  # decision 0069
    t = site(seen_by=["d1"], first_seen_ms=9_000, last_seen_ms=10_000, rf_detected=False,
             ir_detected=True, sound_detected=True)  # fmt: skip
    r = identify_targets([t], 10_000, 200)[0]
    assert (
        r.ident_reasons[:2] == ["ir_signature", "sound"] and r.ident_confidence == 60
    )  # scan 40 + 10 + 10
