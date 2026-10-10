import json
from pathlib import Path

import pytest

from contracts.models import Decision, GeoPoint, TickInputs
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
    assert (spot.lat, spot.lon) == (37.955, 124.585)  # the sea west of the island
    assert not inside(spot, sc.land)
    assert point_in_polygon(spot, sc.operation.zone)
    for vid in ("r1", "r2", "r3", "a1", "a2", "a3"):
        assert by_id[vid].home == spot, vid


def test_each_recon_drone_starts_on_its_own_coast_patrol(sc):
    assert sc.id == "baengnyeong_strike"
    patrols = {"r1": "site_patrol_ne", "r2": "site_patrol_nw", "r3": "site_patrol_s"}
    assert {k: v for k, v in sc.operation.assign.items() if k in patrols} == patrols
    assert {v for k, v in sc.operation.assign.items() if k not in patrols} == {"standby"}
    assert set(sc.operation.assign) == {v.id for v in sc.vehicles}
    assert "site_patrol" not in {r.id for r in sc.roles}


def _patrol_points(sc, role_id):
    role = next(r for r in sc.roles if r.id == role_id)
    return [(p["lat"], p["lon"]) for p in role.steps[0].do.params["route"]]


def test_the_three_patrols_cover_the_north_east_north_west_and_south_coast(sc):
    ne, nw, south = (
        _patrol_points(sc, r) for r in ("site_patrol_ne", "site_patrol_nw", "site_patrol_s")
    )
    ne_coast = ne[1:]  # the first point is the sea waypoint checked in its own test
    assert max(lon for _, lon in ne_coast) > 124.75  # east tip
    assert min(lon for _, lon in ne_coast) > 124.68  # and it stays on the east half
    assert min(lon for _, lon in nw) < 124.61 and max(lon for _, lon in nw) < 124.70  # west tip
    assert max(lat for lat, _ in south) < 37.975  # the south coast, no site on it
    for pts in (ne, nw, south):
        assert all(point_in_polygon(GeoPoint(lat=a, lon=b), sc.operation.zone) for a, b in pts)


def test_the_patrol_routes_are_in_the_route_list_for_the_editor(sc):
    ids = [r.id for r in sc.routes]
    assert {"site_ne", "site_nw", "site_s"} <= set(ids) and "coast_a" not in ids


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


def test_a_silent_site_seen_by_one_drone_never_reaches_identified(sc):
    es = init_engine(sc)
    for _ in range(7500):  # 25 simulated minutes: r2 meets site_c, r3 meets site_b
        es, _ = tick(es, TickInputs())
    states = [_site(es, i).ident_state for i in ("site_b", "site_c")]
    assert all(s in ("identifying", "rf_only", "undetected") for s in states), states
    assert "identifying" in states  # but they were seen


def _identified_card_state(sc):
    es = init_engine(sc)
    return _run_until(  # the card appears a little after the identification
        es,
        lambda e: (
            any(t.id == "site_a" and t.ident_state == "identified" for t in e.targets)
            and any(r.kind == "target_detected" and r.target_id == "site_a" for r in e.reports)
        ),
    )


def test_the_card_offers_exactly_the_three_attack_drones_and_not_the_usv(sc):
    es = _identified_card_state(sc)
    ids = [c.id for c in _card(es).choices if c.id.startswith("strike_")]
    assert ids == ["strike_a1", "strike_a2", "strike_a3", "strike_all"]  # no strike_usv


def test_only_the_chosen_attack_drone_flies_to_the_site(sc):
    es = _identified_card_state(sc)
    dec = Decision(
        id="dec-1", t_ms=es.t_ms + sc.tick_ms, report_id=_card(es).id, choice_id="strike_a2"
    )
    es, _ = tick(es, TickInputs(decisions=[dec]))
    es = _run_until(es, lambda e: _site(e).neutralized_ms is not None, limit=9000)
    states = {s.id: s for s in es.states}
    home = next(v for v in sc.vehicles if v.id == "usv").home
    assert states["a2"].role_id == "strike"
    for idle in ("a1", "a3"):
        assert states[idle].role_id == "standby", idle
        assert dist_m(states[idle].pos, home) < 1.0, idle  # still at the usv spot
    assert not es.blocks  # no safety rule (zone, battery, provenance) stopped the strike


def test_the_north_east_patrol_starts_over_the_sea_so_it_does_not_cross_site_c(sc):
    first = _patrol_points(sc, "site_patrol_ne")[0]
    assert not inside(GeoPoint(lat=first[0], lon=first[1]), sc.land)  # a waypoint on the sea
    site_c = next(e for e in sc.enemies if e.id == "site_c").pos
    assert dist_m(GeoPoint(lat=first[0], lon=first[1]), site_c) > 2000


PATROL_OF = {"r1": "site_patrol_ne", "r2": "site_patrol_nw", "r3": "site_patrol_s"}
ROUTE_OF = {"site_patrol_ne": "site_ne", "site_patrol_nw": "site_nw", "site_patrol_s": "site_s"}


def test_every_patrol_card_lets_its_drone_leave_the_site_for_any_stretch(sc):
    roles = {r.id: r for r in sc.roles}
    for drone, role_id in PATROL_OF.items():
        step = roles[role_id].steps[1]
        choices = {c.id: c for c in step.report.choices}
        others = [r for r in PATROL_OF.values() if r != role_id]
        assert set(choices) == {"resume", *(f"go_{ROUTE_OF[o]}" for o in others)}, drone
        assert choices["resume"].role_by_vehicle == {}, drone
        for o in others:
            assert choices[f"go_{ROUTE_OF[o]}"].role_by_vehicle == {drone: o}, drone
        assert any(
            e.cond.kind.value == "operator_choice"
            and e.cond.params == {"choice": "resume"}
            and e.go_step == "patrol"
            for e in step.on
        ), drone


