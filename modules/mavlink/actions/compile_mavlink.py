"""MAV-01 compile_mavlink: Role을 기체별 QGC .plan + pymavlink 스크립트로(결정 0011, 실제 전송 없음)
.plan은 entry step의 미션, 스크립트는 step 그래프 전체(틀: modules/mavlink/vehicle_script.py.txt).
SPEC: modules/mavlink/SPEC.md#MAV-01
"""

from pathlib import Path

from contracts.models import CommandKind, Domain, Operation, Role, Step, VehicleSpec
from modules.role import expand_action

TEMPLATE = Path(__file__).resolve().parents[1] / "vehicle_script.py.txt"
WAYPOINT, LOITER_UNLIM, RTL, DO_SET_MODE = 16, 17, 20, 176  # MAV_CMD
FOLLOW = {Domain.air: 23, Domain.sea: 6, Domain.ground: 6}  # ArduPilot custom mode (Copter/Rover)
ROVER_HOLD = 4
MAV_TYPE = {Domain.air: 2, Domain.sea: 11, Domain.ground: 10}  # quadrotor / surface boat / rover
AIR_ALT_M = 50  # roles store alt_m 0; drones need a flight altitude
K = CommandKind


def _points(step: Step, spec: VehicleSpec) -> list[list[float]]:
    p = step.do.params
    pts = p.get("route") or ([p["target"]] if isinstance(p.get("target"), dict) else [])
    alt = AIR_ALT_M if spec.domain == Domain.air else 0
    return [[q["lat"], q["lon"], q.get("alt_m") or alt] for q in pts]


def _items(step: Step, spec: VehicleSpec) -> list[list[float]]:
    """[MAV_CMD, p1..p7] per mission item; empty when the vehicle cannot do the action."""
    kind, pts = expand_action(step.do, spec.domain), _points(step, spec)
    if kind in (K.move, K.follow_route, K.zigzag):
        return [[WAYPOINT, 0, 0, 0, 0, *pt] for pt in pts]
    if kind == K.return_home:
        return [[RTL, 0, 0, 0, 0, 0, 0, 0]]
    if kind == K.keep_distance:
        return [[DO_SET_MODE, 1, FOLLOW[spec.domain], 0, 0, 0, 0, 0]]
    if kind == K.hold and spec.domain == Domain.ground:
        return [[DO_SET_MODE, 1, ROVER_HOLD, 0, 0, 0, 0, 0]]
    if kind in (K.orbit, K.hold, K.relay):  # lat/lon 0 = loiter where the vehicle is (ArduPilot)
        return [[LOITER_UNLIM, 0, 0, 0, 0, *(pts[0] if pts else [0, 0, 0])]]
    return []


def _plan(items: list[list[float]], spec: VehicleSpec) -> dict:
    mission_items = [
        {"type": "SimpleItem", "autoContinue": True, "command": int(c), "doJumpId": n + 1,
         "frame": 3, "params": p, "AMSLAltAboveTerrain": None, "Altitude": p[6], "AltitudeMode": 1}
        for n, (c, *p) in enumerate(items)
    ]  # fmt: skip
    home = [spec.home.lat, spec.home.lon, spec.home.alt_m]
    mission = {"version": 2, "firmwareType": 3, "vehicleType": MAV_TYPE[spec.domain],
               "cruiseSpeed": spec.speed_mps, "hoverSpeed": spec.speed_mps,
               "plannedHomePosition": home, "items": mission_items}  # fmt: skip
    return {"fileType": "Plan", "version": 1, "groundStation": "QGroundControl", "mission": mission,
            "geoFence": {"circles": [], "polygons": [], "version": 2},
            "rallyPoints": {"points": [], "version": 2}}  # fmt: skip


def compile_mavlink(
    role: Role, op: Operation, specs: dict[str, VehicleSpec]
) -> dict[str, tuple[dict, str]]:
    out = {}
    for vid in (v for v, pid in op.assign.items() if pid == role.id):
        spec = specs[vid]
        steps = {
            s.id: {"items": _items(s, spec), "wait": bool(s.report and s.report.choices),
                   "moves": {c.id: c.role_by_vehicle[vid] for c in (s.report.choices if s.report else [])
                             if vid in c.role_by_vehicle},
                   "exits": [[e.cond.kind.value, e.cond.params, e.go_step] for e in s.on]}
            for s in role.steps
        }  # fmt: skip
        fill = {"VEHICLE": vid, "ROLE": role.id, "ENTRY": role.entry, "STEPS": steps}
        script = TEMPLATE.read_text(encoding="utf-8")
        for key, value in fill.items():
            script = script.replace("{" + key + "}", repr(value))
        out[vid] = (_plan(steps[role.entry]["items"], spec), script)
    return out
