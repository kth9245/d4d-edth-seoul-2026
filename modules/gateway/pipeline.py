"""gateway pipeline: run all modules for one time step. No domain logic here."""

from contracts.models import LegacyFrame, Track
from modules.assess import assess
from modules.gateway.actions.build_frame import build_frame
from modules.respond import respond
from modules.sensing import normalize
from modules.sim import Scenario, simulate
from modules.tracking import update


class Engine:
    def __init__(self, scenario: Scenario, seed: int = 0):
        self.scenario, self.seed = scenario, seed
        self.t_ms = scenario.start_ms
        self.end_ms = scenario.start_ms + int(scenario.duration_s * 1000)
        self.tracks: list[Track] = []

    @property
    def done(self) -> bool:
        return self.t_ms >= self.end_ms

    def step(self) -> LegacyFrame:
        detections = normalize(simulate(self.scenario, self.t_ms, self.seed))
        self.tracks = update(self.tracks, detections, self.t_ms)
        origin = self.scenario.origin
        assessments = assess(self.tracks, origin.lat, origin.lon)
        frame = build_frame(self.t_ms, self.tracks, assessments, respond(assessments))
        self.t_ms += self.scenario.step_ms
        return frame
