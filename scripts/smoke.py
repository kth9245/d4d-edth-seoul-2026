"""Headless integration-1 slice on the demo scenario (docs/research/09 section 4), run by ship.sh.

Ticks the real engine until a target_detected report with choices appears, sends one decision (its first
choice), runs a little longer and checks: every vehicle the choice names switched to its play, at least one of
them moved, no command was blocked after the decision, the card was resolved, metrics.operator_actions == 1.
Every frame must survive the WS JSON round trip. Prints one line; exits 1 with a short reason on failure.
"""

import argparse
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from contracts.models import Decision, Frame, TickInputs  # noqa: E402
from modules.gateway.engine import init_engine, tick  # noqa: E402
from modules.sim import load_scenario_json  # noqa: E402
from shared.log import get_logger, setup_logging  # noqa: E402

log = get_logger("smoke")


def _step(es, inputs=None):
    es, frame = tick(es, inputs or TickInputs())
    Frame.model_validate_json(frame.model_dump_json())  # what the screen receives
    return es, frame


def _moved_m(a, b) -> float:
    dy = (a.lat - b.lat) * 111_195
    dx = (a.lon - b.lon) * 111_195 * math.cos(math.radians(a.lat))
    return math.hypot(dx, dy)


def run(path: str, max_minutes: float, after_s: float) -> str:
    sc = load_scenario_json(path)
    es = init_engine(sc)
    limit, ticks, frame, card = int(max_minutes * 60_000 / sc.tick_ms), 0, None, None
    while card is None:
        if ticks >= limit:
            raise AssertionError(
                f"no open target_detected report with choices within {max_minutes:g} min"
            )
        es, frame = _step(es)
        ticks += 1
        card = next(
            (
                r
                for r in frame.reports
                if r.kind == "target_detected" and r.choices and r.resolved_ms is None
            ),
            None,
        )
    choice, at = card.choices[0], (frame.t_ms - sc.operation.started_ms) // 1000
    before = {v.id: v.pos for v in frame.vehicles}
    blocks = len(frame.blocks)
    es, frame = _step(
        es,
        TickInputs(
            decisions=[
                Decision(id="dec-1", t_ms=frame.t_ms, report_id=card.id, choice_id=choice.id)
            ]
        ),
    )
    ticks += 1
    for _ in range(int(after_s * 1000 / sc.tick_ms)):
        es, frame = _step(es)
        ticks += 1
    now = {v.id: v for v in frame.vehicles}
    wrong = {
        v: (now[v].play_id, p) for v, p in choice.play_by_vehicle.items() if now[v].play_id != p
    }
    if wrong:
        raise AssertionError(f"decision did not switch plays (vehicle: got, want): {wrong}")
    moved = [v for v in choice.play_by_vehicle if _moved_m(now[v].pos, before[v]) > 1]
    if not moved:
        raise AssertionError(f"no vehicle of the choice moved in {after_s:g} s after the decision")
    if len(frame.blocks) != blocks:
        raise AssertionError(
            f"commands blocked after the decision: {[b.detail for b in frame.blocks[blocks:]]}"
        )
    if next(r for r in frame.reports if r.id == card.id).resolved_ms is None:
        raise AssertionError("the decided card is still open")
    if frame.metrics.operator_actions != 1:
        raise AssertionError(f"operator_actions={frame.metrics.operator_actions}, want 1")
    return (
        f"{ticks} ticks, card {card.id} at T+{at // 60}:{at % 60:02d}, '{choice.label}' switched "
        f"{len(choice.play_by_vehicle)} vehicles, moved {','.join(moved)}, operator_actions=1"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default=str(ROOT / "demo/scenarios/baengnyeong_night.json"))
    ap.add_argument(
        "--max-minutes", type=float, default=30, help="give up looking for the card after this"
    )
    ap.add_argument(
        "--after-s", type=float, default=20, help="simulated seconds to run after the decision"
    )
    a = ap.parse_args()
    setup_logging("smoke")  # decision 0010
    t0 = time.monotonic()
    try:
        line = run(a.scenario, a.max_minutes, a.after_s)
    except Exception as e:  # noqa: BLE001 - report any failure briefly
        log.exception("smoke failed")
        print(f"smoke FAIL: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"smoke OK: {line} ({time.monotonic() - t0:.1f}s)")


if __name__ == "__main__":
    main()
