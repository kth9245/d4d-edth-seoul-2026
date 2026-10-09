"""The two-layer spike runs the whole 3-minute script on the demo scenario (decisions 0015-0018)."""

import importlib.util
from pathlib import Path

import pytest

from contracts.models import Frame

SPIKE = Path(__file__).resolve().parent.parent / "knowledge/spikes/rolecall_engine_proto"
MIN = 60_000


@pytest.fixture(scope="module")
def result():
    spec = importlib.util.spec_from_file_location("engine_proto", SPIKE / "engine_proto.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.run(minutes=35)


def _at(result, offset_ms):
    frames = result["frames"]
    return next((f for f in frames if f.t_ms - result["start_ms"] >= offset_ms), frames[-1])


def _plays(frame):
    return {v.id: v.play_id for v in frame.vehicles}


def test_frames_are_contract_frames(result):
    f = result["frames"][-1]
    assert Frame.model_validate(f.model_dump()) == f


def test_report_card_comes_from_sensing_after_the_boat_appears(result):
    reps = [r for r in result["frames"][-1].reports if r.kind == "target_detected"]
    assert reps and reps[0].vehicle_id == "d1"
    assert reps[0].t_ms - result["start_ms"] >= 11 * MIN


def test_one_decision_switches_four_vehicles(result):
    rep = next(r for r in result["frames"][-1].reports if r.kind == "target_detected")
    after = _at(result, rep.resolved_ms - result["start_ms"] + 5000)
    assert {k: _plays(after)[k] for k in ("d1", "usv", "ugv", "d2")} == {
        "d1": "watch", "usv": "approach", "ugv": "landing", "d2": "patrol_b",
    }  # fmt: skip


def test_reserve_takes_over_the_watch_step(result):
    f = _at(result, 20 * MIN)
    d1, d3 = (next(v for v in f.vehicles if v.id == i) for i in ("d1", "d3"))
    assert d1.status in ("returning", "maintenance")
    assert (d3.play_id, d3.step_id) == ("watch", "watch")
    assert any(a.reason == "예비 투입: d1 대신" for a in f.assignments)
    assert result["frames"][-1].metrics.vehicle_gap_ms > 0


def test_switch_then_operator_picks_the_fast_boat(result):
    f = _at(result, 25 * MIN)
    d2 = next(v for v in f.vehicles if v.id == "d2")
    assert (d2.play_id, d2.target_id) == ("track_fast", "fast1")
    assert any(r.kind == "target_select" and r.resolved_ms for r in f.reports)


def test_only_the_direct_control_commands_are_blocked(result):
    blocks = result["frames"][-1].blocks
    assert [b.reason for b in blocks] == ["outside_zone", "battery_insufficient"]
    assert blocks[0].alternative is not None
