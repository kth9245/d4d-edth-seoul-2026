"""PLY-11 check_operation: 작전 전체 검사 — 작전이 기체에 줄 수 있는 모든 (기체, Role)를 모아 Role마다 check_role
모으는 곳: 시작 배정(assign), 예비(reserve: 빠진 기체의 Role), 전환 버튼(switches), Role 보고 선택지(choices).
없는 Role을 가리키면 오류. 예상 귀환 배터리는 기체별로 가장 낮은 값.
SPEC: modules/role/SPEC.md#PLY-11
"""

from contracts.models import Operation, Role, RoleCheck, ValidationIssue, VehicleSpec
from modules.role.actions.check_role import check_role


def _pairs(op: Operation, roles: dict[str, Role]) -> list[tuple[str, str]]:
    out = list(op.assign.items())
    out += [(r, op.assign[v]) for v, rs in op.reserve.items() if v in op.assign for r in rs]
    out += [pair for sw in op.switches for pair in sw.role_by_vehicle.items()]
    choices = [c for p in roles.values() for s in p.steps if s.report for c in s.report.choices]
    return out + [pair for c in choices for pair in c.role_by_vehicle.items()]


def check_operation(
    op: Operation, roles: dict[str, Role], specs: dict[str, VehicleSpec]
) -> RoleCheck:
    pairs = _pairs(op, roles)
    issues = [
        ValidationIssue(code="missing_role", message=f"{v}에 없는 Role: {p}")
        for v, p in pairs
        if p not in roles
    ]
    est: dict[str, float] = {}
    for pid in sorted({p for _, p in pairs if p in roles}):
        recv = {v: pid for v, p in pairs if p == pid}
        chk = check_role(
            roles[pid], op.model_copy(update={"assign": recv, "reserve": {}, "switches": []}), specs
        )
        issues += [i.model_copy(update={"message": f"[{pid}] {i.message}"}) for i in chk.issues]
        for v, b in chk.est_return_battery.items():
            est[v] = min(b, est.get(v, 100.0))
    return RoleCheck(ok=not issues, issues=issues, est_return_battery=est)
