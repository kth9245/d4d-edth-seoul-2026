"""PLY-03 check_report_points: 표적 발견(target_found) 탈출 뒤 운용자 승인 없이 접근하는 경로 찾기
target_found의 go_step부터 따라가며, 선택지 있는 report step을 만나면 그 길은 멈춘다(승인 지점).
그 전에 approach_target step에 닿으면 오류. 접근 step 자신의 report는 명령과 같이 나가므로 승인으로 치지 않는다.
SPEC: modules/role/SPEC.md#PLY-03
"""

from contracts.models import ActionKind, ConditionKind, Role, ValidationIssue


def check_report_points(role: Role) -> list[ValidationIssue]:
    by = {s.id: s for s in role.steps}
    todo = [
        e.go_step for s in role.steps for e in s.on if e.cond.kind == ConditionKind.target_found
    ]
    seen, issues = set(), []
    while todo:
        sid = todo.pop()
        if sid in seen or sid not in by:
            continue
        seen.add(sid)
        s = by[sid]
        if s.do.kind == ActionKind.approach_target:
            msg = f"표적 발견 뒤 선택지 있는 보고 없이 접근: {sid}"
            issues.append(ValidationIssue(code="missing_report_point", step_id=sid, message=msg))
        elif not (s.report and s.report.choices):
            todo += [e.go_step for e in s.on]
    return issues
