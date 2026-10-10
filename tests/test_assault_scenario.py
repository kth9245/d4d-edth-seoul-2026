import json
from pathlib import Path

import pytest

from contracts.models import GeoPoint
from modules.role import check_operation
from modules.safety import point_in_polygon
from modules.sim import load_scenario_json
from shared.geo import dist_m
from shared.land import inside

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "demo/scenarios/baengnyeong_assault.json"


@pytest.fixture(scope="module")
def sc():
    return load_scenario_json(str(PATH))


def test_fleet_is_six_vehicles_air_sea_ground(sc):
    assert [v.id for v in sc.vehicles] == ["usv", "r1", "r2", "a1", "a2", "ugv"]
    kinds = {v.id: v.kind for v in sc.vehicles}
    assert kinds == {"usv": "armed_usv", "r1": "recon_drone", "r2": "recon_drone",
                     "a1": "armed_drone", "a2": "armed_drone", "ugv": "ground_robot"}  # fmt: skip
    assert sc.operation.vehicle_ids == [v.id for v in sc.vehicles]


def test_every_drone_starts_and_returns_at_the_usv_spot_on_the_sea(sc):
    by_id = {v.id: v for v in sc.vehicles}
    spot = by_id["usv"].home
    assert not inside(spot, sc.land)  # the sea, not on the island
    assert point_in_polygon(spot, sc.operation.zone)
    for vid in ("r1", "r2", "a1", "a2"):
        assert by_id[vid].home == spot, vid


def test_enemies_are_one_unknown_site_one_usv_two_ugv(sc):
    kinds = {e.id: e.kind.value for e in sc.enemies}
    assert kinds == {"site_rf": "unknown", "e_usv": "usv", "e_ugv1": "ugv", "e_ugv2": "ugv"}
    by_id = {e.id: e for e in sc.enemies}
    assert by_id["site_rf"].emit_start_offset_ms == 0  # RF from the start
    assert by_id["site_rf"].speed_mps == 0.0 and by_id["site_rf"].role_id == "site_hold"
    # the two ground robots are dropped by the enemy usv: they spawn at its position
    assert by_id["e_ugv1"].from_enemy == "e_usv" and by_id["e_ugv2"].from_enemy == "e_usv"
    assert by_id["e_usv"].from_enemy is None and by_id["e_usv"].role_id == "enemy_usv_run"
    assert all(e.appear_offset_ms >= sc.tick_ms for e in sc.enemies)  # offset 0 never spawns


def test_no_person_target_anywhere(sc):
    text = PATH.read_text(encoding="utf-8")
    assert '"person"' not in text and "person" not in {e.kind.value for e in sc.enemies}


def test_zone_and_area_match_night_for_the_ai_draft_cache(sc):
    night = load_scenario_json(str(ROOT / "demo/scenarios/baengnyeong_night.json"))
    assert sc.operation.zone == night.operation.zone
    assert sc.operation.area == night.operation.area


def test_site_rf_is_inland_off_the_recon_route_but_in_rf_range(sc):
    site = next(e for e in sc.enemies if e.id == "site_rf").pos
    assert inside(site, sc.land)  # on the island, not a sea point
    assert point_in_polygon(site, sc.operation.zone)
    route = next(r for r in sc.roles if r.id == "site_recon").steps[0].do.params["route"]
    nearest = min(dist_m(GeoPoint(**p), site) for p in route)
    assert 800 < nearest <= 2000  # outside the 800 m camera, inside the 2000 m RF receive


def test_assign_and_roles_and_operation_checks(sc):
    assert sc.id == "baengnyeong_assault" and sc.operation.id == "op_assault"
    assert sc.operation.assign == {"usv": "sea_patrol", "r1": "site_recon", "r2": "site_recon",
                                   "a1": "standby", "a2": "standby", "ugv": "watch_landing"}  # fmt: skip
    ids = {r.id for r in sc.roles}
    assert {"site_recon", "sea_patrol", "watch_landing", "strike", "standby", "go_home",
            "site_hold", "enemy_usv_run", "enemy_hold"} <= ids
    roles, specs = {r.id: r for r in sc.roles}, {v.id: v for v in sc.vehicles}
    assert check_operation(sc.operation, roles, specs).ok


def test_the_json_is_what_the_script_builds():
    from scripts.make_assault_scenario import build
    on_disk = json.loads(PATH.read_text(encoding="utf-8"))
    assert build() == on_disk


# ---- Act 1 acceptance: RF clue -> operator direct control -> identified -> approve -> neutralized ----
from contracts.models import Decision, DirectControl, TickInputs  # noqa: E402
from modules.gateway.engine import init_engine, tick  # noqa: E402


def _run_until(es, pred, limit=12000):
    for _ in range(limit):
        if pred(es):
            return es
        es, _ = tick(es, TickInputs())
    raise AssertionError("never happened")


def _site(es):
    return next((t for t in es.targets if t.id == "site_rf"), None)


def _site_state(es, want):
    s = _site(es)
    return s is not None and s.ident_state == want


