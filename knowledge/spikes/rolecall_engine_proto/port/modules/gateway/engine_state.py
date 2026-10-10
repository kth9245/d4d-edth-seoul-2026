"""EngineState: the tick loop's whole state (contracts/API.md §3). Not a contract; gateway only."""

from dataclasses import dataclass

from contracts.models import (
    Assignment,
    Block,
    Injection,
    Metrics,
    Report,
    Role,
    RunState,
    Scenario,
    Target,
    VehicleSpec,
    VehicleState,
)


@dataclass
class EngineState:
    t_ms: int
    scenario: Scenario
    specs: dict[str, VehicleSpec]
    roles: dict[str, Role]
    states: list[VehicleState]
    targets: list[Target]
    reports: list[Report]
    assignments: list[Assignment]
    blocks: list[Block]
    injections: list[Injection]
    metrics: Metrics
    run: RunState
