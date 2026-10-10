"""RT-14 relief_due: 교대 기체를 지금 보낼지. 기준 배터리(귀환량 2배 빼고 35%)에 닿았거나, 교대 기체가
경로점 m까지 나는 동안 순찰기가 쓸 배터리+5%가 하한선 위 여유 이상이면 보낸다(멀리서 오는 교대도 하한선 전에 인계, 사용자 10/10).
SPEC: modules/runtime/SPEC.md#RT-14
"""

from contracts.models import VehicleSpec, VehicleState
from shared.geo import dist_m

FLOOR = 31.0  # floor 30% + 1 tick slack
START = 35.0  # relief threshold %
SPARE = 7.0  # % spare over the relief flight (user, 10/10: 5% left 1.3% over the floor, 10% relieved the north coast 16% more often)


def _back(st: VehicleState, spec: VehicleSpec) -> float:  # battery % to fly home from here
    return 100 / spec.endurance_min * dist_m(st.pos, spec.home) / spec.speed_mps / 60


def relief_due(st: VehicleState, spec: VehicleSpec, fly_min: float) -> bool:
    back = _back(st, spec)
    late = st.battery_pct - back - FLOOR <= fly_min * 100 / spec.endurance_min + SPARE
    return st.battery_pct - 2 * back <= START or late
