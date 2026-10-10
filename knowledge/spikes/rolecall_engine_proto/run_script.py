"""Run the 3-minute script on the port files (port/modules/...) with a scripted operator.

The port tree mirrors the repo's modules/ so each file can be copied as is. Run it with the port
first on the import path (tests/test_spike_script.py does this in a subprocess):
  PYTHONPATH=knowledge/spikes/rolecall_engine_proto/port:. uv run python \
      knowledge/spikes/rolecall_engine_proto/run_script.py [--out frames.json]
"""

import argparse
import json
import sys
import time
from pathlib import Path

from modules.gateway.engine import init_engine, tick

from contracts.models import Decision, DirectControl, GeoPoint, Injection, TickInputs
from modules.sim import load_scenario_json

ROOT = Path(__file__).resolve().parents[3]
# Frozen copy of the demo scenario from before enemies (decision 0032, Part1-19): the port engine
# only knows the spawn_target/split_target events.
SCENARIO = Path(__file__).resolve().parent / "baengnyeong_night.json"
MIN = 60_000


class Operator:
    """Stands in for the screen: answers cards, requests and approves the switch, drives d2."""

    def __init__(self, start: int):
        self.start, self.n = start, {"dec": 0, "dir": 0}

    def _id(self, kind: str) -> str:
        self.n[kind] += 1
        return f"{kind}-{self.n[kind]}"

    def inputs(self, es, t: int) -> TickInputs:
        decisions = []
        for r in es.reports:  # a card is answered 20 s after it appears (target pick: 10 s)
            wait = 10_000 if r.kind == "target_select" else 20_000
            if r.choices and not r.resolved_ms and t == r.t_ms + wait:
                ids = [c.id for c in r.choices]
                pick = "fast1" if "fast1" in ids else ids[0]
                decisions.append(
                    Decision(id=self._id("dec"), t_ms=t, report_id=r.id, choice_id=pick)
                )
        off, inj, direct = t - self.start, [], []
        if off == 23 * MIN + 20_000:
            inj.append(Injection(id="inj-1", t_ms=t, label="고속 보트 추적: d2",
                                 play_by_vehicle={"d2": "track_fast"}))  # fmt: skip
        if off == 24 * MIN:
            inj.append(
                next(i for i in es.injections if i.id == "inj-1").model_copy(
                    update={"status": "approved"}
                )
            )
        goals = {
            31 * MIN: GeoPoint(lat=38.05, lon=124.70),
            31 * MIN + 30_000: GeoPoint(lat=37.905, lon=124.565),
        }
        if off == 31 * MIN + 5_000 and es.blocks and es.blocks[-1].alternative:  # "대안 지점으로"
            goals[off] = GeoPoint(**es.blocks[-1].alternative.params["target"])
        if off in goals:
            direct.append(
                DirectControl(id=self._id("dir"), vehicle_id="d2", target=goals[off], t_ms=t)
            )
        return TickInputs(decisions=decisions, direct=direct, injections=inj)


def run(minutes: int = 35, path: Path = SCENARIO, every: int = 25):
    sc = load_scenario_json(path)
    es, op = init_engine(sc), Operator(sc.operation.started_ms)
    frames, log, fr = [], [], None
    for i in range(minutes * MIN // sc.tick_ms):
        es, fr = tick(es, op.inputs(es, es.t_ms + sc.tick_ms))
        log += fr.log
        if i % every == 0:
            frames.append(fr)
    frames.append(fr)
    return {"start_ms": sc.operation.started_ms, "frames": frames, "log": log}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="write start_ms + kept frames as JSON here")
    a = ap.parse_args()
    t0 = time.perf_counter()
    out = run()
    if a.out:
        data = {
            "start_ms": out["start_ms"],
            "frames": [f.model_dump(mode="json") for f in out["frames"]],
        }
        Path(a.out).write_text(json.dumps(data), encoding="utf-8")
    last = out["frames"][-1]
    print(f"{len(out['frames'])} frames, {time.perf_counter() - t0:.2f}s", file=sys.stderr)
    print("\n".join(out["log"]))
    print("metrics:", last.metrics.model_dump())
    print(
        "final:",
        {v.id: (v.play_id, v.step_id, v.status.value, round(v.battery_pct)) for v in last.vehicles},
    )
