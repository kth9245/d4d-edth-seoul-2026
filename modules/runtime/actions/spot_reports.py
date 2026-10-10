"""RT-17 spot_reports: 순찰 밖 기체가 본 새 적의 발견 카드(결정 0057). 순찰 기체는 순찰 Role의 보고 단계가 올린다.
아직 카드가 없고(reported_by 없음) 아무도 표적으로 삼지 않은 적을 위협 누적 4.5(0043) 넘게 본 기체 이름으로 한 장.
올린 기체는 하던 일을 계속한다(카드를 기다리지 않음). 선택지: 작전의 표적용 전환(모든 Role의 첫 단계가 표적을
operator로 받는 전환, 그 적으로 표적을 정함) → 기지 대기 드론마다 'X → 적 감시'. 둘 다 없으면 '전 기체 현 임무 유지'.
SPEC: modules/runtime/SPEC.md#RT-17
"""

from contracts.models import Choice, Operation, Report, Role, Target, VehicleState
from modules.runtime.actions.enter_step import _basis
from modules.runtime.actions.fleet_choices import WATCH_ROLE
from modules.sensing import CARD_ACCUM

LIVE = ("active", "ready")
TARGET_KINDS = ("watch_target", "approach_target")


# its entry step works the target the operator gives (so the card's pick becomes its target)
def _targets_a_pick(role: Role | None) -> bool:
    first = next((s for s in role.steps if s.id == role.entry), None) if role else None
    return bool(
        first
        and first.do.kind.value in TARGET_KINDS
        and first.do.params.get("target") == "operator"
    )


# not in a patrol's find-and-report flow (decision 0036): that step raises its own card, a tick after target_found
def _outside_report_flow(s: VehicleState, roles: dict[str, Role]) -> bool:
    role = roles.get(s.role_id or "")
    step = next((st for st in role.steps if st.id == s.step_id), None) if role else None
    return not (step and (step.report or any(e.cond.kind.value == "target_found" for e in step.on)))


def spot_reports(
    states: list[VehicleState],
    targets: list[Target],
    roles: dict[str, Role],
    op: Operation,
    t_ms: int,
) -> list[Report]:
    worked = {s.target_id for s in states if s.target_id}
    by_id = {s.id: s for s in states}
    out = []
    for t in targets:
        if t.reported_by or t.neutralized_ms or t.id in worked or t.threat_accum < CARD_ACCUM:
            continue
        me = next(
            (
                by_id[v]
                for v in t.seen_by
                if v in by_id
                and by_id[v].status.value in LIVE
                and _outside_report_flow(by_id[v], roles)
            ),
            None,
        )
        if me is None:
            continue
        switches = [
            Choice(id=f"switch_{sw.id}", label=sw.label, role_by_vehicle=sw.role_by_vehicle,
                   target_by_vehicle={v: t.id for v in sw.role_by_vehicle})
            for sw in op.switches
            if all(_targets_a_pick(roles.get(r)) for r in sw.role_by_vehicle.values())
        ]  # fmt: skip
        standby = [
            Choice(id=f"watch_{s.id}", label=f"{s.id} → {t.id} 감시",
                   role_by_vehicle={s.id: WATCH_ROLE}, target_by_vehicle={s.id: t.id})
            for s in states
            if s.id in op.rotation and s.id != me.id and s.status.value == "ready"
            and s.battery_pct >= 99.9 and s.pending_report_id is None
        ]  # fmt: skip
        keep = [] if switches or standby else [Choice(id="keep", label="전 기체 현 임무 유지")]
        out.append(Report(id=f"rep-{me.id}-{t_ms}-s", t_ms=t_ms, kind="target_detected", vehicle_id=me.id,
                          target_id=t.id, text="새 적 탐지" + _basis(me, targets, t.id),
                          choices=[*switches, *standby, *keep]))  # fmt: skip
        worked.add(t.id)
    return out
