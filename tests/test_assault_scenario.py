import json
from pathlib import Path

import pytest

from contracts.models import DirectControl, GeoPoint, Injection, TickInputs
from modules.gateway.engine import init_engine, tick
from modules.role import check_operation
from modules.safety import point_in_polygon
from modules.sim import load_scenario_json
from shared.geo import dist_m
from shared.land import inside, to_sea

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "demo/scenarios/baengnyeong_assault.json"
SITES = ("site_n", "site_s", "site_f")
BEACH = GeoPoint(lat=37.955, lon=124.625, alt_m=0.0)  # the operator's click just past the west shore


@pytest.fixture(scope="module")
def sc():
    return load_scenario_json(str(PATH))


def _roles(sc):
    return {r.id: r for r in sc.roles}


def _route(sc, role_id, step_id):
    step = next(s for s in _roles(sc)[role_id].steps if s.id == step_id)
    return [GeoPoint(**p) for p in step.do.params["route"]]


# ---- structure (decision 0080) ----
def test_fleet_is_six_vehicles_air_sea_ground(sc):
    assert [v.id for v in sc.vehicles] == ["usv", "r1", "r2", "a1", "a2", "ugv"]
    kinds = {v.id: v.kind for v in sc.vehicles}
    assert kinds == {"usv": "sea_vehicle", "r1": "recon_drone", "r2": "recon_drone",
                     "a1": "armed_drone", "a2": "armed_drone", "ugv": "ground_robot"}  # fmt: skip
    assert sc.operation.vehicle_ids == [v.id for v in sc.vehicles]


def test_only_the_two_attack_drones_can_strike(sc):
    armed = {v.id for v in sc.vehicles if "strike_target" in [c.value for c in v.capabilities]}
    assert armed == {"a1", "a2"}  # the usv lands, it does not strike


def test_drones_and_usv_start_at_sea_and_the_ground_robot_is_already_ashore(sc):
    by = {v.id: v for v in sc.vehicles}
    for vid in ("usv", "r1", "r2", "a1", "a2"):
        assert not inside(by[vid].home, sc.land), vid
        assert point_in_polygon(by[vid].home, sc.operation.zone), vid
    assert inside(by["ugv"].home, sc.land)


def test_enemies_are_three_fixed_silent_unknown_sites_on_land(sc):
    assert [e.id for e in sc.enemies] == list(SITES)
    for e in sc.enemies:
        assert (e.kind.value, e.speed_mps, e.role_id, e.emit_start_offset_ms) == (
            "unknown", 0.0, "site_hold", None)  # fmt: skip
        assert inside(e.pos, sc.land) and point_in_polygon(e.pos, sc.operation.zone), e.id
        assert e.appear_offset_ms >= sc.tick_ms  # an offset of 0 never spawns


def test_no_person_target_anywhere():
    assert '"person"' not in PATH.read_text(encoding="utf-8")


def test_zone_and_area_match_night_for_the_ai_draft_cache(sc):
    night = load_scenario_json(str(ROOT / "demo/scenarios/baengnyeong_night.json"))
    assert sc.operation.zone == night.operation.zone and sc.operation.area == night.operation.area


def test_assign_and_operation_checks(sc):
    assert sc.id == "baengnyeong_assault" and sc.operation.id == "op_assault"
    assert sc.operation.assign == {"usv": "standby", "r1": "recon_r1", "r2": "recon_r2",
                                   "a1": "standby", "a2": "standby", "ugv": "standby"}  # fmt: skip
    assert {"recon_r1", "recon_r2", "strike", "standby", "go_home", "site_hold"} <= set(_roles(sc))
    assert check_operation(sc.operation, _roles(sc), {v.id: v for v in sc.vehicles}).ok


def test_the_two_recon_drones_fly_the_beach_side_by_side(sc):
    r1, r2 = _route(sc, "recon_r1", "formation"), _route(sc, "recon_r2", "formation")
    assert len(r1) == len(r2)
    for a, b in zip(r1, r2):
        assert 300 < dist_m(a, b) < 800  # a formation, not stacked on one point


def test_no_site_is_in_sight_during_the_formation_or_from_the_beach_or_the_ugv(sc):
    form = _route(sc, "recon_r1", "formation") + _route(sc, "recon_r2", "formation")
    ugv = next(v for v in sc.vehicles if v.id == "ugv").home
    shore = to_sea(BEACH, sc.land)
    for e in sc.enemies:
        assert min(dist_m(p, e.pos) for p in form) > 800, e.id  # recon camera
        assert dist_m(shore, e.pos) > 500, e.id  # usv sensor once landed
        assert dist_m(ugv, e.pos) > 300, e.id  # ground robot sensor


