"""Enumerations (docs/research/09 2.1, decisions 0015-0017)."""

from enum import Enum


class Domain(str, Enum):
    air = "air"
    sea = "sea"
    ground = "ground"


class VehicleStatus(str, Enum):
    ready = "ready"
    active = "active"
    returning = "returning"
    maintenance = "maintenance"
    lost = "lost"  # link lost


class ActionKind(str, Enum):  # the one action of a step; also the AI draft vocabulary
    move_to = "move_to"
    patrol_route = "patrol_route"
    search_area = "search_area"
    return_home = "return_home"
    watch_target = "watch_target"
    watch_point = "watch_point"
    approach_target = "approach_target"
    relay_comms = "relay_comms"
    hold = "hold"
    strike_target = "strike_target"  # decision 0033: strike the approved target


class ConditionKind(str, Enum):
    target_found = "target_found"
    arrived = "arrived"
    time_elapsed = "time_elapsed"
    battery_below = "battery_below"
    operator_choice = "operator_choice"
    signal_received = "signal_received"
    at_time = "at_time"  # decision 0045: T+ params.offset_ms after operation.started_ms


class CommandKind(str, Enum):  # what goes out to a vehicle
    move = "move"
    orbit = "orbit"
    keep_distance = "keep_distance"
    hold = "hold"
    follow_route = "follow_route"
    zigzag = "zigzag"
    return_home = "return_home"
    relay = "relay"
    strike = "strike"


class CommandSource(str, Enum):
    role_step = "role_step"
    operator_decision = "operator_decision"
    operator_direct = "operator_direct"
    injected_plan = "injected_plan"
    emergency = "emergency"


class BlockReason(str, Enum):  # one per safety floor rule (decision 0003)
    no_provenance = "no_provenance"
    outside_zone = "outside_zone"
    battery_insufficient = "battery_insufficient"


class ReportKind(str, Enum):
    target_detected = "target_detected"
    target_select = "target_select"  # operator picks the target of a step (decision 0016)
    vehicle_gap = "vehicle_gap"
    vehicle_lost = "vehicle_lost"
    battery_low = "battery_low"
    injection_pending = "injection_pending"
    command_blocked = "command_blocked"
    target_neutralized = "target_neutralized"  # alert only (decision 0033)


class TargetKind(str, Enum):
    boat = "boat"
    fast_boat = "fast_boat"
    person = "person"
    unknown = "unknown"


class EmergencyKind(str, Enum):
    link_lost = "link_lost"
    battery_low = "battery_low"
    operator_call = "operator_call"


class RunStatus(str, Enum):
    running = "running"
    paused = "paused"
    ended = "ended"
