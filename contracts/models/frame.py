"""Metrics, the per-tick Frame sent to the screen, scenario input and tick input/outcome."""

from typing import Any, Literal

from pydantic import BaseModel

from .command import Block, Command, PassedCommand
from .enums import RunStatus
from .events import Assignment, Decision, DirectControl, Injection, Report, Target
from .play import Play
from .world import Operation, VehicleSpec, VehicleState


class Metrics(BaseModel):  # definitions: docs/research/09 2.3
    operator_actions: int = 0
    manual_baseline_actions: int = 0
    open_reports_max: int = 0
    vehicle_gap_ms: int = 0
    blocked_commands: int = 0
    decisions: int = 0
    commands_sent: int = 0
    mission_success: bool | None = None


class RunState(BaseModel):
    status: RunStatus = RunStatus.paused
    speed: float = 1.0


class Frame(BaseModel):
    t_ms: int
    run: RunState
    vehicles: list[VehicleState]
    targets: list[Target]
    reports: list[Report]
    assignments: list[Assignment]
    blocks: list[Block]
    injections: list[Injection]
    metrics: Metrics
    log: list[str] = []  # lines added this tick


class ScenarioEvent(BaseModel):
    offset_ms: int  # ms after operation.started_ms (decision 0014)
    kind: Literal[
        "spawn_target", "target_move", "vehicle_link_lost", "vehicle_battery_set", "split_target"
    ]
    params: dict[str, Any]  # keys per kind: docs/research/09 2.2 ScenarioEvent


class Scenario(BaseModel):
    id: str
    operation: Operation
    vehicles: list[VehicleSpec]
    plays: list[Play]
    events: list[ScenarioEvent] = []
    seed: int = 0
    tick_ms: int = 200
    speed: float = 1.0


class TickInputs(BaseModel):
    decisions: list[Decision] = []
    direct: list[DirectControl] = []
    injections: list[Injection] = []  # new requests and approve/reject status changes


class TickOutcome(BaseModel):  # what one tick produced; input of runtime.update_metrics
    inputs: TickInputs = TickInputs()
    commands: list[Command] = []
    passed: list[PassedCommand] = []
    blocks: list[Block] = []
    new_reports: list[Report] = []
    assignments: list[Assignment] = []
    states: list[VehicleState] = []
    targets: list[Target] = []
    plays: dict[str, Play] = {}
