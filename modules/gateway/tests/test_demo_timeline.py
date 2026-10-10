"""Part2-19: the demo scenario on the real tick loop gives the scenes in the strike-phase order
(docs/superpowers/specs/2026-10-10-strike-phase-design.md section 2): s1 s2 s3 s5 s6 s4 s7 s8.

The operator is scripted here: cards answered 20 s after they appear (target picks 10 s, fast1;
strike approval: '함께 타격'), d2 sent past the NLL at 20:00, the block's alternative applied at
20:05, d2 sent to the far south-east corner at 20:30. Decision 0057: fast1's card (raised by d3, which keeps
watching boat1) is answered with its first choice, the '고속 보트 추적' switch, so s4 is that card.
"""

import pytest

from contracts.models import Decision, DirectControl, GeoPoint, TickInputs
from modules.gateway.engine import init_engine, tick
from modules.role import check_operation, load_role
from modules.sim import load_scenario_json
from shared.geo import dist_m
from shared.land import inside, to_sea

SC = load_scenario_json("demo/scenarios/baengnyeong_night.json")
START, MIN = SC.operation.started_ms, 60_000
PAST_NLL = GeoPoint(lat=38.05, lon=124.66)  # s5: north of the zone edge (lat 38.0)
FAR_SE = GeoPoint(lat=37.905, lon=124.835)  # s6: inside the zone, beyond d2's return battery


def _pick(r) -> str:
    ids = [c.id for c in r.choices]
    return next((i for i in ("fast1", "strike_both") if i in ids), ids[0])


def _inputs(es, t: int, n: dict) -> TickInputs:
    decs, direct, inj = [], [], []
    for r in es.reports:
        wait = 10_000 if r.kind == "target_select" else 20_000
        if r.choices and not r.resolved_ms and t == r.t_ms + wait:
            n["dec"] += 1
            decs.append(Decision(id=f"dec-{n['dec']}", t_ms=t, report_id=r.id, choice_id=_pick(r)))
    goal = {20 * MIN: PAST_NLL, 20 * MIN + 30_000: FAR_SE}.get(t - START)
    if t - START == 20 * MIN + 5_000 and es.blocks and es.blocks[-1].alternative:
        goal = GeoPoint(**es.blocks[-1].alternative.params["target"])
    if goal:
        n["dir"] += 1
        direct.append(DirectControl(id=f"dir-{n['dir']}", vehicle_id="d2", target=goal, t_ms=t))
    return TickInputs(decisions=decs, direct=direct, injections=inj)


