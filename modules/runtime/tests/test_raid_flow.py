"""RT-19 raid_next: the 24h raid asks one question at a time, act → track(+tracker act) → focus → cover → summary."""

from contracts.models import Decision, Report
from modules.runtime.actions.apply_decision import apply_decision
from modules.runtime.actions.raid_cards import idle_choices
from modules.runtime.actions.raid_flow import raid_next
from modules.runtime.tests.test_fleet_choices import ROLES, vs
from modules.runtime.tests.test_raid_choices import LAND, OPX, RAID, SEA, SPECS, _role, tg

DRONE = tg("e_drone", "drone", SEA.pos, 20, threat=90)
STATES = [vs("d1", "coast_a", "report", target="e_drone"), vs("d2", "coast_b", "patrol"),
          vs("d3", None, None, "ready"), vs("d4", None, None, "ready"), vs("usv", None, None, "ready"),
          vs("ugv", None, None, "ready")]  # fmt: skip


def nxt(reports, decisions, states=STATES, targets=(DRONE,), roles=RAID):
    return raid_next(reports, decisions, list(states), list(targets), OPX, roles, SPECS, LAND, 100)


def answer(reports, decisions, rep, cid):
    d = Decision(id=f"dec-{len(decisions)}", t_ms=1, report_id=rep.id, choice_id=cid)
    return [*reports, rep.model_copy(update={"resolved_ms": 1, "decision_id": d.id})], [
        *decisions,
        d,
    ]


def ids(rep) -> list[str]:
    return [c.id for c in rep.choices]


def walk(*cids, states=STATES, targets=(DRONE,)):
    reports, decisions = [], []
    for cid in cids:
        reports, decisions = answer(
            reports, decisions, nxt(reports, decisions, states, targets), cid
        )
    return reports, decisions, nxt(reports, decisions, states, targets)


def test_first_card_asks_finder_strike_or_observe():
    rep = nxt([], [])
    assert rep.id == "raid-e_drone-act" and rep.vehicle_id == "d1" and rep.target_id == "e_drone"
    assert ids(rep) == ["strike_d1", "observe_d1"] and rep.kind == "target_detected"


def test_strike_goes_straight_to_summary():
    *_, rep = walk("strike_d1")
    assert rep.id == "raid-e_drone-done" and rep.kind == "target_neutralized" and rep.choices == []
    assert "e_drone 대응" in rep.text and "격추" in rep.text


def test_track_pick_asks_that_tracker_before_next_pick():
    *_, rep = walk("observe_d1")
    assert rep.id == "raid-e_drone-track-0"
    assert ids(rep) == [
        "track_d2",
        "track_d3",
        "track_d4",
        "track_skip",
        "track_allstay",
    ]  # air: drones only
    assert rep.choices[1].role_by_vehicle == {"d3": "watch"}
    *_, rep = walk("observe_d1", "track_d3")
    assert (
        rep.id == "raid-e_drone-tact-d3"
        and rep.vehicle_id == "d3"
        and ids(rep) == ["strike_d3", "observe_d3"]
    )
    *_, rep = walk("observe_d1", "track_d3", "observe_d3")
    assert rep.id == "raid-e_drone-track-1" and "track_d3" not in ids(rep)


def test_track_skip_moves_to_focus_then_cover_then_summary():
    *_, rep = walk("observe_d1", "track_skip")
    assert rep.id == "raid-e_drone-focus-0" and rep.choices[0].role_by_vehicle == {
        "d2": "focus_orbit"
    }
    *_, rep = walk("observe_d1", "track_skip", "focus_d4", "focus_skip")
    assert rep.id == "raid-e_drone-cover-0" and "cover_d4" not in ids(rep)
    assert rep.choices[0].role_by_vehicle == {"d2": "coast_a"}  # takes over the finder's patrol
    *_, rep = walk(
        "observe_d1",
        "track_d3",
        "observe_d3",
        "track_skip",
        "focus_d4",
        "focus_skip",
        "cover_skip",
    )
    assert rep.id == "raid-e_drone-done" and "d3" in rep.text and "d4" in rep.text


