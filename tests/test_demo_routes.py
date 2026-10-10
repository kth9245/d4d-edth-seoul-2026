import json
from pathlib import Path

import pytest

from contracts.models import Scenario
from modules.safety import point_in_polygon

ROOT = Path(__file__).resolve().parent.parent
FILES = ["baengnyeong_night.json", "baengnyeong_24h.json"]
RELATIVE = {"square_300", "zigzag_600", "orbit_200", "north_1km"}


@pytest.mark.parametrize("name", FILES)
def test_demo_routes(name):  # decision 0044
    sc = Scenario.model_validate(json.loads((ROOT / "demo/scenarios" / name).read_text("utf-8")))
    ids = [r.id for r in sc.routes]
    assert len(ids) == len(set(ids)) and len({r.name for r in sc.routes}) == len(ids)
    assert RELATIVE <= set(ids) and "base_to_north" in ids
    for r in sc.routes:
        assert bool(r.points) != bool(r.offsets), r.id  # one kind each
        assert all(point_in_polygon(p, sc.operation.zone) for p in r.points), r.id
    names = {r.name for r in sc.routes}
    for p in sc.roles:  # every patrol card on the demo names a route from the list
        for s in p.steps:
            if s.do.kind.value == "patrol_route" and not p.id.startswith("enemy"):
                assert s.do.params.get("route_name") in names, (p.id, s.id)
