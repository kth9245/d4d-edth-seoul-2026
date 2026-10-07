"""Data contracts shared by all modules. Only the lead edits this file (branch contracts/*).

Units: WGS84 degrees, meters, UTC epoch milliseconds (t_ms).
"""

from enum import Enum

from pydantic import BaseModel, Field


class SensorType(str, Enum):
    RF = "rf"
    EOIR = "eoir"
    RADAR = "radar"


class Detection(BaseModel):
    id: str
    sensor: SensorType
    t_ms: int
    lat: float
    lon: float
    alt_m: float
    strength: float = Field(ge=0.0, le=1.0)


class Track(BaseModel):
    id: str
    t_ms: int
    lat: float
    lon: float
    alt_m: float
    vel_east_mps: float = 0.0
    vel_north_mps: float = 0.0
    hits: int = 1
    last_seen_ms: int


class ObjectClass(str, Enum):
    DRONE = "drone"
    BALLOON = "balloon"
    BIRD = "bird"
    UNKNOWN = "unknown"


class Assessment(BaseModel):
    track_id: str
    object_class: ObjectClass
    threat: float = Field(ge=0.0, le=1.0)
    reason: str


class ResponseKind(str, Enum):
    OBSERVE = "observe"
    SOFT_KILL = "soft_kill"
    HARD_KILL = "hard_kill"


class Response(BaseModel):
    track_id: str
    kind: ResponseKind
    reason: str


class Frame(BaseModel):
    t_ms: int
    tracks: list[Track]
    assessments: list[Assessment]
    responses: list[Response]


ALL_MODELS: dict[str, type[BaseModel]] = {
    "detection": Detection,
    "track": Track,
    "assessment": Assessment,
    "response": Response,
    "frame": Frame,
}
