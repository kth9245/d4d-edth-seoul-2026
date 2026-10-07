"""sim module internal types (scenario file format)."""

from typing import Literal

from pydantic import BaseModel, Field


class Origin(BaseModel):
    lat: float
    lon: float


class SimObject(BaseModel):
    id: str
    kind: Literal["drone", "balloon", "bird"]
    start_east_m: float
    start_north_m: float
    alt_m: float = Field(ge=0)
    vel_east_mps: float
    vel_north_mps: float
    appear_s: float = Field(default=0.0, ge=0)


class Scenario(BaseModel):
    name: str
    start_ms: int
    duration_s: float = Field(gt=0)
    step_ms: int = Field(gt=0)
    origin: Origin
    objects: list[SimObject]


class TruthPoint(BaseModel):
    object_id: str
    kind: str
    lat: float
    lon: float
    alt_m: float
