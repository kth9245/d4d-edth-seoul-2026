"""MAV-02 mavlink_lines: 통과한 명령을 시간순 MAVLink 메시지 줄로(GET /mavlink, 결정 0064)
NAV 명령은 MISSION_ITEM_INT seq 줄들 뒤에 MISSION_START, 나머지는 COMMAND_LONG 한 줄. 대응표가 없는 명령(타격)은 줄 없음.
대응표는 compile_mavlink과 같은 mav_cmd.py(결정 0011).
SPEC: modules/mavlink/SPEC.md#MAV-02
"""

from datetime import datetime

from contracts.models import PassedCommand, VehicleSpec
from modules.mavlink.mav_cmd import MISSION_START, NAME, NAV, items
from shared.kst import KST


def _line(head: str, msg: str, cmd: float, params: list[float]) -> str:
    nums = " ".join(f"{p:.10g}" for p in params)
    return f"{head} {msg} {NAME[int(cmd)]}({int(cmd)}) {nums}"


def mavlink_lines(passed: list[PassedCommand], specs: dict[str, VehicleSpec]) -> list[str]:
    out = []
    for pc in passed:
        c = pc.command
        head = f"{datetime.fromtimestamp(pc.passed_ms / 1000, KST):%H:%M:%S} {c.vehicle_id}"
        rows = items(c.kind, c.params, specs[c.vehicle_id].domain)
        nav = [r for r in rows if r[0] in NAV]
        out += [_line(head, f"MISSION_ITEM_INT seq{n}", r[0], r[1:]) for n, r in enumerate(nav)]
        out += [_line(head, "COMMAND_LONG", MISSION_START, [0] * 7)] if nav else []
        out += [_line(head, "COMMAND_LONG", r[0], r[1:]) for r in rows if r[0] not in NAV]
    return out
