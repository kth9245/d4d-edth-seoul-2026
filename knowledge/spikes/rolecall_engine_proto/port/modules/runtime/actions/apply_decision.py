"""RT-03 apply_decision: 운용자 결정 적용 — 선택지 play_by_vehicle대로 기체들을 새 플레이로(사건 2),
target_select 카드면 그 기체의 표적을 정한다. 카드에 resolved_ms·decision_id 기록.
SPEC: modules/runtime/SPEC.md#RT-03
"""

from contracts.models import Decision, Play, Report, VehicleState
from modules.runtime.actions.switch_play import switch_play


def apply_decision(
    states: list[VehicleState], plays: dict[str, Play], decision: Decision, reports: list[Report]
) -> tuple[list[VehicleState], list[Report]]:
    rep = next(r for r in reports if r.id == decision.report_id)
    ch = next(c for c in rep.choices if c.id == decision.choice_id)
    done = {"resolved_ms": decision.t_ms, "decision_id": decision.id}
    reports = [r.model_copy(update=done) if r.id == rep.id else r for r in reports]
    out = []
    for s in states:
        if rep.kind == "target_select" and s.id == rep.vehicle_id:
            s = s.model_copy(
                update={"target_id": ch.id, "pending_report_id": None, "entered_step": False}
            )
        elif s.id in ch.play_by_vehicle:
            s = switch_play(s, plays[ch.play_by_vehicle[s.id]])
        elif s.id == rep.vehicle_id:
            s = s.model_copy(update={"pending_report_id": None})
        out.append(s)
    return out, reports
