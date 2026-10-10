import json
from pathlib import Path

import pytest

from modules.role import check_operation
from modules.safety import point_in_polygon
from modules.sim import load_scenario_json
from shared.geo import dist_m
from shared.land import inside, to_sea

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def sc():
    return load_scenario_json(str(ROOT / "demo/scenarios/baengnyeong_strike.json"))


def test_one_drone_starts_on_the_north_search_patrol(sc):
    assert sc.id == "baengnyeong_strike"
    assert sc.operation.assign["d1"] == "site_patrol"
    assert {v for k, v in sc.operation.assign.items() if k != "d1"} == {"standby"}


def test_three_fixed_unknown_sites_and_only_site_a_emits(sc):
    assert [e.id for e in sc.enemies] == ["site_a", "site_b", "site_c"]
    for e in sc.enemies:
        assert (e.kind.value, e.speed_mps, e.role_id) == ("unknown", 0.0, "site_hold")
    assert [e.emit_start_offset_ms for e in sc.enemies] == [0, None, None]


def test_sites_appear_after_the_first_tick(sc):
    # spawn_enemies needs t - dt < start + offset <= t, so an offset of 0 never spawns the enemy
    assert all(e.appear_offset_ms >= sc.tick_ms for e in sc.enemies)


def test_sites_are_inside_the_zone_and_a_strike_boat_can_reach_them(sc):
    for e in sc.enemies:
        assert point_in_polygon(e.pos, sc.operation.zone), e.id
        assert inside(e.pos, sc.land), e.id  # on the island
        assert dist_m(e.pos, to_sea(e.pos, sc.land)) <= 100, (
            e.id
        )  # the USV aims at the nearest sea point


def test_sites_are_within_threat_range_of_the_watch_point(sc):
    wp = sc.watch_points[0]
    for e in sc.enemies:
        assert dist_m(e.pos, wp.pos) <= 3 * wp.radius_m, (
            e.id
        )  # near step, else a silent site never scores 0.40


def test_the_operation_passes_the_role_checks(sc):
    roles, specs = {r.id: r for r in sc.roles}, {v.id: v for v in sc.vehicles}
    assert check_operation(sc.operation, roles, specs).ok


def test_the_reference_point_is_the_target_area_not_the_defended_landing_point(sc):
    night = load_scenario_json(str(ROOT / "demo/scenarios/baengnyeong_night.json"))
    wp, nwp = sc.watch_points[0], night.watch_points[0]
    assert (wp.id, wp.name) == ("target_area", "목표 지역 중심")
    assert (wp.pos, wp.radius_m) == (
        nwp.pos,
        nwp.radius_m,
    )  # same place, so the verified scores hold


def test_the_json_is_what_the_script_builds(sc):
    from scripts.make_strike_scenario import build

    on_disk = json.loads(
        (ROOT / "demo/scenarios/baengnyeong_strike.json").read_text(encoding="utf-8")
    )
    assert build() == on_disk
