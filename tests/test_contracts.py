import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from contracts.models import (
    ALL_MODELS,
    Action,
    Detection,
    EnemySpec,
    Frame,
    GeoPoint,
    Polygon,
    Scenario,
    ScenarioEvent,
    Target,
    TickOutcome,
    VehicleState,
)

EXAMPLES = Path(__file__).resolve().parent.parent / "contracts" / "examples"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", sorted(ALL_MODELS))
def test_example_matches_model(name):
    ALL_MODELS[name].model_validate(_load(EXAMPLES / f"{name}.json"))


@pytest.mark.parametrize("path", sorted((EXAMPLES / "frames").glob("*.json")), ids=lambda p: p.stem)
def test_scene_frames_are_frames(path):
    Frame.model_validate(_load(path))


def test_eight_scene_frames_exist():
    assert len(list((EXAMPLES / "frames").glob("*.json"))) == 8


def test_example_scenario_is_the_demo_scenario():  # decision 0035: the demo JSON is the source
    demo = EXAMPLES.parent.parent / "demo" / "scenarios" / "baengnyeong_night.json"
    assert Scenario.model_validate(_load(EXAMPLES / "scenario.json")) == Scenario.model_validate(
        _load(demo)
    )


def test_examples_share_one_world():
    scenario = Scenario.model_validate(_load(EXAMPLES / "scenario.json"))
    vehicle_ids = {v.id for v in scenario.vehicles}
    play_ids = {p.id for p in scenario.plays}
    assert set(scenario.operation.vehicle_ids) == vehicle_ids
    assert set(scenario.operation.assign) <= vehicle_ids
    assert set(scenario.operation.assign.values()) <= play_ids
    for path in [EXAMPLES / "frame.json", *sorted((EXAMPLES / "frames").glob("*.json"))]:
        frame = Frame.model_validate(_load(path))
        assert {v.id for v in frame.vehicles} == vehicle_ids, path.name
        assert {v.play_id for v in frame.vehicles if v.play_id} <= play_ids, path.name


def test_polygon_needs_three_points():
    with pytest.raises(ValidationError):
        Polygon(points=[GeoPoint(lat=37.9, lon=124.6), GeoPoint(lat=38.0, lon=124.7)])


def test_scenario_event_uses_offset():
    ev = ScenarioEvent.model_validate({"offset_ms": 660000, "kind": "spawn_target", "params": {}})
    assert ev.offset_ms == 660000
    with pytest.raises(ValidationError):
        ScenarioEvent.model_validate({"t_ms": 660000, "kind": "spawn_target", "params": {}})


def test_action_params_hold_points_and_routes():
    a = Action(kind="patrol_route", params={"route": [{"lat": 37.98, "lon": 124.66}]})
    b = Action(kind="watch_target", params={"target": "nearest", "distance_m": 150})
    assert a.params["route"][0]["lat"] == 37.98 and b.params["target"] == "nearest"


def test_vehicle_state_keeps_active_command():
    data = _load(EXAMPLES / "vehicle_state.json")
    st = VehicleState.model_validate(data)
    assert st.active is not None
    assert VehicleState.model_validate(st.model_dump()) == st


def test_frame_has_run_state_and_no_mode():
    fields = Frame.model_fields
    assert "run" in fields and "mode" not in fields


def test_strength_out_of_range_rejected():
    with pytest.raises(ValidationError):
        Detection(id="d", sensor="radar", t_ms=0, lat=37.0, lon=127.0, alt_m=10, strength=1.5)


def test_unknown_sensor_rejected():
    with pytest.raises(ValidationError):
        Detection(id="d", sensor="sonar", t_ms=0, lat=37.0, lon=127.0, alt_m=10, strength=0.5)


def test_tick_outcome_carries_all_reports_for_open_report_counting():
    assert "reports" in TickOutcome.model_fields


def test_strike_and_enemy_enum_values():
    from contracts.models import ActionKind, CommandKind, ReportKind

    assert ActionKind("strike_target") and CommandKind("strike")
    assert ReportKind("target_neutralized")


