"""RT-20 raid_idle: 멸공에서 적 대응 임무가 사라진 기체에 "기지 복귀 / 현재 위치에서 대기" 카드(설계 2026-10-10-24h-raid-flow).
사유: 표적 무력화, USV가 쫓는 적이 땅 위, UGV가 쫓는 적이 바다, 드론 배터리가 지금 돌아가야 할 만큼(relief_due 기준, 편도).
그 기체의 raid-idle 카드가 열려 있으면 새로 만들지 않는다. auto_watch: 공중의 대기·복귀 기체가 본 적을 바로 감시. raid_held: 적 대응으로 빈 순찰은 ④까지 비움(사용자 10/11).
SPEC: modules/runtime/SPEC.md#RT-20"""

from collections.abc import Sequence

from contracts.models import (
    Assignment,
    Operation,
    Polygon,
    Report,
    Role,
    Target,
    VehicleSpec,
    VehicleState,
)
from modules.runtime.actions.raid_cards import TRACK_ROLE, idle_choices
from modules.runtime.actions.relief_due import START, _back
from modules.runtime.actions.switch_role import switch_role
from modules.runtime.actions.target_domain import target_domain

JOBS = ("watch", "track_sea", "track_ground", "focus_orbit", "strike")


def _why(s: VehicleState, tg: Target, spec: VehicleSpec, land: Sequence[Polygon]) -> str | None:
    if tg.neutralized_ms is not None:
        return f"{tg.id} 제거됨, 임무 없음"
    dom, mine = target_domain(tg, land), spec.domain.value
    if mine == "sea" and dom == "ground":
        return f"추적 불가: {tg.id} 지상 진입, 수상정은 땅에 못 오름"
    if mine == "ground" and dom == "sea":
        return f"추적 불가: {tg.id} 해상 진입, 지상로봇은 바다에 못 들어감"
    if mine == "air" and s.battery_pct - _back(s, spec) <= START:
        return f"추적 불가: 배터리 {s.battery_pct:.0f}%"
    return None


def raid_idle(reports: list[Report], states: list[VehicleState], targets: list[Target],
              specs: dict[str, VehicleSpec], land: Sequence[Polygon], roles: dict[str, Role],
              t_ms: int) -> list[Report]:  # fmt: skip
    if "focus_orbit" not in roles:
        return []
    by = {t.id: t for t in targets}
    asked = {r.vehicle_id for r in reports if r.id.startswith("raid-idle-") and not r.resolved_ms}
    out = []
    for s in states:
        tg = by.get(s.target_id or "")
        if s.role_id not in JOBS or tg is None or s.id in asked or s.id not in specs:
            continue
        if why := _why(s, tg, specs[s.id], land):
            out.append(Report(id=f"raid-idle-{s.id}-{t_ms}", t_ms=t_ms, kind="target_detected", vehicle_id=s.id,
                              target_id=None, text=f"{s.id}: {why}", choices=idle_choices(s.id)))  # fmt: skip
    return out


def auto_watch(states: list[VehicleState], targets: list[Target], specs: dict[str, VehicleSpec],
               land: Sequence[Polygon], roles: dict[str, Role]) -> list[VehicleState]:  # fmt: skip
    """24h: an idle vehicle in the air (standby or going home, battery above 30%) that sees an enemy nobody has
    takes it at once, the patrol's own auto job (user 10/11). Drones take any, usv only sea, ugv only ground."""
    if "focus_orbit" not in roles:
        return states
    taken, out = {s.target_id for s in states if s.target_id}, []
    for s in states:
        dom = specs[s.id].domain.value if s.id in specs else None
        tg = next((t for t in targets if s.id in t.seen_by and t.neutralized_ms is None and t.id not in taken
                   and dom in ("air", target_domain(t, land))), None)  # fmt: skip
        if (tg and s.role_id in ("standby", "go_home") and s.status.value in ("active", "returning")
                and s.target_id is None and s.battery_pct > 30):  # fmt: skip
            s = switch_role(s, roles[TRACK_ROLE[dom]]).model_copy(update={"target_id": tg.id, "status": type(s.status).active, "active": None})  # stop the trip home  # fmt: skip
            taken.add(tg.id)
        out.append(s)
    return out


def raid_held(p: str, op: Operation, by: dict[str, VehicleState], assignments: list[Assignment],
              roles: dict[str, Role]) -> bool:  # fmt: skip
    """24h: coast p waits for the ④ cover card while a pool drone is out on a decision or an auto watch (user 10/11)."""
    why = {a.vehicle_id: a.reason for a in assignments}
    return "focus_orbit" in roles and any(by[w].status.value in ("active", "returning") and why.get(w, "").startswith(("결정", "자동 감시")) for w in op.rotation_pools.get(p) or op.rotation if w in by)  # fmt: skip
