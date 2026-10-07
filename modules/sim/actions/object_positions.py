"""SIM-02 object_positions: 시각 t_ms의 객체 실제 위치(등속 이동)
SPEC: modules/sim/SPEC.md#SIM-02
"""

from modules.sim.types import Scenario, TruthPoint
from shared.geo import offset_latlon


def object_positions(scenario: Scenario, t_ms: int) -> list[TruthPoint]:
    elapsed_s = (t_ms - scenario.start_ms) / 1000
    points = []
    for o in scenario.objects:
        if elapsed_s < o.appear_s:
            continue
        t = elapsed_s - o.appear_s
        lat, lon = offset_latlon(
            scenario.origin.lat,
            scenario.origin.lon,
            o.start_east_m + o.vel_east_mps * t,
            o.start_north_m + o.vel_north_mps * t,
        )
        points.append(TruthPoint(object_id=o.id, kind=o.kind, lat=lat, lon=lon, alt_m=o.alt_m))
    return points
