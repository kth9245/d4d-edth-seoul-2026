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


def test_a_condition_can_wait_for_a_site_another_vehicle_reported():  # decision 0068
    from contracts.models import ConditionKind

    assert ConditionKind("target_resighted") is ConditionKind.target_resighted
