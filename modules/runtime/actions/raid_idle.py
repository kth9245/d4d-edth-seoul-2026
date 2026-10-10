"""RT-20 raid_idle: 멸공에서 적 대응 임무가 사라진 기체에 "기지 복귀 / 현재 위치에서 대기" 카드(설계 2026-10-10-24h-raid-flow).
사유: 표적 무력화, USV가 쫓는 적이 땅 위, UGV가 쫓는 적이 바다, 드론 배터리가 지금 돌아가야 할 만큼(relief_due 기준, 편도).
그 기체의 raid-idle 카드가 열려 있으면 새로 만들지 않는다.
SPEC: modules/runtime/SPEC.md#RT-20
"""

from collections.abc import Sequence

from contracts.models import Polygon, Report, Role, Target, VehicleSpec, VehicleState
from modules.runtime.actions.raid_cards import idle_choices
from modules.runtime.actions.relief_due import START, _back
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
