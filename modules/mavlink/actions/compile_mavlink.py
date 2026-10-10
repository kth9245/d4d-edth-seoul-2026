"""MAV-01 compile_mavlink: Role을 기체별 QGC .plan + pymavlink 스크립트로(결정 0011, 실제 전송 없음)
.plan은 entry step의 미션, 스크립트는 step 그래프 전체(틀: modules/mavlink/vehicle_script.py.txt).
명령 종류 → MAV_CMD 대응표는 mav_cmd.py(mavlink_lines와 같은 표, 결정 0063).
SPEC: modules/mavlink/SPEC.md#MAV-01
"""

from pathlib import Path

from contracts.models import Domain, Operation, Role, Step, VehicleSpec
from modules.mavlink.mav_cmd import items as mav_items
from modules.role import expand_action

TEMPLATE = Path(__file__).resolve().parents[1] / "vehicle_script.py.txt"
MAV_TYPE = {Domain.air: 2, Domain.sea: 11, Domain.ground: 10}  # quadrotor / surface boat / rover


def _items(step: Step, spec: VehicleSpec) -> list[list[float]]:
    return mav_items(expand_action(step.do, spec.domain), step.do.params, spec.domain)


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
