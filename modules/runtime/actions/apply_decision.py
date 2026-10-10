"""RT-03 apply_decision: 운용자 결정 적용 — 선택지 role_by_vehicle대로 기체들을 새 Role로(사건 2),
target_select 카드면 그 기체의 표적을 정한다. 카드에 resolved_ms·decision_id 기록. 옮긴 기체에는 결정 id·카드 표적(결정 0033).
SPEC: modules/runtime/SPEC.md#RT-03
"""

from contracts.models import ConditionKind, Decision, Report, Role, VehicleState
from modules.runtime.actions.switch_role import switch_role


def apply_decision(
    states: list[VehicleState], roles: dict[str, Role], decision: Decision, reports: list[Report]
) -> tuple[list[VehicleState], list[Report]]:
    rep = next(r for r in reports if r.id == decision.report_id)
    ch = next(c for c in rep.choices if c.id == decision.choice_id)
    done = {"resolved_ms": decision.t_ms, "decision_id": decision.id}
    moved = set(ch.role_by_vehicle)

    def closes(r: Report) -> bool:  # this card, and cards the moved vehicles were waiting on
        waiting = r.vehicle_id in moved and bool(r.choices) and not r.resolved_ms
        return r.id == rep.id or (
            waiting and not r.id.startswith("raid-")
        )  # 24h raid cards stay (RT-19)

    reports = [r.model_copy(update=done) if closes(r) else r for r in reports]
    focused = {
        s.target_id for s in states if s.role_id == "focus_orbit"
    }  # 0055: one drone per spot
    out = []
    for s in states:
        if rep.kind == "target_select" and s.id == rep.vehicle_id:
            s = s.model_copy(
                update={"target_id": ch.id, "pending_report_id": None, "entered_step": False}
            )
        elif s.id in moved:  # decision 0033: the strike step needs who approved and what
            tid = ch.target_by_vehicle.get(s.id, rep.target_id)  # fleet choice: whose target
            if ch.role_by_vehicle[s.id] == "focus_orbit" and tid in focused:
                out.append(s)  # another drone already orbits that spot
                continue
            s = switch_role(s, roles[ch.role_by_vehicle[s.id]])
            s = s.model_copy(update={"decision_id": decision.id, "target_id": tid})
        elif s.id == rep.vehicle_id:
            ex = _choice_exit(s, roles, ch.id)  # an exit taken on this decision carries its id
            s = s.model_copy(
                update={
                    "pending_report_id": None,
                    **ex,
                    **({"decision_id": decision.id} if ex else {}),
                }
            )
        out.append(s)
    return out, reports


def _choice_exit(s: VehicleState, roles: dict[str, Role], choice_id: str) -> dict:
    """Decision 0031: a reporter left out of role_by_vehicle takes its step's operator_choice exit for this choice."""
    role = roles.get(s.role_id or "")
    step = next((st for st in role.steps if st.id == s.step_id), None) if role else None
    for ex in step.on if step else []:
        if (
            ex.cond.kind == ConditionKind.operator_choice
            and ex.cond.params.get("choice") == choice_id
        ):
            return {"step_id": ex.go_step, "entered_step": False}
    return {}
