"""Legacy T1-3 Engine (smoke.py uses it until Part1-14)."""

from pathlib import Path

from modules.gateway import Engine
from modules.sim import load_scenario

ROOT = Path(__file__).resolve().parents[3]
SCENARIO = str(ROOT / "demo/scenarios/seoul_mixed.yaml")


def test_engine_produces_tracks_and_assessments():
    eng = Engine(load_scenario(SCENARIO), seed=1)
    frames = [eng.step() for _ in range(40)]
    last = frames[-1]
    assert len(last.tracks) >= 3
    assert {a.track_id for a in last.assessments} == {t.id for t in last.tracks}
    assert frames[1].t_ms - frames[0].t_ms == 500


def test_engine_done_at_end():
    eng = Engine(load_scenario(SCENARIO))
    for _ in range(240):
        eng.step()
    assert eng.done