@pytest.fixture(scope="module")
def run():
    es, n, seen = init_engine(SC), {"dec": 0, "dir": 0}, {}

    def mark(scene: str, ok: bool) -> None:
        if ok and scene not in seen:
            seen[scene] = es.t_ms - START

    for _ in range(35 * MIN // SC.tick_ms):
        es, fr = tick(es, _inputs(es, es.t_ms + SC.tick_ms, n))
        mark("s1", any(r.kind == "target_detected" and r.vehicle_id == "d1" for r in es.reports))
        mark("s2", sum(a.reason == "결정 dec-1" for a in es.assignments) == 3)  # d1·usv·ugv (0036)
        mark("s3", any(r.kind == "vehicle_gap" for r in es.reports))
        mark("s5", any(b.vehicle_id == "d2" and b.reason == "outside_zone" for b in es.blocks))
        mark(
            "s6",
            any(b.vehicle_id == "d2" and b.reason == "battery_insufficient" for b in es.blocks),
        )
        mark(
            "s4",
            any(r.target_id == "fast1" and r.text.startswith("새 적 탐지") for r in es.reports),
        )  # 0057
        mark("s7", any(r.text.startswith("타격 승인 요청") for r in es.reports))
        mark("s8", any(t.id == "fast1" and t.neutralized_ms for t in es.targets))
    return es, seen


@pytest.fixture(scope="module")
def scenes(run) -> dict[str, int]:
    return run[1]


def test_scenes_happen_in_strike_phase_order(scenes):
    order = ["s1", "s2", "s3", "s5", "s6", "s4", "s7", "s8"]
    assert [s for s in order if s in scenes] == order, scenes
    assert [scenes[s] for s in order] == sorted(scenes[s] for s in order), scenes


def test_three_boats_each_get_one_card_from_the_drone_that_found_it(run):  # decision 0036
    es, _ = run
    found = [r for r in es.reports if r.kind == "target_detected" and r.text.startswith("미식별")]
    assert [(r.vehicle_id, r.target_id) for r in found] == [
        ("d1", "boat1"), ("d2", "boat2"), ("d2", "boat3"),
    ]  # fmt: skip
    assert found[1].t_ms < found[0].resolved_ms  # two cards open at once
    assert all(r.resolved_ms - START < 20 * MIN for r in found)  # before d2 is sent past the NLL
    # planned choices come first (usv takes boat2 over, d2 keeps boat3), decision 0046
    assert [r.choices[0].id for r in found[1:]] == ["handoff", "keep"]
    extra = {c.id for r in found for c in r.choices[1:]}  # what the fleet choices add
    assert extra and all(i.split("_")[1] in ("d3", "d4") for i in extra)  # only standby drones


def test_fast1_card_comes_from_the_drone_watching_boat1_and_offers_the_track_switch_first(run):
    # decision 0057: a drone that is not patrolling raises the new-enemy card and keeps its own job
    es, _ = run
    (card,) = [r for r in es.reports if r.text.startswith("새 적 탐지")]
    assert (card.vehicle_id, card.target_id, card.choices[0].id) == (
        "d3",
        "fast1",
        "switch_track_fast",
    )
    assert card.choices[0].target_by_vehicle == {"d2": "fast1", "usv": "fast1"}
    assert not [
        r for r in es.reports if r.kind == "target_select"
    ]  # the pick already set the target


def test_alternative_after_zone_block_is_not_blocked(scenes):
    assert scenes["s6"] - scenes["s5"] == 30_000  # only the 20:30 command was blocked after s5


def test_only_the_two_direct_commands_are_blocked_so_strikes_pass_return_battery(run):
    es, _ = run
    assert [(b.vehicle_id, b.reason) for b in es.blocks] == [
        ("d2", "outside_zone"),
        ("d2", "battery_insufficient"),
    ]


def test_strike_ends_in_mission_success(run):
    es, _ = run
    assert es.metrics.mission_success is True
    assert any(r.kind == "target_neutralized" and r.target_id == "fast1" for r in es.reports)


def test_operation_passes_role_checks_including_reserve_return_battery():
    roles, specs = {p.id: p for p in SC.roles}, {v.id: v for v in SC.vehicles}
    assert check_operation(SC.operation, roles, specs).ok


# Part1-19 (spec section 5 and 10.1): the structure; the numbers are tuned in Part2-19.


def test_boat1_and_fast1_are_enemies_not_script_events():
    assert {e.id: e.from_enemy for e in SC.enemies} == {
        "boat1": None, "fast1": "boat1", "boat2": None, "boat3": None,  # decision 0036
    }  # fmt: skip
    assert not [e for e in SC.events if e.kind in ("spawn_target", "split_target")]


def test_fast1_appears_from_boat1_and_moves():
    es, at = init_engine(SC), None
    for _ in range(26 * MIN // SC.tick_ms):
        es, _ = tick(es, TickInputs())
        fast = next((t for t in es.targets if t.id == "fast1"), None)
        if fast and at is None:
            boat = next(t for t in es.targets if t.id == "boat1")
            at = fast.pos
            assert (fast.pos.lat, fast.pos.lon) == pytest.approx((boat.pos.lat, boat.pos.lon))
    assert fast.role_id == "enemy_fast1"
    assert dist_m(at, fast.pos) > 1000


def test_track_fast_switch_sends_d2_and_usv():
    sw = next(s for s in SC.operation.switches if s.id == "track_fast")
    assert (sw.label, sw.role_by_vehicle) == (
        "고속 보트 추적",
        {"d2": "track_fast", "usv": "track_fast_sea"},
    )


def test_track_roles_ask_strike_approval_with_three_choices():
    roles = {p.id: p for p in SC.roles}
    for pid, mine in (("track_fast", "strike_d2"), ("track_fast_sea", "strike_usv")):
        ask = next(s for s in roles[pid].steps if s.id == "ask")
        assert ask.report.text == "타격 승인 요청"
        assert [c.id for c in ask.report.choices] == [mine, "strike_both"]
    assert roles["strike"].steps[0].do.kind == "strike_target"


def test_demo_role_files_match_scenario_roles():
    for p in SC.roles:
        assert load_role(f"demo/roles/{p.id}.json") == p, p.id


def test_ugv_waits_near_the_shore_where_boat1_stops():
    roles = {p.id: p for p in SC.roles}
    ugv_at = GeoPoint(**roles["landing"].steps[0].do.params["target"])
    # boat1's target may be on land; sim stops it at the sea point off that coast (decision 0034)
    boat_at = to_sea(GeoPoint(**roles["enemy_boat1"].steps[0].do.params["target"]), SC.land)
    assert inside(ugv_at, SC.land) and dist_m(ugv_at, boat_at) < 500


def test_fast1_graph_shows_the_decision_behind_the_strikes(run):  # 0038: the last demo beat
    from modules.gateway.actions.build_object_graph import build_object_graph

    es, _ = run
    g = build_object_graph(es, "fast1")
    label = {n.id: n.label for n in g.nodes}
    strikes = {lk.src for lk in g.links
               if lk.rel == "aims_at" and lk.dst == "fast1" and label[lk.src].startswith("strike")}  # fmt: skip
    assert {label[c].split(" · ")[1] for c in strikes} == {"d2", "usv"}
    decs = {lk.dst for lk in g.links if lk.rel == "from_decision" and lk.src in strikes}
    assert len(decs) == 1 and label[next(iter(decs))].endswith("'함께 타격'")
    assert all(label[c].endswith("출처·구역·배터리 통과") for c in strikes)