def _site_card(es):
    return next((r for r in es.reports
                 if r.kind == "target_detected" and r.target_id == "site_rf"), None)


def test_rf_clue_comes_before_the_drone_sees_the_site(sc):
    es = init_engine(sc)
    es = _run_until(es, lambda e: _site_state(e, "rf_only"))
    assert _site_card(es) is None  # heard on RF, not yet scanned: no card, nothing to strike


def test_operator_direct_sends_a_recon_drone_to_the_off_route_site(sc):
    es = init_engine(sc)
    es = _run_until(es, lambda e: _site_state(e, "rf_only"))
    site = _site(es).pos
    dc = DirectControl(id="dir-1", vehicle_id="r1", t_ms=es.t_ms + sc.tick_ms,
                       target=GeoPoint(lat=site.lat, lon=site.lon, alt_m=0.0))
    es, _ = tick(es, TickInputs(direct=[dc]))
    assert not es.blocks  # the direct order is inside the zone and battery-feasible
    es = _run_until(es, lambda e: _site(e) and "r1" in _site(e).seen_by)  # r1 reaches camera range


def test_site_is_identified_then_approved_then_neutralized(sc):
    es = init_engine(sc)
    es = _run_until(es, lambda e: _site_state(e, "rf_only"))
    site = _site(es).pos
    dc = DirectControl(id="dir-1", vehicle_id="r1", t_ms=es.t_ms + sc.tick_ms,
                       target=GeoPoint(lat=site.lat, lon=site.lon, alt_m=0.0))
    es, _ = tick(es, TickInputs(direct=[dc]))
    # the drone reaches the site, the patrol step raises the card, and identification climbs to identified
    es = _run_until(es, lambda e: _site_card(e) is not None and _site_state(e, "identified"))
    card = _site_card(es)
    assert "식별: 식별됨" in card.text
    assert {"strike_a1", "strike_a2"} <= {c.id for c in card.choices}  # armed drones offered
    dec = Decision(id="dec-1", t_ms=es.t_ms + sc.tick_ms, report_id=card.id, choice_id="strike_a1")
    es, _ = tick(es, TickInputs(decisions=[dec]))
    es = _run_until(es, lambda e: _site(e).neutralized_ms is not None, limit=15000)
    assert any(r.kind == "target_neutralized" and r.target_id == "site_rf" for r in es.reports)
    assert not es.blocks  # no safety rule (provenance, zone, battery) stopped the strike


# ---- Act 2 acceptance: enemy unmanned gear; one decision moves air + sea + ground ----
def _e_usv(es):
    return next((t for t in es.targets if t.id == "e_usv"), None)


def e_usv_down(es):
    t = _e_usv(es)
    return t is not None and t.neutralized_ms is not None


def _sea_card(es):
    return next((r for r in es.reports if r.kind == "target_detected"
                 and r.target_id == "e_usv" and not r.resolved_ms), None)


def test_enemy_usv_spawns_and_drops_two_ground_robots(sc):
    es = init_engine(sc)
    es = _run_until(es, lambda e: _e_usv(e) is not None, limit=20000)
    es = _run_until(es, lambda e: {"e_ugv1", "e_ugv2"} <= {t.id for t in e.targets}, limit=20000)
    ugv1 = next(t for t in es.targets if t.id == "e_ugv1")
    assert ugv1.kind.value == "ugv"  # dropped by the enemy usv (from_enemy)


def test_one_decision_moves_air_sea_and_ground_and_neutralizes_the_enemy_usv(sc):
    es = init_engine(sc)
    es = _run_until(es, lambda e: _sea_card(e) is not None, limit=25000)
    card = _sea_card(es)
    assert any(c.id == "strike_all_domains" for c in card.choices)
    dec = Decision(id="dec-1", t_ms=es.t_ms + sc.tick_ms, report_id=card.id,
                   choice_id="strike_all_domains")
    es, _ = tick(es, TickInputs(decisions=[dec]))
    moved = {s.id: s.role_id for s in es.states}
    assert moved["a1"] == "strike" and moved["a2"] == "strike" and moved["usv"] == "strike"
    assert moved["ugv"] == "watch_landing"  # the ground robot moves on the same decision
    strikers = {s.id: s for s in es.states}
    for vid in ("a1", "a2", "usv"):  # the operator decision id rides each strike command
        assert strikers[vid].decision_id == "dec-1" and strikers[vid].target_id == "e_usv", vid
    es = _run_until(es, e_usv_down, limit=25000)
    assert not es.blocks  # no provenance/zone/battery block on the whole-domain strike


def test_mission_success_when_the_enemy_usv_is_down(sc):
    es = init_engine(sc)
    es = _run_until(es, lambda e: _sea_card(e) is not None, limit=25000)
    card = _sea_card(es)
    dec = Decision(id="dec-1", t_ms=es.t_ms + sc.tick_ms, report_id=card.id,
                   choice_id="strike_all_domains")
    es, _ = tick(es, TickInputs(decisions=[dec]))
    es = _run_until(es, e_usv_down, limit=25000)
    assert es.metrics.mission_success  # a target was neutralized
