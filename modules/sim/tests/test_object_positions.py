import math

from modules.sim.actions.object_positions import object_positions
from modules.sim.types import Origin, Scenario, SimObject
from shared.geo import enu_delta_m

ORIGIN = Origin(lat=37.5665, lon=126.978)


def scenario(**kw) -> Scenario:
    obj = SimObject(
        id="d1",
        kind="drone",
        start_east_m=-100,
        start_north_m=50,
        alt_m=100,
        vel_east_mps=10,
        vel_north_mps=0,
        **kw,
    )
    return Scenario(
        name="t", start_ms=1000, duration_s=60, step_ms=500, origin=ORIGIN, objects=[obj]
    )


def test_moves_at_constant_velocity():
    pts = object_positions(scenario(), t_ms=1000 + 5000)
    east, north = enu_delta_m(ORIGIN.lat, ORIGIN.lon, pts[0].lat, pts[0].lon)
    assert math.isclose(east, -50, abs_tol=0.5) and math.isclose(north, 50, abs_tol=0.5)
    assert pts[0].alt_m == 100 and pts[0].kind == "drone"


def test_object_hidden_before_appear():
    assert object_positions(scenario(appear_s=10), t_ms=1000 + 5000) == []
    assert len(object_positions(scenario(appear_s=10), t_ms=1000 + 10000)) == 1
