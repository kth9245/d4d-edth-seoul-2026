"""Commands and the safety floor. Only safety.check_command creates PassedCommand."""

from typing import Any

from pydantic import BaseModel

from .enums import BlockReason, CommandKind, CommandSource


class Provenance(BaseModel):
    source: CommandSource
    play_id: str | None = None
    step_id: str | None = None
    decision_id: str | None = None
    injection_id: str | None = None
    operator_id: str | None = None
    issued_ms: int


class Command(BaseModel):
    id: str
    vehicle_id: str
    kind: CommandKind
    params: dict[str, Any] = {}  # target GeoPoint dict | route list | target_id | distance_m
    provenance: Provenance | None = None


class PassedCommand(BaseModel):
    command: Command
    checks: list[str]  # names of the safety rules it passed
    passed_ms: int


class Block(BaseModel):
    command_id: str
    vehicle_id: str
    reason: BlockReason
    detail: str
    alternative: Command | None = None
    t_ms: int
