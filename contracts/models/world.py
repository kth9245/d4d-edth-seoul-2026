"""Space, vehicles and the operation (the layer that groups the vehicles' plays)."""

from pydantic import BaseModel, Field

from .command import PassedCommand
from .enums import ActionKind, Domain, EmergencyKind, VehicleStatus
from .play import Switch


class GeoPoint(BaseModel):
    lat: float
    lon: float
    alt_m: float = 0


class Polygon(BaseModel):
    points: list[GeoPoint] = Field(min_length=3)  # not closed: last point != first


class VehicleSpec(BaseModel):
    id: str
    name: str
    domain: Domain
    speed_mps: float
    endurance_min: float
    sensor_range_m: float
    capabilities: list[ActionKind]
    home: GeoPoint


class VehicleState(BaseModel):
    id: str
    t_ms: int
    pos: GeoPoint
    heading_deg: float
    battery_pct: float
    status: VehicleStatus
    play_id: str | None = None
    step_id: str | None = None
    entered_step: bool = False  # False: emit this step's command/card once on the next tick
    waypoint_idx: int = 0  # -1 = arrived at the current command's destination
    active: PassedCommand | None = None  # sim keeps executing this between commands
    pending_report_id: str | None = None  # waiting for a Decision; no transitions meanwhile
    target_id: str | None = None  # target resolved for this step (nearest / operator / fixed)
    emergency: EmergencyKind | None = None
    resume_play_id: str | None = None  # where to return after direct control
    resume_step_id: str | None = None


class Operation(BaseModel):
    id: str
    name: str
    purpose: str = ""
    area: Polygon  # shown on the map
    zone: Polygon  # safety rule 2; not editable from the live board
    vehicle_ids: list[str]
    started_ms: int | None = None  # epoch ms; required when a scenario is loaded (decision 0014)
    assign: dict[str, str] = {}  # vehicle id -> play id at start
    reserve: dict[str, list[str]] = {}  # vehicle id -> reserves in order (decision 0016)
    switches: list[Switch] = []
