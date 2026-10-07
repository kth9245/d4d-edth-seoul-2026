"""Headless demo smoke test: run the scenario for N simulated seconds, validate every frame."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from contracts.models import Frame  # noqa: E402
from modules.gateway import Engine  # noqa: E402
from modules.sim import load_scenario  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default=str(ROOT / "demo/scenarios/seoul_mixed.yaml"))
    ap.add_argument("--seconds", type=float, default=10)
    a = ap.parse_args()
    try:
        scenario = load_scenario(a.scenario)
        engine = Engine(scenario)
        steps = int(a.seconds * 1000 / scenario.step_ms)
        for _ in range(steps):
            Frame.model_validate(engine.step().model_dump())
    except Exception as e:  # noqa: BLE001 - report any failure briefly
        print(f"smoke FAIL: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"smoke OK: {steps} frames, {len(engine.tracks)} tracks")


if __name__ == "__main__":
    main()
