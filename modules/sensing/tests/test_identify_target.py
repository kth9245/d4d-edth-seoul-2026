from modules.sensing.actions.identify_target import identify_target

TICK = 200


def test_no_evidence_is_undetected():
    assert identify_target(False, 0, None, 0, TICK) == ("undetected", 0, [], 0)


def test_rf_alone_is_a_source_not_yet_confirmed():
    r = identify_target(True, 0, None, 0, TICK)
    assert (r.state, r.confidence, r.reasons) == ("rf_only", 25, ["rf_emission"])


def test_rf_plus_a_fresh_scan_is_identifying_not_yet_identified():
    r = identify_target(True, 1, 0, 0, TICK)
    assert (r.state, r.confidence, r.reasons, r.observed_ms) == (
        "identifying", 65, ["rf_emission", "scan"], 200)  # fmt: skip


def test_five_seconds_of_unbroken_observation_reaches_the_threshold():
    r = identify_target(True, 1, 0, 4800, TICK)  # 4800 + 200 = 5000 ms -> +5
    assert (r.state, r.confidence, r.observed_ms) == ("identified", 70, 5000)
    assert r.reasons == ["rf_emission", "scan", "sustained"]


def test_a_second_observer_adds_fifteen():
    r = identify_target(True, 2, 0, 0, TICK)
    assert (r.state, r.confidence) == ("identified", 80)
    assert "multi_observer" in r.reasons


def test_a_silent_site_needs_two_observers():
    one = identify_target(False, 1, 0, 19800, TICK)  # scan 40 + sustained 20
    assert (one.state, one.confidence) == ("identifying", 60)
    two = identify_target(False, 2, 0, 19800, TICK)
    assert (two.state, two.confidence) == ("identified", 75)


def test_losing_it_resets_the_duration_and_fades_the_scan():
    r = identify_target(True, 0, 30_000, 6000, TICK)  # 30 s since last seen
    assert (r.state, r.confidence, r.observed_ms) == ("identifying", 35, 0)  # rf 25 + scan 10


def test_after_forty_seconds_only_the_rf_clue_is_left():
    r = identify_target(True, 0, 40_000, 0, TICK)
    assert (r.state, r.confidence, r.reasons) == ("rf_only", 25, ["rf_emission"])


def test_a_gap_shorter_than_a_second_does_not_reset_the_sustained_time():
    r = identify_target(True, 0, 200, 5000, TICK)  # lost one tick right at the threshold
    assert (r.state, r.confidence, r.observed_ms) == ("identified", 70, 5000)


def test_a_gap_of_a_second_or_more_resets_it():
    r = identify_target(True, 0, 3000, 5000, TICK)
    assert (r.state, r.confidence, r.observed_ms) == ("identifying", 62, 0)  # rf 25 + scan 37