def test_allstay_finishes_tracker_acts_then_summary():
    *_, rep = walk("observe_d1", "track_d3", "observe_d3", "track_allstay")
    assert rep.id == "raid-e_drone-done" and "d3" in rep.text


def test_higher_threat_enemy_first_then_first_seen():
    boat = tg("e_usv", "usv", SEA.pos, 10, seen=("d2",), threat=50)
    assert nxt([], [], targets=(boat, DRONE)).id == "raid-e_drone-act"
    same = DRONE.model_copy(update={"threat": 5.0})
    assert nxt([], [], targets=(same, boat)).id == "raid-e_usv-act"
    reports, decisions, _ = walk("strike_d1", targets=(boat, DRONE))
    reports.append(nxt(reports, decisions, targets=(boat, DRONE)))  # the summary
    assert nxt(reports, decisions, targets=(boat, DRONE)).id == "raid-e_usv-act"


def test_no_card_while_one_is_open():
    assert nxt([nxt([], [])], []) is None


def test_neutralized_mid_flow_jumps_to_summary():
    gone = DRONE.model_copy(update={"neutralized_ms": 5})
    reports, decisions, _ = walk("observe_d1", "track_d3", "observe_d3")
    assert nxt(reports, decisions, targets=(gone,)).id == "raid-e_drone-done"


def test_candidate_moved_elsewhere_drops_from_next_pick():
    moved = [*STATES[:3], vs("d4", "watch", "watch", target="x"), *STATES[4:]]
    *_, rep = walk("observe_d1", states=moved)
    assert "track_d4" not in ids(rep)


def test_night_operation_gets_nothing():
    assert nxt([], [], roles=ROLES) is None


def idle(v):
    return Report(
        id=f"raid-idle-{v}-50",
        t_ms=50,
        kind="target_detected",
        vehicle_id=v,
        text="x",
        choices=idle_choices(v),
    )


def test_an_open_idle_card_does_not_stop_the_flow_and_its_vehicle_is_not_offered():  # review 2, 5
    rep = nxt([idle("d4")], [])
    assert rep.id == "raid-e_drone-act"
    *_, rep = walk("observe_d1")
    assert "track_d4" in ids(rep) and "track_d4" not in ids(
        nxt([idle("d4"), *walk("observe_d1")[0]], walk("observe_d1")[1])
    )


def test_sea_enemy_offers_the_usv_and_not_the_ugv():  # review 3
    boat = tg("e_usv", "usv", SEA.pos, 10, seen=("d2",), threat=50)
    states = [*STATES[:1], vs("d2", "coast_b", "report", target="e_usv"), *STATES[2:]]
    *_, rep = walk("observe_d2", states=states, targets=(boat,))
    assert "track_usv" in ids(rep) and "track_ugv" not in ids(rep)
    assert rep.choices[ids(rep).index("track_usv")].role_by_vehicle == {"usv": "track_sea"}


def test_an_open_pick_card_drops_a_vehicle_moved_elsewhere():  # review 4
    reports, decisions, rep = walk("observe_d1")
    moved = [*STATES[:3], vs("d4", "watch", "watch", target="x"), *STATES[4:]]
    again = nxt([*reports, rep], decisions, states=moved)
    assert again.id == rep.id and "track_d4" not in ids(again) and again.t_ms == rep.t_ms
    assert nxt([*reports, rep], decisions) is None  # nothing changed: no refresh


def test_hold_on_an_idle_card_leaves_the_vehicles_raid_question_open():  # review 1
    roles = RAID | {"standby": _role("standby", "air"), "go_home": _role("go_home", "air")}
    act, card = nxt([], []), idle("d1")
    d = Decision(id="dec-h", t_ms=60, report_id=card.id, choice_id="hold_d1")
    _, reports = apply_decision(STATES, roles, d, [act, card])
    assert reports[0].resolved_ms is None and reports[1].resolved_ms == 60