def test_each_site_lies_on_its_finders_search_route(sc):
    finders = {"site_n": ("recon_r1", "search_n"), "site_s": ("recon_r2", "search_s"),
               "site_f": ("recon_r1", "search_f")}  # fmt: skip
    by = {e.id: e.pos for e in sc.enemies}
    for site, (role, step) in finders.items():
        assert min(dist_m(p, by[site]) for p in _route(sc, role, step)) < 800, site


def test_every_site_scores_above_the_card_threshold(sc):
    wp = sc.watch_points[0]
    for e in sc.enemies:  # near step +0.15: a silent unknown 0.30 becomes 0.45 >= 0.40
        assert dist_m(e.pos, wp.pos) <= 3 * wp.radius_m, e.id


def test_the_json_is_what_the_script_builds():
    from scripts.make_assault_scenario import build

    assert build() == json.loads(PATH.read_text(encoding="utf-8"))


# ---- acceptance over the real engine ----
def _run_until(es, pred, limit=20000):
    for _ in range(limit):
        if pred(es):
            return es
        es, _ = tick(es, TickInputs())
    raise AssertionError("never happened")


def _st(es, vid):
    return next(s for s in es.states if s.id == vid)


def _tg(es, tid):
    return next((t for t in es.targets if t.id == tid), None)


def _card(es, site, by):
    return next((r for r in es.reports
                 if r.kind == "target_detected" and r.target_id == site and r.vehicle_id == by), None)  # fmt: skip


def _down(es, site):
    t = _tg(es, site)
    return t is not None and t.neutralized_ms is not None


def _point(es, sc, n, vehicle, site):  # the vehicle menu's '표적 타격' (decision 0058): one approved request
    inj = Injection(id=f"inj-{n}", t_ms=es.t_ms + sc.tick_ms, label=f"표적 타격: {vehicle} → {site}",
                    role_by_vehicle={vehicle: "strike"}, target_by_vehicle={vehicle: site},
                    status="approved")  # fmt: skip
    es, _ = tick(es, TickInputs(injections=[inj]))
    return es


def test_the_formation_flies_apart_not_stacked(sc):
    es = init_engine(sc)
    for _ in range(300):  # 60 s in
        es, _ = tick(es, TickInputs())
    assert dist_m(_st(es, "r1").pos, _st(es, "r2").pos) > 300


def test_the_operator_lands_the_usv_on_the_beach_and_it_stays(sc):
    es = init_engine(sc)
    dc = DirectControl(id="dir-1", vehicle_id="usv", t_ms=es.t_ms + sc.tick_ms, target=BEACH)
    es, _ = tick(es, TickInputs(direct=[dc]))
    shore = to_sea(BEACH, sc.land)
    es = _run_until(es, lambda e: dist_m(_st(e, "usv").pos, shore) < 5)
    for _ in range(300):
        es, _ = tick(es, TickInputs())
    assert dist_m(_st(es, "usv").pos, shore) < 5  # hold keeps it on the beach
    assert not es.blocks


def test_r1_finds_the_north_site_and_r2_the_south_one_as_plain_alerts(sc):
    es = init_engine(sc)
    es = _run_until(es, lambda e: _card(e, "site_n", "r1") and _card(e, "site_s", "r2"))
    assert _card(es, "site_f", "r1") is None  # the forest comes later
    for site, by in (("site_n", "r1"), ("site_s", "r2")):
        assert not _card(es, site, by).choices  # an alert: the strike goes through the vehicle menu
    assert _st(es, "r1").target_id == "site_n" and _st(es, "r2").target_id == "site_s"


def test_full_run_the_operator_strikes_three_sites_with_two_drones(sc):
    es = init_engine(sc)
    es = _run_until(es, lambda e: _card(e, "site_n", "r1") and _card(e, "site_s", "r2"))
    es = _point(es, sc, 1, "a1", "site_n")
    es = _point(es, sc, 2, "a2", "site_s")
    es = _run_until(es, lambda e: _down(e, "site_n") and _down(e, "site_s"))
    # r1 goes on to the forest; r2 is done and heads home
    es = _run_until(es, lambda e: _card(e, "site_f", "r1") is not None)
    assert _st(es, "r2").status.value in ("returning", "maintenance")
    es = _point(es, sc, 3, "a1", "site_f")  # a1's second sortie
    es = _run_until(es, lambda e: _down(e, "site_f"))
    assert es.metrics.mission_success
    assert not es.blocks  # cumulative over the run (engine.py: es.blocks + blocks)
