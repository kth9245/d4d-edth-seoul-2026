import json
from pathlib import Path

import pytest

from contracts.models import Action, GeoPoint, Operation, Play, Polygon, Step
from modules.play.actions.check_zone import check_zone

DEMO = Path(__file__).resolve().parents[3] / "demo"


def P(lat: float, lon: float) -> dict:
    return {"lat": lat, "lon": lon, "alt_m": 0}


ZONE = Polygon(points=[GeoPoint(**P(37.0, 126.0)), GeoPoint(**P(37.0, 126.1)),
                       GeoPoint(**P(37.1, 126.1)), GeoPoint(**P(37.1, 126.0))])  # fmt: skip
OP = Operation(id="op", name="op", area=ZONE, zone=ZONE, vehicle_ids=[])


def play(*actions: Action) -> Play:
    steps = [Step(id=f"s{i}", name="s", do=a) for i, a in enumerate(actions)]
    return Play(id="p", name="p", domains=["air"], steps=steps, entry="s0")


@pytest.mark.parametrize("path", sorted((DEMO / "plays").glob("*.json")), ids=lambda p: p.stem)
def test_demo_plays_stay_in_the_demo_zone(path):
    sc = json.loads((DEMO / "scenarios" / "baengnyeong_night.json").read_text(encoding="utf-8"))
    op = Operation.model_validate(sc["operation"])
    assert check_zone(Play.model_validate_json(path.read_text(encoding="utf-8")), op) == []


def test_destination_outside_the_zone():
    (issue,) = check_zone(
        play(Action(kind="hold"), Action(kind="move_to", params={"target": P(37.2, 126.05)})), OP
    )
    assert (issue.code, issue.step_id) == ("outside_zone", "s1")


def test_each_route_point_outside_is_reported():
    route = [P(37.05, 126.05), P(37.05, 126.2), P(36.9, 126.05)]
    issues = check_zone(play(Action(kind="patrol_route", params={"route": route})), OP)
    assert len(issues) == 2


def test_target_ids_are_not_coordinates():
    p = play(Action(kind="watch_target", params={"target": "nearest"}),
             Action(kind="move_to", params={"target": P(37.05, 126.05)}))  # fmt: skip
    assert check_zone(p, OP) == []