def _site_c_card(sc):
    es = init_engine(sc)
    es = _run_until(
        es,
        lambda e: any(r.kind == "target_detected" and r.target_id == "site_c" for r in e.reports),
    )
    return es, next(
        r for r in es.reports if r.kind == "target_detected" and r.target_id == "site_c"
    )


@pytest.mark.parametrize(
    "choice,role_id",
    [
        ("resume", "site_patrol_nw"),
        ("go_site_ne", "site_patrol_ne"),
        ("go_site_s", "site_patrol_s"),
    ],
)
def test_leaving_a_site_frees_the_drone_and_its_card_does_not_come_back(sc, choice, role_id):
    es, card = _site_c_card(sc)
    assert card.vehicle_id == "r2"  # the north-west stretch meets site_c first
    dec = Decision(id="dec-1", t_ms=es.t_ms + sc.tick_ms, report_id=card.id, choice_id=choice)
    es, _ = tick(es, TickInputs(decisions=[dec]))
    for _ in range(180 * 1000 // sc.tick_ms):  # three minutes
        es, _ = tick(es, TickInputs())
    r2 = next(s for s in es.states if s.id == "r2")
    assert (r2.role_id, r2.step_id) == (role_id, "patrol")
    cards = [r for r in es.reports if r.kind == "target_detected" and r.target_id == "site_c"]
    assert len(cards) == 1 and cards[0].resolved_ms  # answered, and not raised again
    assert dist_m(r2.pos, _site(es, "site_c").pos) > 800  # out of its sensor range: it really left


def test_every_patrol_asks_what_next_once_its_site_is_neutralized(sc):  # decision 0066
    roles = {r.id: r for r in sc.roles}
    for drone, role_id in PATROL_OF.items():
        steps = {s.id: s for s in roles[role_id].steps}
        assert any(
            e.cond.kind.value == "target_neutralized" and e.go_step == "after_strike"
            for e in steps["report"].on
        ), drone
        after = steps["after_strike"]
        choices = {c.id: c for c in after.report.choices}
        assert list(choices) == ["more", "home"], drone
        assert choices["more"].role_by_vehicle == {}, drone
        assert choices["home"].role_by_vehicle == {drone: "go_home"}, drone
        assert any(
            e.cond.kind.value == "operator_choice"
            and e.cond.params == {"choice": "more"}
            and e.go_step == "patrol"
            for e in after.on
        ), drone


def _struck_state(sc):
    """site_a approved for a1 and neutralized; returns the state when r1 asks what next."""
    es = _identified_card_state(sc)
    dec = Decision(
        id="dec-1", t_ms=es.t_ms + sc.tick_ms, report_id=_card(es).id, choice_id="strike_a1"
    )
    es, _ = tick(es, TickInputs(decisions=[dec]))
    es = _run_until(es, lambda e: _site(e).neutralized_ms is not None, limit=9000)
    return _run_until(es, lambda e: _after_strike_card(e) is not None, limit=200)


def _after_strike_card(es):
    return next(
        (
            r
            for r in es.reports
            if r.vehicle_id == "r1" and not r.resolved_ms and r.text.startswith("거점 무력화됨")
        ),
        None,
    )


def _r1(es):
    return next(s for s in es.states if s.id == "r1")


def test_after_the_strike_the_scout_asks_whether_to_scout_more_or_go_home(sc):
    es = _struck_state(sc)
    assert [c.id for c in _after_strike_card(es).choices] == ["more", "home"]
    assert _r1(es).step_id == "after_strike" and _r1(es).pending_report_id


def test_scouting_more_continues_the_stretch_from_where_it_was_left(sc):
    es = _struck_state(sc)
    left = _r1(es).patrol_idx
    assert _r1(es).patrol_step_id == "patrol" and left > 0  # remembered when it found site_a
    dec = Decision(id="dec-2", t_ms=es.t_ms + sc.tick_ms,
                   report_id=_after_strike_card(es).id, choice_id="more")  # fmt: skip
    es, _ = tick(es, TickInputs(decisions=[dec]))
    es, _ = tick(es, TickInputs())
    assert (_r1(es).role_id, _r1(es).step_id) == ("site_patrol_ne", "patrol")
    assert _r1(es).waypoint_idx >= left  # not back at the first waypoint
    for _ in range(60 * 1000 // sc.tick_ms):
        es, _ = tick(es, TickInputs())
    assert _r1(es).pos.lon > 124.69  # still on the east half: a restart would fly back west first


def test_going_home_sends_the_scout_back_to_the_usv_spot(sc):
    es = _struck_state(sc)
    spot = next(v for v in sc.vehicles if v.id == "usv").home
    far = dist_m(_r1(es).pos, spot)
    dec = Decision(id="dec-2", t_ms=es.t_ms + sc.tick_ms,
                   report_id=_after_strike_card(es).id, choice_id="home")  # fmt: skip
    es, _ = tick(es, TickInputs(decisions=[dec]))
    for _ in range(300 * 1000 // sc.tick_ms):  # five minutes
        es, _ = tick(es, TickInputs())
    assert _r1(es).role_id == "go_home"
    assert dist_m(_r1(es).pos, spot) < far - 3000  # it is flying back
