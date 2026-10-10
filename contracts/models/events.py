"""Targets, report cards and operator inputs."""

from typing import Literal

from pydantic import BaseModel

from .enums import ReportKind, TargetKind
from .play import Choice
from .world import GeoPoint


class Target(BaseModel):
    id: str
    kind: TargetKind
    pos: GeoPoint
    vel_east_mps: float
    vel_north_mps: float
    first_seen_ms: int
    last_seen_ms: int
    seen_by: list[str] = []
    neutralized_ms: int | None = None  # struck (decision 0033); it stops moving
    reported_by: str | None = None  # vehicle that raised its target_detected card (decision 0036)
    play_id: str | None = None  # enemy progress (decision 0032)
    step_id: str | None = None
    waypoint_idx: int = 0  # -1 = arrived at the move_to destination
    step_since_ms: int | None = None  # when this step began (time_elapsed)


class Report(BaseModel):
    id: str
    t_ms: int
    kind: ReportKind
    vehicle_id: str | None = None
    target_id: str | None = None
    text: str
    choices: list[Choice] = []
    resolved_ms: int | None = None
    decision_id: str | None = None


class Decision(BaseModel):
    id: str
    t_ms: int
    report_id: str
    choice_id: str
    operator_id: str = "op1"


class Assignment(BaseModel):  # which vehicle runs which play, since when and why
    vehicle_id: str
    play_id: str
    since_ms: int
    reason: str  # "작전 배정" | "예비 투입: d1 대신" | "결정 dec-1" | "전환 inj-1"


class Injection(BaseModel):  # a switch request: previewed, then approved or rejected
    id: str
    t_ms: int
    label: str
    play_by_vehicle: dict[str, str]
    switch_id: str | None = None  # set when it comes from an Operation switch button
    status: Literal["pending", "approved", "rejected"] = "pending"


class DirectControl(BaseModel):
    id: str
    vehicle_id: str
    target: GeoPoint
    t_ms: int
