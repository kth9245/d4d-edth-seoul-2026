"""GW-09 mark_reported: 표적 발견 카드가 생기면 그 카드의 표적에 reported_by(카드를 올린 기체) 기록 (결정 0036)
다음 기체의 target_found·"nearest"는 아직 카드가 없는 배를 본다. 처음 올린 기체를 덮어쓰지 않는다.
SPEC: modules/gateway/SPEC.md#GW-09
"""

from contracts.models import Report, Target


def mark_reported(targets: list[Target], new_reports: list[Report]) -> list[Target]:
    by = {
        r.target_id: r.vehicle_id
        for r in reversed(new_reports)
        if r.kind == "target_detected" and r.target_id
    }
    return [
        t.model_copy(update={"reported_by": by[t.id]})
        if t.id in by and t.reported_by is None
        else t
        for t in targets
    ]
