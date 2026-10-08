"""Section 2 of docs/research/09 transcribed literally to pydantic v2."""
from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel

class Domain(str, Enum):
    air = "air"; sea = "sea"; ground = "ground"
class VehicleStatus(str, Enum):
    ready = "ready"; active = "active"; returning = "returning"; maintenance = "maintenance"; lost = "lost"
class ActionKind(str, Enum):  # step의 행동 하나. 분기·보고는 step의 on/report 필드 (결정 0006 단순형)
    move_to="move_to"; patrol_route="patrol_route"; search_area="search_area"; return_home="return_home"
    watch_target="watch_target"; watch_point="watch_point"; approach_target="approach_target"; relay_comms="relay_comms"
    hold="hold"
class ConditionKind(str, Enum):
    target_found="target_found"; arrived="arrived"; time_elapsed="time_elapsed"; battery_below="battery_below"
    operator_choice="operator_choice"; signal_received="signal_received"
class CommandKind(str, Enum):
    move="move"; orbit="orbit"; keep_distance="keep_distance"; hold="hold"; follow_route="follow_route"
    zigzag="zigzag"; return_home="return_home"; relay="relay"
class CommandSource(str, Enum):
    play_step="play_step"; operator_decision="operator_decision"; operator_direct="operator_direct"
    injected_plan="injected_plan"; emergency="emergency"
class BlockReason(str, Enum):
    no_provenance="no_provenance"; outside_zone="outside_zone"; battery_insufficient="battery_insufficient"
class ReportKind(str, Enum):
    target_detected="target_detected"; role_gap="role_gap"; vehicle_lost="vehicle_lost"; battery_low="battery_low"
    injection_pending="injection_pending"; command_blocked="command_blocked"
class TargetKind(str, Enum):
    boat="boat"; fast_boat="fast_boat"; person="person"; unknown="unknown"
class EmergencyKind(str, Enum):
    link_lost="link_lost"; battery_low="battery_low"; operator_call="operator_call"
class RunMode(str, Enum):
    role="role"; manual_baseline="manual_baseline"

class GeoPoint(BaseModel):
    lat: float; lon: float; alt_m: float = 0
class Polygon(BaseModel):
    points: list[GeoPoint]
class VehicleSpec(BaseModel):
    id: str; name: str; domain: Domain; speed_mps: float; endurance_min: float; sensor_range_m: float
    capabilities: list[ActionKind]; home: GeoPoint
class VehicleState(BaseModel):
    id: str; t_ms: int; pos: GeoPoint; heading_deg: float; battery_pct: float; status: VehicleStatus
    role_id: str | None = None; play_id: str | None = None; step_id: str | None = None
    entered_step: bool = False; waypoint_idx: int = 0; emergency: EmergencyKind | None = None; resume_step_id: str | None = None
    active: PassedCommand | None = None  # PROTO ADDITION under test
    pending_report_id: str | None = None  # PROTO ADDITION: vehicle waits for a Decision
class Operation(BaseModel):
    id: str; name: str; purpose: str; area: Polygon; zone: Polygon; vehicle_ids: list[str]; started_ms: int | None = None
class Role(BaseModel):
    id: str; name: str; domains: list[Domain]; required: list[ActionKind]; vehicles: list[str]
class Condition(BaseModel):
    kind: ConditionKind; params: dict[str, float | str] = {}
class Action(BaseModel):
    kind: ActionKind; params: dict[str, Any] = {}
class Exit(BaseModel):
    cond: Condition; go_step: str
class Choice(BaseModel):
    id: str; label: str; step_by_role: dict[str, str]
class ReportSpec(BaseModel):
    text: str; choices: list[Choice] = []  # choices가 있으면 결정을 기다린다(승인 지점)
class Step(BaseModel):
    id: str; role_id: str; name: str; do: Action; on: list[Exit] = []; report: ReportSpec | None = None; ui: dict = {}
class EmergencyRules(BaseModel):
    battery_low_pct: float = 30; link_lost_step: str | None = None; battery_low_step: str | None = None; operator_call_step: str | None = None
class Play(BaseModel):
    id: str; name: str; roles: list[Role]; steps: list[Step]; emergency: EmergencyRules = EmergencyRules()
    entry: dict[str, str]; origin: Literal["human", "ai_draft"] = "human"; approved: bool = False; template: bool = False
class ValidationIssue(BaseModel):
    code: str; step_id: str | None = None; message: str
class PlayCheck(BaseModel):
    ok: bool; issues: list[ValidationIssue]; est_return_battery: dict[str, float]
class Provenance(BaseModel):
    source: CommandSource; play_id: str | None = None; step_id: str | None = None
    decision_id: str | None = None; injection_id: str | None = None; operator_id: str | None = None; issued_ms: int
class Command(BaseModel):
    id: str; vehicle_id: str; kind: CommandKind; params: dict = {}; provenance: Provenance | None = None
class PassedCommand(BaseModel):
    command: Command; checks: list[str]; passed_ms: int
class Block(BaseModel):
    command_id: str; vehicle_id: str; reason: BlockReason; detail: str; alternative: Command | None = None; t_ms: int
class Target(BaseModel):
    id: str; kind: TargetKind; pos: GeoPoint; vel_east_mps: float; vel_north_mps: float
    first_seen_ms: int; last_seen_ms: int; seen_by: list[str] = []
class Report(BaseModel):
    id: str; t_ms: int; kind: ReportKind; vehicle_id: str | None = None; target_id: str | None = None; role_id: str | None = None
    text: str; choices: list[Choice] = []; resolved_ms: int | None = None; decision_id: str | None = None
class Decision(BaseModel):
    id: str; t_ms: int; report_id: str; choice_id: str; operator_id: str = "op1"
class Assignment(BaseModel):
    role_id: str; vehicle_id: str; since_ms: int; reason: str
class Injection(BaseModel):
    id: str; play_id: str; anchor: dict; proposed: list[Assignment]; status: Literal["pending", "approved", "rejected"]; t_ms: int
class DirectControl(BaseModel):
    vehicle_id: str; target: GeoPoint; t_ms: int
class Metrics(BaseModel):
    operator_actions: int = 0; manual_baseline_actions: int = 0; open_reports_max: int = 0; role_gap_ms: int = 0
    blocked_commands: int = 0; decisions: int = 0; commands_sent: int = 0; mission_success: bool | None = None
class Frame(BaseModel):
    t_ms: int; mode: RunMode; vehicles: list[VehicleState]; targets: list[Target]; reports: list[Report]
    assignments: list[Assignment]; blocks: list[Block]; injections: list[Injection]; metrics: Metrics; log: list[str] = []
class ScenarioEvent(BaseModel):
    t_ms: int; kind: Literal["spawn_target", "target_move", "vehicle_link_lost", "vehicle_battery_set", "split_target"]; params: dict
class Scenario(BaseModel):
    id: str; operation: Operation; vehicles: list[VehicleSpec]; plays: list[Play]; events: list[ScenarioEvent]
    seed: int; tick_ms: int = 200; speed: float = 1.0
class TickInputs(BaseModel):
    decisions: list[Decision] = []; direct: list[DirectControl] = []; injections: list[Injection] = []; mode: RunMode = RunMode.role
