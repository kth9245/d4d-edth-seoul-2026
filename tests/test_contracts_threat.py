from contracts.models import EnemySpec, GeoPoint, Scenario, Target, VehicleSpec, WatchPoint
from modules.sim import load_scenario_json

P = GeoPoint(lat=37.98, lon=124.7)


def test_new_threat_fields_default_off():
    t = Target(id="b", kind="boat", pos=P, vel_east_mps=0, vel_north_mps=0,
               first_seen_ms=0, last_seen_ms=0)  # fmt: skip
    assert (t.emitting, t.rf_detected, t.threat, t.threat_reasons, t.threat_accum) == (
        False, False, 0, [], 0,
    )  # fmt: skip


def test_watch_point_and_rf_fields_exist():
    w = WatchPoint(id="landing", name="상륙 예상 지점", pos=P, radius_m=2000)
    assert w.radius_m == 2000
    assert VehicleSpec.model_fields["rf_range_m"].default == 0
    assert EnemySpec.model_fields["emit_start_offset_ms"].default is None
    assert Scenario.model_fields["watch_points"].default == []


def test_existing_demo_scenario_still_loads():
    assert load_scenario_json("demo/scenarios/baengnyeong_night.json").id == "baengnyeong_night"
