"""RT-04 update_metrics: 한 틱의 결과(TickOutcome)로 지표 갱신. 정의는 09 문서 2.3·contracts/API.md 2절
기체 공백: 예비 투입 시각부터 예비가 그 step 목적(감시·접근은 표적 seen_by, 이동·순찰은 waypoint)에 닿을 때까지.
SPEC: modules/runtime/SPEC.md#RT-04
"""

from contracts.models import Metrics, TickOutcome


def _reached(vid: str, out: TickOutcome) -> bool:
    st = next(s for s in out.states if s.id == vid)
    role = out.roles.get(st.role_id)
    step = next((s for s in role.steps if s.id == st.step_id), None) if role else None
    kind = step.do.kind.value if step else None
    if kind in ("watch_target", "approach_target"):
        return any(vid in t.seen_by for t in out.targets)
    if kind in ("move_to", "patrol_route"):
        return st.waypoint_idx < 0 or st.waypoint_idx >= 1
    return st.active is not None


def update_metrics(metrics: Metrics, outcome: TickOutcome) -> Metrics:
    m, inp = metrics.model_copy(), outcome.inputs
    m.operator_actions += len(inp.decisions) + len(inp.direct) + len(inp.injections)
    m.decisions += len(inp.decisions)
    m.commands_sent += len(outcome.passed)
    m.blocked_commands += len(outcome.blocks)
    by_plan = [
        c
        for c in outcome.commands
        if c.provenance and c.provenance.source in ("role_step", "emergency")
    ]
    m.manual_baseline_actions += len(outcome.new_reports) + len(by_plan)
    waiting = sum(1 for r in outcome.reports if r.choices and not r.resolved_ms)
    m.open_reports_max = max(m.open_reports_max, waiting)
    now = outcome.states[0].t_ms if outcome.states else 0
    for a in outcome.assignments:
        if a.reason.startswith("예비 투입") and not _reached(a.vehicle_id, outcome):
            m.vehicle_gap_ms = max(m.vehicle_gap_ms, now - a.since_ms)
    if any(t.neutralized_ms is not None for t in outcome.targets):  # decision 0033
        m.mission_success = True
    return m
