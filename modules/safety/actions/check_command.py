"""SFT-03 check_command: 하한선 규칙 1(출처)→2(작전 구역)→3(귀환 배터리), 첫 실패에서 Block
PassedCommand는 여기서만 만든다(결정 0003). 대안은 같은 명령의 target만 바꾼 것.
SPEC: modules/safety/SPEC.md#SFT-03
"""

from contracts.models import (
    Block,
    Command,
    CommandKind,
    GeoPoint,
    Injection,
    Operation,
    PassedCommand,
    Role,
    VehicleSpec,
    VehicleState,
)
from modules.safety.actions.point_in_polygon import point_in_polygon
from modules.safety.actions.return_feasible import return_feasible
from shared.geo import lerp, move_toward

RULES = ["no_provenance", "outside_zone", "battery_insufficient"]


def _no_provenance(cmd: Command, roles: dict[str, Role], injections: list[Injection]) -> bool:
    p = cmd.provenance
    if p is None:
        return True
    if cmd.kind == CommandKind.strike and not p.decision_id:  # decision 0033
        return True
    if p.source == "role_step":
        return not roles[p.role_id].approved
    if p.source == "injected_plan":
        return not any(i.id == p.injection_id and i.status == "approved" for i in injections)
    return False


def check_command(
    cmd: Command,
    state: VehicleState,
    spec: VehicleSpec,
    op: Operation,
    roles: dict[str, Role],
    injections: list[Injection],
) -> PassedCommand | Block:
    def block(reason: str, detail: str, alt: GeoPoint | None = None) -> Block:
        new = (
            {"id": cmd.id + "-alt", "params": {**cmd.params, "target": alt.model_dump()}}
            if alt
            else None
        )
        return Block(command_id=cmd.id, vehicle_id=cmd.vehicle_id, reason=reason, detail=detail,
                     alternative=cmd.model_copy(update=new) if new else None, t_ms=state.t_ms)  # fmt: skip

    if _no_provenance(cmd, roles, injections):
        why = "운용자 결정 없는 타격" if cmd.kind == CommandKind.strike else "출처 없음"
        return block("no_provenance", why)
    p = cmd.params
    dests = (
        [GeoPoint(**p["target"])] if "target" in p else [GeoPoint(**q) for q in p.get("route", [])]
    )
    for d in dests:
        if not point_in_polygon(d, op.zone):
            steps = (lerp(state.pos, d, 1 - k / 200) for k in range(1, 201))
            inside = next((c for c in steps if point_in_polygon(c, op.zone)), None)
            alt = move_toward(inside, state.pos, 50) if inside else None
            return block("outside_zone", f"작전 구역 밖({d.lat:.4f}, {d.lon:.4f})", alt)
    if dests:
        ok, alt = return_feasible(state, spec, dests[-1])
        if not ok:
            d = dests[-1]
            return block("battery_insufficient", f"귀환 배터리 부족({d.lat:.4f}, {d.lon:.4f})", alt)
    return PassedCommand(command=cmd, checks=RULES, passed_ms=state.t_ms)
