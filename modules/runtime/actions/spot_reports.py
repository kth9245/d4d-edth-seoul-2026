"""RT-17 spot_reports: 순찰 밖 기체가 본 새 적의 발견 카드(결정 0057). 순찰 기체는 순찰 Role의 보고 단계가 올린다.
아직 카드가 없고(reported_by 없음) 아무도 표적으로 삼지 않은 적을 위협 누적 4.5(0043) 넘게 본 기체 이름으로 한 장.
올린 기체는 하던 일 계속(카드를 기다리지 않음). 선택지: 표적용 전환(첫 단계가 표적 operator, 올린 기체 빼고, 기체마다
그 적의 영역을 맡음: 드론은 어디든·수상은 해상·지상은 지상, 0055) → 기지 대기 드론 감시 → 둘 다 없으면 '유지'.
SPEC: modules/runtime/SPEC.md#RT-17
"""

from collections.abc import Sequence

from contracts.models import (  # fmt: skip
    Choice,
    Operation,
    Polygon,
    Report,
    Role,
    Switch,
    Target,
    VehicleSpec,
    VehicleState,
)
from modules.runtime.actions.enter_step import _basis
from modules.runtime.actions.fleet_choices import WATCH_ROLE
from modules.runtime.actions.target_domain import target_domain
from modules.sensing import CARD_ACCUM

LIVE = ("active", "ready")
TARGET_KINDS = ("watch_target", "approach_target")


def _picks(role: Role | None) -> bool:  # its entry step works the target the operator gives
    first = next((s for s in role.steps if s.id == role.entry), None) if role else None
    return bool(first and first.do.kind.value in TARGET_KINDS and first.do.params.get("target") == "operator")  # fmt: skip


def _fits(sw: Switch, me: str, dom: str, roles: dict[str, Role], specs: dict[str, VehicleSpec]) -> bool:  # fmt: skip
    return me not in sw.role_by_vehicle and all(
        _picks(roles.get(r)) and specs[v].domain.value in ("air", dom) for v, r in sw.role_by_vehicle.items()
    )  # fmt: skip


# not in a patrol's find-and-report flow (decision 0036): that step raises its own card, a tick after target_found
def _outside_report_flow(s: VehicleState, roles: dict[str, Role]) -> bool:
    role = roles.get(s.role_id or "")
    step = next((st for st in role.steps if st.id == s.step_id), None) if role else None
    return not (step and (step.report or any(e.cond.kind.value == "target_found" for e in step.on)))


def spot_reports(
    states: list[VehicleState], targets: list[Target], roles: dict[str, Role], op: Operation,
    specs: dict[str, VehicleSpec], land: Sequence[Polygon], t_ms: int,
) -> list[Report]:  # fmt: skip
    worked = {s.target_id for s in states if s.target_id}
    by_id = {s.id: s for s in states}
    out = []
    for t in targets:
        if t.reported_by or t.neutralized_ms or t.id in worked or t.threat_accum < CARD_ACCUM:
            continue
        me = next((by_id[v] for v in t.seen_by if v in by_id and by_id[v].status.value in LIVE
                   and _outside_report_flow(by_id[v], roles)), None)  # fmt: skip
        if me is None:
            continue
        dom = target_domain(t, land)
        switches = [
            Choice(id=f"switch_{sw.id}", label=sw.label, role_by_vehicle=sw.role_by_vehicle,
                   target_by_vehicle={v: t.id for v in sw.role_by_vehicle})
            for sw in op.switches if _fits(sw, me.id, dom, roles, specs)
        ]  # fmt: skip
        standby = [
            Choice(id=f"watch_{s.id}", label=f"{s.id} → {t.id} 감시",
                   role_by_vehicle={s.id: WATCH_ROLE}, target_by_vehicle={s.id: t.id})
            for s in states
            if s.id in op.rotation and s.id != me.id and s.status.value == "ready"
            and s.battery_pct >= 99.9 and s.pending_report_id is None
        ]  # fmt: skip
        keep = [] if switches or standby else [Choice(id="keep", label="전 기체 현 임무 유지")]
        out.append(Report(id=f"rep-{me.id}-{t_ms}-{t.id}", t_ms=t_ms, kind="target_detected", vehicle_id=me.id,
                          target_id=t.id, text="새 적 탐지" + _basis(me, targets, t.id),
                          choices=[*switches, *standby, *keep]))  # fmt: skip
        worked.add(t.id)
    return out
