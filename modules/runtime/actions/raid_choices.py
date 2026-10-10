"""RT-16 raid_choices: 멸공 적 침투 카드의 동적 선택지(결정 0055, 사용자 10/10).
적기 번호는 누가 봤고 무력화되지 않은 표적을 first_seen_ms 순으로 1부터. 감시(호버링) 중인 드론이 붙은 적기마다
나머지 교대 드론에게 "발견 지점 집중 순찰"(적기당 드론 1대: focus_orbit이 이미 붙은 적기는 빼고),
아군 수상 기체는 해상 적기, 지상 기체는 지상 적기만 "추적"(영역은 target_domain으로 지금 위치에서 판단). 끝에 "대기".
SPEC: modules/runtime/SPEC.md#RT-16
"""

from collections.abc import Sequence

from contracts.models import (
    Choice,
    Operation,
    Polygon,
    Report,
    Role,
    Target,
    VehicleSpec,
    VehicleState,
)
from modules.runtime.actions.target_domain import DOMAIN_LABEL, target_domain

FOCUS = "focus_orbit"
TRACK = {"sea": "track_sea", "ground": "track_ground"}  # own vehicle domain -> role
NEVER = {
    "sea": "ugv",
    "ground": "usv",
}  # a ugv just off the enemy usv is not chased at sea, nor a beached usv


def raid_choices(
    others: list[VehicleState],
    hover: list[VehicleState],
    states: list[VehicleState],
    targets: Sequence[Target],
    land: Sequence[Polygon],
    specs: dict[str, VehicleSpec],
    rotation: list[str],
    spotted: list[str] | None = None,
) -> list[Choice]:
    seen = [t for t in targets if (t.seen_by or t.reported_by) and t.neutralized_ms is None]
    num = {t.id: i + 1 for i, t in enumerate(sorted(seen, key=lambda t: t.first_seen_ms))}
    by = {t.id: t for t in seen}
    spotted = (
        [t for t in spotted if t in num]
        if spotted is not None
        else list(dict.fromkeys(s.target_id for s in hover if s.target_id in num))
    )
    focused = {s.target_id for s in states if s.role_id == FOCUS}
    focus = [
        Choice(id=f"focus_{x.id}_{tid}", label=f"{x.id} → 적기 {num[tid]} 발견 지점 집중 순찰",
               role_by_vehicle={x.id: FOCUS}, target_by_vehicle={x.id: tid})
        for tid in spotted if tid not in focused
        for x in others
    ]  # fmt: skip
    crew = [s for s in states if s.id not in rotation and s.status.value in ("ready", "active")]
    track = [
        Choice(id=f"track_{s.id}_{tid}", label=f"{s.id} → 적기 {num[tid]} 추적({DOMAIN_LABEL[dom]})",
               role_by_vehicle={s.id: TRACK[dom]}, target_by_vehicle={s.id: tid})
        for tid in spotted
        for dom in [target_domain(by[tid], land)]
        for s in crew
        if s.id in specs and specs[s.id].domain.value == dom and s.target_id != tid
        and NEVER.get(dom) != by[tid].kind.value
    ]  # fmt: skip
    return [*focus, *track, Choice(id="stay", label="대기")]


def raid_spot(rep: Report, states: list[VehicleState], op: Operation, roles: dict[str, Role],
              targets: Sequence[Target], land: Sequence[Polygon], specs: dict[str, VehicleSpec]) -> Report:  # fmt: skip
    """A decision 0057 card (raised from outside a patrol, the reporter keeps its job) gets the raid choices for its
    enemy in the 24h operation: full standby drones may focus on it, usv/ugv track it by domain, or stand by."""
    if FOCUS not in roles or not rep.target_id:
        return rep
    standby = [s for s in states if s.id in op.rotation and s.id != rep.vehicle_id and s.status.value == "ready"
               and s.battery_pct >= 99.9 and s.pending_report_id is None]  # fmt: skip
    picks = raid_choices(standby, [], states, targets, land, specs, op.rotation, [rep.target_id])
    return rep.model_copy(update={"choices": picks})
