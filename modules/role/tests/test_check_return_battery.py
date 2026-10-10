import pytest

from contracts.models import Action, GeoPoint, Role, Step, VehicleSpec
from modules.role.actions.check_return_battery import check_return_battery

HOME = GeoPoint(lat=37.0, lon=126.0)


def spec(vid: str, domain: str = "air") -> VehicleSpec:  # 10 m/s for 10 min = 6000 m
    return VehicleSpec(id=vid, name=vid, domain=domain, speed_mps=10, endurance_min=10,
                       sensor_range_m=500, capabilities=[], home=HOME)  # fmt: skip


def north(m: float) -> dict:
    return {"lat": HOME.lat + m / 111_195, "lon": HOME.lon, "alt_m": 0}


def role(*actions: Action) -> Role:
    steps = [Step(id=f"s{i}", name="s", do=a) for i, a in enumerate(actions)]
    return Role(id="p", name="p", domains=["air"], steps=steps, entry="s0")


def test_estimate_from_the_round_trip_length():
    issues, est = check_return_battery(role(Action(kind="move_to", params={"target": north(1000)})),
                                       {"d1": spec("d1")})  # fmt: skip
    assert issues == [] and est["d1"] == pytest.approx(100 - 2000 / 6000 * 100, abs=0.2)


def test_route_points_are_visited_in_order():
    route = [north(500), north(1500)]
    _, est = check_return_battery(role(Action(kind="patrol_route", params={"route": route})),
                                  {"d1": spec("d1")})  # fmt: skip
    assert est["d1"] == pytest.approx(100 - 3000 / 6000 * 100, abs=0.2)


def test_below_30_percent_is_an_error():
    issues, est = check_return_battery(role(Action(kind="move_to", params={"target": north(2500)})),
                                       {"d1": spec("d1")})  # fmt: skip
    assert est["d1"] < 30 and [i.code for i in issues] == ["low_return_battery"]
    assert "d1" in issues[0].message


def test_other_domains_are_skipped_and_no_coordinates_means_full():
    issues, est = check_return_battery(role(Action(kind="watch_target", params={"target": "nearest"})),
                                       {"d1": spec("d1"), "usv": spec("usv", "sea")})  # fmt: skip
    assert issues == [] and est == {"d1": 100.0}
