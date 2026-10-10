"""GW-14 decision_applicable: 결정이 가리키는 카드가 있고 그 카드에 그 선택지가 있는지(없으면 엔진이 건너뛴다)
식별을 잃거나 기체가 다른 카드를 쥐면 타격 선택지가 사라지는데, 그 순간 눌린 결정이 apply_decision에 닿으면 StopIteration으로 실행이 멈춘다(검토 지적).
SPEC: modules/gateway/SPEC.md#GW-14
"""

from contracts.models import Decision, Report


def decision_applicable(reports: list[Report], decision: Decision) -> bool:
    rep = next((r for r in reports if r.id == decision.report_id), None)
    return rep is not None and any(c.id == decision.choice_id for c in rep.choices)
