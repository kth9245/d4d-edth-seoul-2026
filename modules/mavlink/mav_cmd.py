"""Command kind -> MAV_CMD items (decision 0011), one table for compile_mavlink and mavlink_lines (decision 0063)."""

from contracts.models import CommandKind, Domain

WAYPOINT, LOITER_UNLIM, RTL, DO_SET_MODE, MISSION_START = 16, 17, 20, 176, 300  # MAV_CMD
NAME = {WAYPOINT: "MAV_CMD_NAV_WAYPOINT", LOITER_UNLIM: "MAV_CMD_NAV_LOITER_UNLIM",
        RTL: "MAV_CMD_NAV_RETURN_TO_LAUNCH", DO_SET_MODE: "MAV_CMD_DO_SET_MODE",
        MISSION_START: "MAV_CMD_MISSION_START"}  # fmt: skip
NAV = (WAYPOINT, LOITER_UNLIM)  # mission items; the rest go as COMMAND_LONG
FOLLOW = {Domain.air: 23, Domain.sea: 6, Domain.ground: 6}  # ArduPilot custom mode (Copter/Rover)
ROVER_HOLD = 4
AIR_ALT_M = 50  # roles store alt_m 0; drones need a flight altitude
K = CommandKind


def points(params: dict, domain: Domain) -> list[list[float]]:
    pts = params.get("route") or (
        [params["target"]] if isinstance(params.get("target"), dict) else []
    )
    alt = AIR_ALT_M if domain == Domain.air else 0
    return [[q["lat"], q["lon"], q.get("alt_m") or alt] for q in pts]


def items(kind: CommandKind | None, params: dict, domain: Domain) -> list[list[float]]:
    """[MAV_CMD, p1..p7] per mission item; empty when the vehicle cannot do the action."""
    pts = points(params, domain)
    if kind in (K.move, K.follow_route, K.zigzag):
        return [[WAYPOINT, 0, 0, 0, 0, *pt] for pt in pts]
    if kind == K.return_home:
        return [[RTL, 0, 0, 0, 0, 0, 0, 0]]
    if kind == K.keep_distance:
        return [[DO_SET_MODE, 1, FOLLOW[domain], 0, 0, 0, 0, 0]]
    if kind == K.hold and domain == Domain.ground:
        return [[DO_SET_MODE, 1, ROVER_HOLD, 0, 0, 0, 0, 0]]
    if kind in (K.orbit, K.hold, K.relay):  # lat/lon 0 = loiter where the vehicle is (ArduPilot)
        return [[LOITER_UNLIM, 0, 0, 0, 0, *(pts[0] if pts else [0, 0, 0])]]
    return []
