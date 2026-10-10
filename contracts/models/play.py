"""A play is one vehicle's workflow: steps of one action each (decisions 0006, 0015, 0016)."""

from typing import Any, Literal

from pydantic import BaseModel

from .enums import ActionKind, ConditionKind, Domain


class Condition(BaseModel):
    kind: ConditionKind
    params: dict[str, float | str] = {}


class Action(BaseModel):
    kind: ActionKind
    # move_to: target GeoPoint dict; patrol_route: route list of GeoPoint dicts;
    # watch_target/approach_target: target = "nearest" | "operator" | <target id>, distance_m
    params: dict[str, Any] = {}


class Exit(BaseModel):
    cond: Condition
    go_step: str


class Choice(BaseModel):
    id: str
    label: str
    play_by_vehicle: dict[str, str] = {}  # vehicle id -> play it starts (from that play's entry)
    target_by_vehicle: dict[str, str] = {}  # vehicle id -> target it watches (fleet choices)


class Switch(BaseModel):  # an operation-wide switch button, previewed then approved
    id: str
    label: str
    play_by_vehicle: dict[str, str]


class ReportSpec(BaseModel):
    text: str
    choices: list[Choice] = []  # with choices the vehicle waits for a Decision
    auto_choices: bool = False  # runtime fleet_choices builds the choices from the fleet


class Step(BaseModel):
    id: str
    name: str
    do: Action
    on: list[Exit] = []  # first true exit wins
    report: ReportSpec | None = None  # one card when the step is entered
    ui: dict[str, Any] = {}  # editor layout only; the engine ignores it


class EmergencyRules(BaseModel):
    battery_low_pct: float = 30
    link_lost_step: str | None = None
    battery_low_step: str | None = None
    operator_call_step: str | None = None


class Play(BaseModel):
    id: str
    name: str
    domains: list[Domain]  # vehicle domains that can run this play
    steps: list[Step]
    entry: str  # first step id
    emergency: EmergencyRules = EmergencyRules()
    origin: Literal["human", "ai_draft"] = "human"
    approved: bool = False
    template: bool = False


class ValidationIssue(BaseModel):
    code: str
    step_id: str | None = None
    message: str


class PlayCheck(BaseModel):
    ok: bool
    issues: list[ValidationIssue]
    est_return_battery: dict[str, float] = {}  # vehicle id -> expected battery % at home
