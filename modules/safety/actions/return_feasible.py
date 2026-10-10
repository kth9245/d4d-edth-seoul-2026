"""SFT-02 return_feasible: 목적지까지 + 목적지에서 home까지 시간이 남은 배터리의 80% 안인가
안 되면 현재 위치→목적지 선분을 200등분해 목적지 쪽에서부터 되돌아오며 되는 첫 점을 대안으로.
SPEC: modules/safety/SPEC.md#SFT-02
"""

from contracts.models import GeoPoint, VehicleSpec, VehicleState
from shared.geo import dist_m, lerp


def return_feasible(
    state: VehicleState, spec: VehicleSpec, dest: GeoPoint
) -> tuple[bool, GeoPoint | None]:
    have_s = spec.endurance_min * 60 * state.battery_pct / 100 * 0.8

    def need_s(p: GeoPoint) -> float:
        return (dist_m(state.pos, p) + dist_m(p, spec.home)) / spec.speed_mps

    if need_s(dest) <= have_s:
        return True, None
    for k in range(200):
        cand = lerp(state.pos, dest, 1 - k / 200)
        if need_s(cand) <= have_s:
            return False, cand
    return False, None
