"""Space, vehicles and the operation (the layer that groups the vehicles' plays)."""

from pydantic import BaseModel, Field

from .command import PassedCommand
from .enums import ActionKind, Domain, EmergencyKind, TargetKind, VehicleStatus
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
    capabilities: list[ActionKind] = []  # from Scenario.ontology when kind is set (decision 0038)
    home: GeoPoint
    recharge_min: float = 0  # battery swap/charge at home (decision 0037); 0 = no recharge
    kind: str | None = None  # VehicleKind id in Scenario.ontology (decision 0038)
    kind_path: list[str] = []  # kind labels up to the root, filled by the scenario loader
    rf_range_m: float = 0  # RF receive range (decision 0039); 0 = cannot receive


class EnemySpec(BaseModel):  # decision 0032: an enemy follows its own play, no safety checks
    id: str
    kind: TargetKind
    speed_mps: float
    appear_offset_ms: int  # ms after operation.started_ms
    pos: GeoPoint | None = None  # where it appears, or
    from_enemy: str | None = None  # at that enemy's current position
    play_id: str
    emit_start_offset_ms: int | None = (
        None  # emits from this long after it appears; None = silent (0039)
    )


class WatchPoint(BaseModel):  # a place to guard; inside its radius adds to a target's threat (0039)
    id: str
    name: str
    pos: GeoPoint
    radius_m: float


class RouteOffset(BaseModel):  # meters from where the vehicle is as the card starts (0044)
    north_m: float
    east_m: float


class RouteDef(BaseModel):  # a named route the editor offers: points or offsets, not both (0044)
    id: str
    name: str
    points: list[GeoPoint] = []  # fixed route
    offsets: list[RouteOffset] = []  # relative route, measured as the card starts


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
    decision_id: str | None = None  # operator decision that moved it into this play (decision 0033)
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
    started_ms: int | None = None  # epoch ms; required when a scenario is loaded (decision 0018)
    assign: dict[str, str] = {}  # vehicle id -> play id at start
    reserve: dict[str, list[str]] = {}  # vehicle id -> reserves in order (decision 0016)
    switches: list[Switch] = []
    rotation: list[str] = []  # vehicles that relieve each other on patrol (decision 0037)
    rotation_plays: list[str] = []  # patrol plays the rotation keeps covered
    rotation_pools: dict[
        str, list[str]
    ] = {}  # patrol play -> the drones that relieve each other on it
