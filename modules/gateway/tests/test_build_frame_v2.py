import json

from contracts.models import Frame
from modules.gateway.actions.build_frame_v2 import build_frame_v2
from modules.gateway.actions.init_engine import init_engine
from modules.sim import load_scenario_json

ES = init_engine(load_scenario_json("demo/scenarios/baengnyeong_night.json"))
EXAMPLE = json.loads(open("contracts/examples/frame.json", encoding="utf-8").read())


def test_frame_carries_engine_state_and_this_tick_log():
    f = build_frame_v2(ES, ["00:00 작전 시작"])
    assert f.t_ms == ES.t_ms
    assert f.run == ES.run
    assert f.vehicles == ES.states
    assert f.assignments == ES.assignments
    assert (f.targets, f.reports, f.blocks, f.injections) == (
        ES.targets,
        ES.reports,
        ES.blocks,
        ES.injections,
    )
    assert f.metrics == ES.metrics
    assert f.log == ["00:00 작전 시작"]


def test_frame_json_has_same_shape_as_example_frame():
    d = json.loads(build_frame_v2(ES, []).model_dump_json())
    assert set(d) == set(EXAMPLE)
    assert set(d["vehicles"][0]) == set(EXAMPLE["vehicles"][0])
    assert set(d["metrics"]) == set(EXAMPLE["metrics"])


def test_frame_survives_json_round_trip():
    f = build_frame_v2(ES, ["a", "b"])
    assert Frame.model_validate_json(f.model_dump_json()) == f
