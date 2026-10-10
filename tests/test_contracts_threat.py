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


def test_a_new_target_has_no_identification():
    t = Target(id="site_a", kind="unknown", pos=P, vel_east_mps=0, vel_north_mps=0,
               first_seen_ms=0, last_seen_ms=0)  # fmt: skip
    assert (t.ident_state, t.ident_confidence, t.ident_reasons, t.ident_observed_ms) == (
        "undetected", 0, [], 0,
    )  # fmt: skip


def test_a_condition_can_wait_for_the_target_to_be_neutralized():  # decision 0066
    from contracts.models import ConditionKind

    assert ConditionKind("target_neutralized") is ConditionKind.target_neutralized


def test_a_vehicle_remembers_where_it_left_its_patrol_route():  # decision 0066
    from contracts.models import GeoPoint, VehicleState

    st = VehicleState(id="r1", t_ms=0, pos=GeoPoint(lat=37.9, lon=124.7), heading_deg=0,
                      battery_pct=100, status="ready")  # fmt: skip
    assert (st.patrol_step_id, st.patrol_idx) == (None, 0)


def test_a_condition_can_wait_for_a_site_another_vehicle_reported():  # decision 0070
    from contracts.models import ConditionKind

    assert ConditionKind("target_resighted") is ConditionKind.target_resighted


def test_the_sensor_fields_default_to_off():  # decision 0069
    from contracts.models import EnemySpec, GeoPoint, Target, VehicleSpec

    home = GeoPoint(lat=37.9, lon=124.7)
    v = VehicleSpec(id="r1", name="r1", domain="air", speed_mps=15, endurance_min=100,
                    sensor_range_m=800, home=home)  # fmt: skip
    assert (v.ir_range_m, v.acoustic_range_m) == (0, 0)
    e = EnemySpec(id="s", kind="unknown", speed_mps=0, appear_offset_ms=1000, pos=home, role_id="r")
    assert (e.heat, e.noise) == (False, False)
    t = Target(id="s", kind="unknown", pos=home, vel_east_mps=0, vel_north_mps=0,
               first_seen_ms=0, last_seen_ms=0)  # fmt: skip
    assert (t.heat, t.noise, t.ir_detected, t.sound_detected) == (False, False, False, False)
