"""PLY-02 check_links: step 연결 검사 — 없는 step을 가리키는 entry·go_step·비상 step, entry에서 닿지 않는 step
비상 규칙이 가리키는 step은 어디서든 갈 수 있으므로 entry와 함께 출발점으로 본다.
SPEC: modules/play/SPEC.md#PLY-02
"""

from contracts.models import Play, ValidationIssue


def check_links(play: Play) -> list[ValidationIssue]:
    ids = {s.id for s in play.steps}
    em = play.emergency
    roots = [play.entry, em.link_lost_step, em.battery_low_step, em.operator_call_step]
    issues = [
        ValidationIssue(code="missing_step", message=f"없는 step을 가리킴: {r}")
        for r in roots
        if r is not None and r not in ids
    ]
    for s in play.steps:
        issues += [
            ValidationIssue(
                code="missing_step", step_id=s.id, message=f"없는 step으로 감: {e.go_step}"
            )
            for e in s.on
            if e.go_step not in ids
        ]
    nxt = {s.id: [e.go_step for e in s.on] for s in play.steps}
    seen, todo = set(), [r for r in roots if r in ids]
    while todo:
        sid = todo.pop()
        if sid not in seen:
            seen.add(sid)
            todo += [n for n in nxt[sid] if n in ids]
    issues += [
        ValidationIssue(
            code="unreachable_step", step_id=s.id, message=f"entry에서 닿지 않음: {s.id}"
        )
        for s in play.steps
        if s.id not in seen
    ]
    return issues
