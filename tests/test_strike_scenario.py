import json
from pathlib import Path

import pytest

from contracts.models import Decision, TickInputs
from modules.gateway.engine import init_engine, tick
from modules.role import check_operation
from modules.safety import point_in_polygon
from modules.sim import load_scenario_json
from shared.geo import dist_m
from shared.land import inside, to_sea

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def sc():
    return load_scenario_json(str(ROOT / "demo/scenarios/baengnyeong_strike.json"))


def test_the_fleet_is_one_usv_three_recon_three_attack_and_the_ugv(sc):
    assert [v.id for v in sc.vehicles] == ["usv", "r1", "r2", "r3", "a1", "a2", "a3", "ugv"]
    kinds = {v.id: v.kind for v in sc.vehicles}
    assert kinds == {"usv": "sea_vehicle", "r1": "recon_drone", "r2": "recon_drone",
                     "r3": "recon_drone", "a1": "armed_drone", "a2": "armed_drone",
                     "a3": "armed_drone", "ugv": "ground_robot"}  # fmt: skip
    assert sc.operation.vehicle_ids == [v.id for v in sc.vehicles]


def test_every_drone_starts_and_returns_at_the_usv_spot_on_the_sea(sc):
    by_id = {v.id: v for v in sc.vehicles}
    spot = by_id["usv"].home
    assert (spot.lat, spot.lon) == (37.981, 124.691)
    assert not inside(spot, sc.land)
    for vid in ("r1", "r2", "r3", "a1", "a2", "a3"):
        assert by_id[vid].home == spot, vid


def test_one_recon_drone_starts_on_the_north_search_patrol(sc):
    assert sc.id == "baengnyeong_strike"
    assert sc.operation.assign["r1"] == "site_patrol"
    assert {v for k, v in sc.operation.assign.items() if k != "r1"} == {"standby"}
    assert set(sc.operation.assign) == {v.id for v in sc.vehicles}


def test_no_old_vehicle_id_is_left_in_the_json():
    text = (ROOT / "demo/scenarios/baengnyeong_strike.json").read_text(encoding="utf-8")
    for old in ('"d1"', '"d2"', '"d3"', '"d4"'):
        assert old not in text, old


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


def test_the_strike_role_is_available_to_the_armed_vehicles(sc):
    roles, specs = {r.id: r for r in sc.roles}, {v.id: v for v in sc.vehicles}
    assert "strike" in roles
    armed = [v for v, s in specs.items() if "strike_target" in [c.value for c in s.capabilities]]
    assert set(armed) == {"a1", "a2", "a3"}  # the usv is a carrier now


def _run_until(es, pred, limit=6000):
    for _ in range(limit):
        if pred(es):
            return es
        es, _ = tick(es, TickInputs())
    raise AssertionError("never happened")


def _card(es):
    return next(r for r in es.reports if r.kind == "target_detected" and r.target_id == "site_a")


def _site(es, sid="site_a"):
    return next(t for t in es.targets if t.id == sid)


def test_site_a_is_identified_then_approved_then_neutralized(sc):
    es = init_engine(sc)
    # 1. the RF clue comes first: heard, not yet scanned, so nothing to strike
    es = _run_until(
        es, lambda e: any(t.id == "site_a" and t.ident_state == "rf_only" for t in e.targets)
    )
    # 2. the drone scans it and the confidence climbs; the card never offers a strike before that
    es = _run_until(es, lambda e: any(r.target_id == "site_a" for r in e.reports))
    if _site(es).ident_state != "identified":
        assert not any(c.id.startswith("strike_") for c in _card(es).choices)
    # 3. identified: the three attack drones can be approved, and the card says why
    es = _run_until(es, lambda e: _site(e).ident_state == "identified")
    assert {"strike_a1", "strike_a2", "strike_a3", "strike_all"} <= {
        c.id for c in _card(es).choices
    }
    assert "식별: 식별됨" in _card(es).text
    # 4. the operator approves a1 only; the strike runs through the existing engine path
    dec = Decision(
        id="dec-1", t_ms=es.t_ms + sc.tick_ms, report_id=_card(es).id, choice_id="strike_a1"
    )
    es, _ = tick(es, TickInputs(decisions=[dec]))
    es = _run_until(es, lambda e: _site(e).neutralized_ms is not None, limit=9000)
    assert any(r.kind == "target_neutralized" and r.target_id == "site_a" for r in es.reports)
    assert not es.blocks  # no safety rule stopped it


def test_the_silent_sites_stay_unidentified_without_a_clue(sc):
    es = init_engine(sc)
    for _ in range(1500):  # five simulated minutes
        es, _ = tick(es, TickInputs())
    assert [_site(es, i).ident_state for i in ("site_b", "site_c")] == ["undetected"] * 2
