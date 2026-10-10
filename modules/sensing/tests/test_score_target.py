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


NEAR_3KM = GeoPoint(
    lat=38.005, lon=124.70
)  # ~3 km north: outside 2 km, inside 4 km (decision 0041)
FAR_5KM = GeoPoint(lat=38.023, lon=124.70)  # ~5 km north


def test_boat_within_twice_the_radius_gets_the_near_step_of_15():
    r = score(pos=NEAR_3KM)
    assert r.score == 35 and r.reasons == ["kind_boat", "near_watch_radius"]


def test_boat_beyond_twice_the_radius_gets_no_watch_point_score():
    r = score(pos=FAR_5KM)
    assert r.score == 20 and r.reasons == ["kind_boat"]


def test_approaching_boat_outside_the_radius_still_reaches_the_threshold():
    r = score(pos=NEAR_3KM, speed=1.5)  # 20 + 15 + 7 = 42 >= 40
    assert r.score == 42 and r.accum == 42 * 200
