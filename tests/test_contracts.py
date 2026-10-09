import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from contracts.models import (
    ALL_MODELS,
    Action,
    Detection,
    Frame,
    GeoPoint,
    Polygon,
    Scenario,
    ScenarioEvent,
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


def test_six_scene_frames_exist():
    assert len(list((EXAMPLES / "frames").glob("*.json"))) == 6


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
