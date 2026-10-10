from contracts.models import GeoPoint
from modules.sensing.actions.score_target import score_target

WATCH = [(GeoPoint(lat=37.978, lon=124.70), 2000.0)]
INSIDE, FAR = GeoPoint(lat=37.978, lon=124.70), GeoPoint(lat=37.9645, lon=124.737)


def score(kind="boat", pos=INSIDE, speed=0.0, observed=True, emitting=False, rx=(), accum=0):
    return score_target(kind, pos, speed, observed, emitting, list(rx), WATCH, accum, 200)


def test_moving_boat_inside_radius_scores_55():
    r = score(speed=1.0)
    assert r.score == 55 and r.reasons == ["kind_boat", "inside_watch_radius", "speed"]


def test_stopped_boat_inside_radius_scores_50():
    assert score().score == 50


def test_fast_boat_with_everything_is_capped_at_100():
    r = score("fast_boat", speed=6.3, emitting=True, rx=[(INSIDE, 2000.0)])
    assert r.score == 100 and r.rf_detected


def test_silent_target_or_receiver_out_of_range_gives_no_rf():
    assert not score("fast_boat", emitting=False, rx=[(INSIDE, 2000.0)]).rf_detected
    assert not score("fast_boat", pos=FAR, emitting=True, rx=[(INSIDE, 2000.0)]).rf_detected
    assert not score("fast_boat", emitting=True, rx=[(INSIDE, 0.0)]).rf_detected


def test_speed_counts_only_while_observed():
    assert score("fast_boat", speed=6.3, observed=False).score == 70


def test_accum_grows_by_score_times_tick_from_threshold():
    r = score(accum=1000)  # boat inside radius = 50
    assert r.accum == 1000 + 50 * 200


def test_accum_resets_below_threshold_or_when_unobserved():
    assert score("boat", pos=FAR, accum=5000).accum == 0  # 20
    assert score(observed=False, accum=5000).accum == 0


NEAR_5KM = GeoPoint(lat=38.023, lon=124.70)  # ~5 km north: 2.5x the radius (decision 0043: 3x)
FAR_7KM = GeoPoint(lat=38.041, lon=124.70)  # ~7 km north: beyond 3x


def test_boat_within_three_times_the_radius_gets_the_near_step_of_15():
    r = score(pos=NEAR_5KM)
    assert r.score == 35 and r.reasons == ["kind_boat", "near_watch_radius"]


def test_boat_beyond_three_times_the_radius_gets_no_watch_point_score():
    r = score(pos=FAR_7KM)
    assert r.score == 20 and r.reasons == ["kind_boat"]


def test_approaching_boat_outside_the_radius_still_reaches_the_threshold():
    r = score(pos=NEAR_5KM, speed=1.5)  # 20 + 15 + 7 = 42 >= 40
    assert r.score == 42 and r.accum == 42 * 200


def sig(**kw):  # an unknown silent site observed in the watch radius, plus the new signals; no RF
    return score_target("unknown", INSIDE, 0.0, True, False, [], WATCH, 0, 200, **kw)


def test_heat_in_infrared_range_adds_ten_with_its_reason_in_order():  # decision 0071
    plain = sig()
    r = sig(heat=True, ir_receivers=[(INSIDE, 800.0)])
    assert (r.score, r.ir_detected) == (plain.score + 10, True)
    assert r.reasons == [*plain.reasons, "ir_signature"]


def test_noise_in_acoustic_range_adds_ten_and_the_reasons_keep_their_order():
    r = sig(
        heat=True, noise=True, ir_receivers=[(INSIDE, 800.0)], sound_receivers=[(INSIDE, 500.0)]
    )
    assert r.reasons[-2:] == ["ir_signature", "sound"] and (r.ir_detected, r.sound_detected) == (
        True,
        True,
    )
    moving = score_target("unknown", INSIDE, 1.0, True, True, [(INSIDE, 2000.0)], WATCH, 0, 200,
                          heat=True, noise=True, ir_receivers=[(INSIDE, 800.0)],
                          sound_receivers=[(INSIDE, 500.0)])  # fmt: skip
    order = [moving.reasons.index(x) for x in ("rf_emission", "ir_signature", "sound", "speed")]
    assert order == sorted(order)


def test_the_range_edge_counts_and_one_metre_less_does_not():
    from shared.geo import dist_m

    far = GeoPoint(lat=INSIDE.lat + 0.004, lon=INSIDE.lon)
    d = dist_m(INSIDE, far)
    assert sig(heat=True, ir_receivers=[(far, d)]).ir_detected  # exactly at the edge
    assert not sig(heat=True, ir_receivers=[(far, d - 1)]).ir_detected
    assert sig(noise=True, sound_receivers=[(far, d)]).sound_detected
    assert not sig(noise=True, sound_receivers=[(far, d - 1)]).sound_detected


def test_no_signal_no_receiver_or_range_zero_gives_nothing():
    base = sig()
    assert sig(heat=False, ir_receivers=[(INSIDE, 800.0)]) == base
    assert sig(heat=True) == base  # nobody listens
    assert sig(heat=True, ir_receivers=[(INSIDE, 0.0)]) == base  # range 0 = cannot
    assert sig(noise=True, sound_receivers=[(INSIDE, 0.0)]) == base


def test_every_signal_together_is_still_capped_at_100():
    r = score_target("fast_boat", INSIDE, 6.3, True, True, [(INSIDE, 2000.0)], WATCH, 0, 200,
                     heat=True, noise=True, ir_receivers=[(INSIDE, 800.0)],
                     sound_receivers=[(INSIDE, 500.0)])  # fmt: skip
    assert r.score == 100


def test_calling_it_the_old_way_still_works_and_reports_no_new_signals():
    r = score()
    assert (r.ir_detected, r.sound_detected) == (False, False)
