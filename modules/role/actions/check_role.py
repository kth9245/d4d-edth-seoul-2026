"""PLY-06 check_role: Role 하나 검사 — step 연결·보고 지점·작전 구역 + 그 Role을 받는 기체의 영역·능력·귀환 배터리
교대 순찰 Role(op.rotation_roles)는 한 바퀴 배터리 추정을 하지 않는다(도중 교대, 귀환은 rotate_patrols 하한선, 결정 0037).
받는 기체 = op.assign·op.switches에서 이 Role로 가는 기체와 그 예비(op.reserve). 없으면 영역이 맞는 모든 기체로 배터리만 추정.
SPEC: modules/role/SPEC.md#PLY-06
"""

from contracts.models import Operation, Role, RoleCheck, ValidationIssue, VehicleSpec
from modules.role.actions.check_links import check_links
from modules.role.actions.check_report_points import check_report_points
from modules.role.actions.check_return_battery import check_return_battery
from modules.role.actions.check_zone import check_zone


def _receivers(role: Role, op: Operation) -> set[str]:
    ids = {v for v, p in op.assign.items() if p == role.id}
    ids |= {v for sw in op.switches for v, p in sw.role_by_vehicle.items() if p == role.id}
    return ids | {r for v in ids for r in op.reserve.get(v, [])}


def check_role(role: Role, op: Operation, specs: dict[str, VehicleSpec]) -> RoleCheck:
    recv = sorted(_receivers(role, op) & specs.keys())
    issues = check_links(role) + check_report_points(role) + check_zone(role, op)
    for vid in recv:
        sp = specs[vid]
        if sp.domain not in role.domains:
            msg = f"{vid}({sp.domain.value})는 이 Role 영역 밖"
            issues.append(ValidationIssue(code="domain_mismatch", message=msg))
        why = f": {' → '.join(sp.kind_path)} 어디에도 이 능력 없음" if sp.kind_path else ""  # 0038
        issues += [
            ValidationIssue(
                code="missing_capability",
                step_id=s.id,
                message=f"{vid}는 {s.do.kind.value}를 못 함{why}",
            )  # fmt: skip
            for s in role.steps
            if s.do.kind not in sp.capabilities
        ]
    if role.id in op.rotation_roles:  # relieved mid-route; rotate_patrols keeps the floor (0037)
        return RoleCheck(ok=not issues, issues=issues)
    low, est = check_return_battery(role, {v: specs[v] for v in recv} if recv else specs)
    issues += low
    return RoleCheck(ok=not issues, issues=issues, est_return_battery=est)
