"""RT-16 raid_choices: 멸공 적 침투 공용 상수와 결정 0057 카드 처리(결정 0055, 사용자 10/10).
멸공의 발견 카드는 선택지 없는 알림이 되고 질문은 단계별 카드(RT-19 raid_flow)가 한다.
SPEC: modules/runtime/SPEC.md#RT-16
"""

from collections.abc import Sequence

from contracts.models import (
    Operation,
    Polygon,
    Report,
    Role,
    Target,
    VehicleSpec,
    VehicleState,
)

FOCUS = "focus_orbit"
TRACK = {"sea": "track_sea", "ground": "track_ground"}  # own vehicle domain -> role
NEVER = {
    "sea": "ugv",
    "ground": "usv",
}  # a ugv just off the enemy usv is not chased at sea, nor a beached usv


def raid_spot(rep: Report, states: list[VehicleState], op: Operation, roles: dict[str, Role],
              targets: Sequence[Target], land: Sequence[Polygon], specs: dict[str, VehicleSpec]) -> Report:  # fmt: skip
    """A decision 0057 card (raised from outside a patrol, the reporter keeps its job) becomes an alert in the 24h
    operation: the step-by-step raid cards (RT-19) ask about its enemy."""
    if FOCUS not in roles or not rep.target_id:
        return rep
    return rep.model_copy(
        update={"choices": [], "resolved_ms": rep.t_ms}
    )  # the step cards ask (RT-19)


def release(
    states: list[VehicleState], reports: list[Report], roles: dict[str, Role]
) -> list[VehicleState]:
    """24h only: a vehicle still waiting on a card that became a resolved alert goes on with its job (user 10/11)."""
    if FOCUS not in roles:
        return states
    done = {r.id for r in reports if r.resolved_ms and not r.decision_id}
    return [
        s.model_copy(update={"pending_report_id": None}) if s.pending_report_id in done else s
        for s in states
    ]
