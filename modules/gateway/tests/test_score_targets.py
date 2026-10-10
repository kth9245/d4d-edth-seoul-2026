from contracts.models import GeoPoint, Target, VehicleSpec, VehicleState, WatchPoint
from modules.gateway.actions.score_targets import score_targets

HOME = GeoPoint(lat=37.978, lon=124.70)
NEAR = GeoPoint(lat=37.9825, lon=124.70)  # ~500 m north of HOME
WATCH = [WatchPoint(id="landing", name="landing", pos=HOME, radius_m=2000)]
SPECS = {"d2": VehicleSpec(id="d2", name="d2", domain="air", speed_mps=15, endurance_min=50,
                           sensor_range_m=800, capabilities=[], home=HOME, rf_range_m=2000)}  # fmt: skip
STATES = [VehicleState(id="d2", t_ms=0, pos=HOME, heading_deg=0, battery_pct=100, status="active")]


def fast(**kw) -> Target:
    base = dict(id="fast1", kind="fast_boat", pos=NEAR, vel_east_mps=6.3, vel_north_mps=0,
                first_seen_ms=0, last_seen_ms=0, seen_by=["d2"], emitting=True)  # fmt: skip
    return Target(**(base | kw))


def run(t: Target) -> Target:
    return score_targets(STATES, SPECS, [t], WATCH, 200)[0]


def test_observed_emitting_fast_boat_in_range_scores_100_and_starts_accumulating():
    t = run(fast())
    assert (t.threat, t.rf_detected, t.threat_accum) == (100, True, 100 * 200)
    assert t.threat_reasons == ["kind_fast_boat", "inside_watch_radius", "rf_emission", "speed"]


def test_accum_continues_between_ticks_and_resets_when_the_scan_is_lost():
    t = run(run(fast()))
    assert t.threat_accum == 2 * 100 * 200
    lost = run(t.model_copy(update={"seen_by": []}))
    assert lost.threat_accum == 0


def test_kind_is_unknown_until_a_vehicle_scans_it():
    t = run(fast(seen_by=[], emitting=False))
    assert t.threat_reasons[0] == "kind_unknown" and t.threat == 60  # 0.30 + inside 0.30
    seen = run(fast(emitting=False))
    assert seen.threat_reasons[0] == "kind_fast_boat"


def test_neutralized_target_is_left_as_it_was():
    t = fast(neutralized_ms=5)
    assert run(t) == t


def test_a_target_scanned_once_keeps_its_kind_when_nobody_sees_it_now():  # decision 0040: "once caught"
    lost = fast(seen_by=[], first_seen_ms=5000, emitting=True)
    t = run(lost)
    assert t.threat_reasons[0] == "kind_fast_boat"  # still known, not 'kind_unknown'
    assert "speed" not in t.threat_reasons and t.threat_accum == 0  # these need a scan right now
    assert t.threat == 100  # fast_boat 0.40 + inside the radius 0.30 + RF 0.30, no speed


def test_infrared_and_sound_are_heard_only_by_live_vehicles_in_range():  # decision 0069
    spec = SPECS["d2"].model_copy(
        update={"ir_range_m": 800.0, "acoustic_range_m": 600.0}
    )  # the target is 500.4 m away: a 500 m ear would just miss it
    t = fast(kind="unknown", seen_by=[], emitting=False, heat=True, noise=True)
    out = score_targets(STATES, {"d2": spec}, [t], WATCH, 200)[0]
    assert (out.ir_detected, out.sound_detected) == (True, True)
    assert "ir_signature" in out.threat_reasons and "sound" in out.threat_reasons
    gone = [STATES[0].model_copy(update={"status": "returning"})]
    out2 = score_targets(gone, {"d2": spec}, [t], WATCH, 200)[0]
    assert (out2.ir_detected, out2.sound_detected) == (
        False,
        False,
    )  # a returning vehicle is no receiver
    out3 = score_targets(STATES, SPECS, [t], WATCH, 200)[0]  # SPECS: both ranges 0
    assert (out3.ir_detected, out3.sound_detected) == (False, False)


def test_a_vehicle_out_of_range_hears_nothing_and_a_neutralized_target_keeps_its_scores():
    spec = SPECS["d2"].model_copy(update={"ir_range_m": 100.0})  # the target is ~500 m away
    t = fast(kind="unknown", emitting=False, heat=True)
    assert not score_targets(STATES, {"d2": spec}, [t], WATCH, 200)[0].ir_detected
    spec = SPECS["d2"].model_copy(update={"ir_range_m": 800.0})
    dead = fast(heat=True, neutralized_ms=5, threat=33)
    out = score_targets(STATES, {"d2": spec}, [dead], WATCH, 200)[0]
    assert (out.threat, out.ir_detected) == (33, False)
