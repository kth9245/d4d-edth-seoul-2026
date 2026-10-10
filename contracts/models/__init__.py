"""Data contracts shared by all modules. Only the lead edits this package.

Units: WGS84 degrees, meters, m/s, UTC epoch milliseconds (t_ms). Conventions: contracts/API.md.
Import from here (`from contracts.models import Play`), never from the submodules.
"""

import re

from pydantic import BaseModel

from .api import Accepted, DecisionIn, DirectIn, DraftIn, ScenarioInfo, SwitchIn
from .command import Block, Command, PassedCommand, Provenance
from .enums import (
    ActionKind,
    BlockReason,
    CommandKind,
    CommandSource,
    ConditionKind,
    Domain,
    EmergencyKind,
    ReportKind,
    RunStatus,
    TargetKind,
    VehicleStatus,
)
from .events import Assignment, Decision, DirectControl, Injection, Report, Target
from .frame import Frame, Metrics, RunState, Scenario, ScenarioEvent, TickInputs, TickOutcome
from .legacy import (
    Assessment,
    Detection,
    LegacyFrame,
    ObjectClass,
    Response,
    ResponseKind,
    SensorType,
    Track,
)
from .ontology import (
    ActionGroup,
    CapabilityReason,
    ObjectGraph,
    ObjectLink,
    ObjectNode,
    Ontology,
    OntologyView,
    VehicleCapabilities,
    VehicleKind,
)
from .play import (
    Action,
    Choice,
    Condition,
    EmergencyRules,
    Exit,
    Play,
    PlayCheck,
    ReportSpec,
    Step,
    Switch,
    ValidationIssue,
)
from .world import (
    EnemySpec,
    GeoPoint,
    Operation,
    Polygon,
    VehicleSpec,
    VehicleState,
    WatchPoint,
)

_MODELS: list[type[BaseModel]] = [
    GeoPoint, Polygon, VehicleSpec, VehicleState, Operation, EnemySpec, WatchPoint,
    Condition, Action, Exit, Choice, Switch, ReportSpec, Step, EmergencyRules, Play,
    ValidationIssue, PlayCheck,
    Provenance, Command, PassedCommand, Block,
    Target, Report, Decision, Assignment, Injection, DirectControl,
    Metrics, RunState, Frame, ScenarioEvent, Scenario, TickInputs, TickOutcome,
    ActionGroup, VehicleKind, Ontology, CapabilityReason, VehicleCapabilities, OntologyView,
    ObjectNode, ObjectLink, ObjectGraph,
    DecisionIn, DirectIn, SwitchIn, DraftIn, Accepted, ScenarioInfo,
    Detection, Track, Assessment, Response, LegacyFrame,
]  # fmt: skip


def _snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


# file stem in contracts/examples and contracts/schema -> model
ALL_MODELS: dict[str, type[BaseModel]] = {_snake(m.__name__): m for m in _MODELS}

__all__ = [
    "ALL_MODELS",
    *(m.__name__ for m in _MODELS),
    "ActionKind", "BlockReason", "CommandKind", "CommandSource", "ConditionKind", "Domain",
    "EmergencyKind", "ReportKind", "RunStatus", "TargetKind", "VehicleStatus",
    "ObjectClass", "ResponseKind", "SensorType",
]  # fmt: skip
