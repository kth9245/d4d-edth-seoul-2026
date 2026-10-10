"""Part2-19: the demo scenario on the real tick loop gives the scenes in the strike-phase order
(docs/superpowers/specs/2026-10-10-strike-phase-design.md section 2): s1 s2 s3 s5 s6 s4 s7 s8.

The operator is scripted here: cards answered 20 s after they appear (target picks 10 s, fast1;
strike approval: '함께 타격'), d2 sent past the NLL at 20:00, the block's alternative applied at
20:05, d2 sent to the far south-east corner at 20:30, switch '고속 보트 추적' requested at 23:20
and approved at 24:00.
"""

import pytest

from contracts.models import Decision, DirectControl, GeoPoint, Injection, TickInputs
from modules.gateway.engine import init_engine, tick
from modules.play import check_operation, load_play
from modules.sim import load_scenario_json
from shared.geo import dist_m

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
    if t - START == 23 * MIN + 20_000:
        sw = next(s for s in SC.operation.switches if s.id == "track_fast")
        inj.append(Injection(id="inj-1", t_ms=t, label=sw.label, switch_id=sw.id,
                             play_by_vehicle=sw.play_by_vehicle))  # fmt: skip
    if t - START == 24 * MIN:
        inj += [
            i.model_copy(update={"status": "approved"}) for i in es.injections if i.id == "inj-1"
        ]
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
        mark("s2", sum(a.reason == "결정 dec-1" for a in es.assignments) == 4)
        mark("s3", any(r.kind == "vehicle_gap" for r in es.reports))
        mark("s5", any(b.vehicle_id == "d2" and b.reason == "outside_zone" for b in es.blocks))
        mark(
            "s6",
            any(b.vehicle_id == "d2" and b.reason == "battery_insufficient" for b in es.blocks),
        )
        mark("s4", sum(r.kind == "target_select" for r in es.reports) == 2)
        mark("s7", any(r.text == "타격 승인 요청" for r in es.reports))
        mark("s8", any(t.id == "fast1" and t.neutralized_ms for t in es.targets))
    return es, seen


@pytest.fixture(scope="module")
def scenes(run) -> dict[str, int]:
    return run[1]


def test_scenes_happen_in_strike_phase_order(scenes):
    order = ["s1", "s2", "s3", "s5", "s6", "s4", "s7", "s8"]
    assert [s for s in order if s in scenes] == order, scenes
    assert [scenes[s] for s in order] == sorted(scenes[s] for s in order), scenes


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


def test_operation_passes_play_checks_including_reserve_return_battery():
    plays, specs = {p.id: p for p in SC.plays}, {v.id: v for v in SC.vehicles}
    assert check_operation(SC.operation, plays, specs).ok


# Part1-19 (spec section 5 and 10.1): the structure; the numbers are tuned in Part2-19.


def test_boat1_and_fast1_are_enemies_not_script_events():
    assert {e.id: e.from_enemy for e in SC.enemies} == {"boat1": None, "fast1": "boat1"}
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
    assert fast.play_id == "enemy_fast1"
    assert dist_m(at, fast.pos) > 1000


def test_track_fast_switch_sends_d2_and_usv():
    sw = next(s for s in SC.operation.switches if s.id == "track_fast")
    assert (sw.label, sw.play_by_vehicle) == (
        "고속 보트 추적",
        {"d2": "track_fast", "usv": "track_fast_sea"},
    )


def test_track_plays_ask_strike_approval_with_three_choices():
    plays = {p.id: p for p in SC.plays}
    for pid, mine in (("track_fast", "strike_d2"), ("track_fast_sea", "strike_usv")):
        ask = next(s for s in plays[pid].steps if s.id == "ask")
        assert ask.report.text == "타격 승인 요청"
        assert [c.id for c in ask.report.choices] == [mine, "strike_both"]
    assert plays["strike"].steps[0].do.kind == "strike_target"


def test_demo_play_files_match_scenario_plays():
    for p in SC.plays:
        assert load_play(f"demo/plays/{p.id}.json") == p, p.id


def test_ugv_waits_near_the_shore_where_boat1_stops():
    plays = {p.id: p for p in SC.plays}
    ugv_at = GeoPoint(**plays["landing"].steps[0].do.params["target"])
    boat_at = GeoPoint(**plays["enemy_boat1"].steps[0].do.params["target"])
    assert dist_m(ugv_at, boat_at) < 500
