"""sim pipeline: calls actions in order. No logic here."""

from contracts.models import Detection
from modules.sim.actions.emit_detections import emit_detections
from modules.sim.actions.object_positions import object_positions
from modules.sim.types import Scenario


def simulate(scenario: Scenario, t_ms: int, seed: int = 0) -> list[Detection]:
    return emit_detections(object_positions(scenario, t_ms), t_ms, seed)
