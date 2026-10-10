"""RT-03 apply_decision: 운용자 결정 적용 — 선택지 play_by_vehicle대로 기체들을 새 플레이로(사건 2),
target_select 카드면 그 기체의 표적을 정한다. 카드에 resolved_ms·decision_id 기록. 옮긴 기체에는 결정 id·카드 표적(결정 0033).
SPEC: modules/runtime/SPEC.md#RT-03
"""

from contracts.models import ConditionKind, Decision, Play, Report, VehicleState
from modules.runtime.actions.switch_play import switch_play


def apply_decision(
    states: list[VehicleState], plays: dict[str, Play], decision: Decision, reports: list[Report]
) -> tuple[list[VehicleState], list[Report]]:
    rep = next(r for r in reports if r.id == decision.report_id)
    ch = next(c for c in rep.choices if c.id == decision.choice_id)
    done = {"resolved_ms": decision.t_ms, "decision_id": decision.id}
    moved = set(ch.play_by_vehicle)

    def closes(r: Report) -> bool:  # this card, and cards the moved vehicles were waiting on
        return r.id == rep.id or (r.vehicle_id in moved and bool(r.choices) and not r.resolved_ms)

    reports = [r.model_copy(update=done) if closes(r) else r for r in reports]
    out = []
    for s in states:
        if rep.kind == "target_select" and s.id == rep.vehicle_id:
            s = s.model_copy(
                update={"target_id": ch.id, "pending_report_id": None, "entered_step": False}
            )
        elif s.id in moved:  # decision 0033: the strike step needs who approved and what
            s = switch_play(s, plays[ch.play_by_vehicle[s.id]])
            s = s.model_copy(update={"decision_id": decision.id, "target_id": rep.target_id})
        elif s.id == rep.vehicle_id:
            s = s.model_copy(update={"pending_report_id": None, **_choice_exit(s, plays, ch.id)})
        out.append(s)
    return out, reports


def _choice_exit(s: VehicleState, plays: dict[str, Play], choice_id: str) -> dict:
    """Decision 0031: a reporter left out of play_by_vehicle takes its step's operator_choice exit for this choice."""
    play = plays.get(s.play_id or "")
    step = next((st for st in play.steps if st.id == s.step_id), None) if play else None
    for ex in step.on if step else []:
        if (
            ex.cond.kind == ConditionKind.operator_choice
            and ex.cond.params.get("choice") == choice_id
        ):
            return {"step_id": ex.go_step, "entered_step": False}
    return {}
