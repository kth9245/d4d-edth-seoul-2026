"""Stand-in for engine.py until Part2-17 lands: the example Frame with a moving clock, no
simulation, inputs ignored. Remove before 통합 2 (contracts/API.md §6).
"""

from pathlib import Path

from contracts.models import Frame, Scenario, TickInputs

ROOT = Path(__file__).resolve().parents[2]
FRAME = Frame.model_validate_json((ROOT / "contracts/examples/frame.json").read_text("utf-8"))


def load_scenario_json(path: str | Path) -> Scenario:
    return Scenario.model_validate_json(Path(path).read_text(encoding="utf-8"))


def init_engine(scenario: Scenario) -> tuple[int, int]:
    return scenario.operation.started_ms, scenario.tick_ms


def tick(state: tuple[int, int], inputs: TickInputs) -> tuple[tuple[int, int], Frame]:
    t, dt = state
    return (t + dt, dt), FRAME.model_copy(update={"t_ms": t + dt})
