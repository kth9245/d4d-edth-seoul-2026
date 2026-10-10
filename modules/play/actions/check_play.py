"""PLY-06 check_play: 플레이 하나 검사 — step 연결·보고 지점·작전 구역 + 그 플레이를 받는 기체의 영역·능력·귀환 배터리
받는 기체 = op.assign·op.switches에서 이 플레이로 가는 기체와 그 예비(op.reserve). 없으면 영역이 맞는 모든 기체로 배터리만 추정.
SPEC: modules/play/SPEC.md#PLY-06
"""

from contracts.models import Operation, Play, PlayCheck, ValidationIssue, VehicleSpec
from modules.play.actions.check_links import check_links
from modules.play.actions.check_report_points import check_report_points
from modules.play.actions.check_return_battery import check_return_battery
from modules.play.actions.check_zone import check_zone


def _receivers(play: Play, op: Operation) -> set[str]:
    ids = {v for v, p in op.assign.items() if p == play.id}
    ids |= {v for sw in op.switches for v, p in sw.play_by_vehicle.items() if p == play.id}
    return ids | {r for v in ids for r in op.reserve.get(v, [])}


def check_play(play: Play, op: Operation, specs: dict[str, VehicleSpec]) -> PlayCheck:
    recv = sorted(_receivers(play, op) & specs.keys())
    issues = check_links(play) + check_report_points(play) + check_zone(play, op)
    for vid in recv:
        sp = specs[vid]
        if sp.domain not in play.domains:
            msg = f"{vid}({sp.domain.value})는 이 플레이 영역 밖"
            issues.append(ValidationIssue(code="domain_mismatch", message=msg))
        issues += [
            ValidationIssue(
                code="missing_capability",
                step_id=s.id,
                message=f"{vid}는 {s.do.kind.value}를 못 함",
            )  # fmt: skip
            for s in play.steps
            if s.do.kind not in sp.capabilities
        ]
    low, est = check_return_battery(play, {v: specs[v] for v in recv} if recv else specs)
    issues += low
    return PlayCheck(ok=not issues, issues=issues, est_return_battery=est)
