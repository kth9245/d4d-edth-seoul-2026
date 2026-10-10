"""Exit conditions of a Role step (moved out of step_vehicle.py so the action file stays under 80 lines).
Decision 0036: target_found wants a boat nobody reported yet; 0043: once the threat has built up;
0045: at_time; 0066: target_neutralized; 0070: target_resighted. Pure functions, no state.
"""

from contracts.models import Condition, ConditionKind, Target, VehicleState
from modules.sensing import CARD_ACCUM


def resighted(st: VehicleState, targets: list[Target]) -> Target | None:
    """A site another vehicle already reported that I see now, that is not my own target (decision 0070)."""
    return next(
        (
            tg
            for tg in targets
            if st.id in tg.seen_by
            and tg.reported_by not in (None, st.id)
            and tg.id != st.target_id
            and tg.threat_accum >= CARD_ACCUM
        ),
        None,
    )


def condition_true(
    cond: Condition,
    st: VehicleState,
    targets: list[Target],
    tracking: bool,
    t_ms: int,
    started_ms: int | None,
) -> bool:
    if cond.kind == ConditionKind.target_found:  # decision 0036: tracking my target, else new boat
        if tracking:
            return any(tg.id == st.target_id and st.id in tg.seen_by for tg in targets)
        return any(
            st.id in tg.seen_by and tg.reported_by is None and tg.threat_accum >= CARD_ACCUM
            for tg in targets
        )  # decision 0043: the card goes up once the threat has built up
    if cond.kind == ConditionKind.arrived:
        return st.waypoint_idx < 0
    if cond.kind == ConditionKind.target_neutralized:  # decision 0066: my target has been struck
        return any(tg.id == st.target_id and tg.neutralized_ms is not None for tg in targets)
    if (
        cond.kind == ConditionKind.target_resighted
    ):  # decision 0070: stop at a site another vehicle reported
        return resighted(st, targets) is not None
    if cond.kind == ConditionKind.battery_below:
        return st.battery_pct < float(cond.params.get("pct", 30))
    if cond.kind == ConditionKind.at_time:  # decision 0045: T+ from the operation start
        return started_ms is not None and t_ms - started_ms >= int(cond.params.get("offset_ms", 0))
    return False  # time_elapsed·operator_choice·signal_received: 시연 Role에서 안 씀
