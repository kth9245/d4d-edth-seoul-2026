"""EngineState: the tick loop's whole state (contracts/API.md §3). Not a contract; gateway only."""

from dataclasses import dataclass, field

from contracts.models import (
    Assignment,
    Block,
    Command,
    Decision,
    Injection,
    Metrics,
    PassedCommand,
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
    # history for GET /graph (decision 0038)
    decisions: list[Decision] = field(default_factory=list)
    commands: list[Command] = field(default_factory=list)  # every command issued, passed or blocked
    passed: list[PassedCommand] = field(default_factory=list)