def test_strike_and_enemy_fields_default_to_empty():
    g = GeoPoint(lat=37.9, lon=124.7)
    st = VehicleState(id="d1", t_ms=0, pos=g, heading_deg=0, battery_pct=90, status="ready")
    assert st.decision_id is None
    tg = Target(id="b", kind="boat", pos=g, vel_east_mps=0, vel_north_mps=0,
                first_seen_ms=0, last_seen_ms=0)  # fmt: skip
    assert (tg.neutralized_ms, tg.play_id, tg.step_id, tg.waypoint_idx, tg.step_since_ms) == (
        None, None, None, 0, None,
    )  # fmt: skip
    sc = Scenario.model_validate(_load(EXAMPLES / "scenario.json"))  # the demo world (0035)
    assert {e.id for e in sc.enemies} == {"boat1", "boat2", "boat3", "fast1"}  # 0036


def test_target_reported_by_names_the_vehicle_that_raised_its_card():  # decision 0036
    g = GeoPoint(lat=37.9, lon=124.7)
    tg = Target(id="b", kind="boat", pos=g, vel_east_mps=0, vel_north_mps=0,
                first_seen_ms=0, last_seen_ms=0)  # fmt: skip
    assert tg.reported_by is None
    assert tg.model_copy(update={"reported_by": "d1"}).reported_by == "d1"
    assert Target.model_validate({**tg.model_dump(), "reported_by": "d2"}).reported_by == "d2"


def test_enemy_appears_at_a_point_or_from_another_enemy():
    e = EnemySpec(id="fast1", kind="fast_boat", speed_mps=6.3, appear_offset_ms=1_380_000,
                  from_enemy="boat1", play_id="enemy_fast1")  # fmt: skip
    assert e.pos is None and e.from_enemy == "boat1"


def test_scenario_land_is_island_polygons_and_defaults_to_none():
    sc = Scenario.model_validate(_load(EXAMPLES / "scenario.json"))
    island = Polygon(points=[GeoPoint(lat=37.94, lon=124.68), GeoPoint(lat=37.94, lon=124.72),
                             GeoPoint(lat=37.97, lon=124.70)])  # fmt: skip
    data = {k: v for k, v in sc.model_dump().items() if k != "land"}
    assert Scenario.model_validate(data).land == []
    assert Scenario.model_validate({**data, "land": [island.model_dump()]}).land == [island]


def test_rotation_fields_default_to_no_rotation():
    from contracts.models import Operation, VehicleSpec

    op = json.loads((EXAMPLES / "operation.json").read_text(encoding="utf-8"))
    spec = json.loads((EXAMPLES / "vehicle_spec.json").read_text(encoding="utf-8"))
    for k in ("rotation", "rotation_plays", "rotation_pools"):
        op.pop(k, None)
    spec.pop("recharge_min", None)
    got = Operation.model_validate(op), VehicleSpec.model_validate(spec)
    assert (got[0].rotation, got[0].rotation_plays, got[1].recharge_min) == ([], [], 0)
    assert got[0].rotation_pools == {}


def test_ontology_fields_default_to_none_and_the_demo_has_the_hierarchy():  # decision 0038
    from contracts.models import ObjectGraph, Ontology, VehicleSpec

    raw = _load(EXAMPLES / "vehicle_spec.json")
    spec = VehicleSpec.model_validate(
        {k: v for k, v in raw.items() if k not in ("kind", "kind_path", "capabilities")}
    )
    assert (spec.kind, spec.kind_path, spec.capabilities) == (None, [], [])
    sc = Scenario.model_validate(_load(EXAMPLES / "scenario.json"))
    assert isinstance(sc.ontology, Ontology)
    assert {k.id: k.is_a for k in sc.ontology.kinds}["armed_drone"] == "air_vehicle"
    assert {v.id: v.kind for v in sc.vehicles} == {
        "d1": "recon_drone", "d2": "armed_drone", "d3": "recon_drone", "d4": "recon_drone",
        "usv": "armed_usv", "ugv": "ground_robot",
    }  # fmt: skip
    g = ObjectGraph.model_validate(_load(EXAMPLES / "object_graph.json"))
    assert g.focus and g.nodes and g.links


def test_scenario_routes_default_empty_and_at_time_condition():  # decisions 0044, 0045
    from contracts.models import Condition, RouteDef

    sc = Scenario.model_validate(_load(EXAMPLES / "scenario.json"))
    assert isinstance(sc.routes, list)
    r = RouteDef(id="sq", name="사각형", offsets=[{"north_m": 300, "east_m": 0}])
    assert r.points == [] and r.offsets[0].north_m == 300
    assert Condition(kind="at_time", params={"offset_ms": 60_000}).kind.value == "at_time"
