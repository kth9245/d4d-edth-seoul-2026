import py_compile
from pathlib import Path

import pytest

from contracts.models import Scenario
from modules.mavlink.actions.compile_mavlink import compile_mavlink
from modules.play import load_play

ROOT = Path(__file__).resolve().parents[3]
SC = Scenario.model_validate_json(
    (ROOT / "demo" / "scenarios" / "baengnyeong_night.json").read_text(encoding="utf-8")
)
SPECS = {v.id: v for v in SC.vehicles}
PLAYS = {p.stem: load_play(p) for p in (ROOT / "demo" / "plays").glob("*.json")}
WAYPOINT, LOITER_UNLIM, RTL, DO_SET_MODE = 16, 17, 20, 176


def run(play_id, assign):
    op = SC.operation.model_copy(update={"assign": assign})
    return compile_mavlink(PLAYS[play_id], op, SPECS)


def commands(plan):
    return [i["command"] for i in plan["mission"]["items"]]


def test_only_vehicles_assigned_this_play_get_a_program():
    out = run("patrol_a", {"d1": "patrol_a", "d2": "standby", "d3": "patrol_a"})
    assert set(out) == {"d1", "d3"}


def test_patrol_plan_is_a_qgc_plan_of_route_waypoints():
    plan, _ = run("patrol_a", {"d1": "patrol_a"})["d1"]
    assert plan["fileType"] == "Plan" and plan["mission"]["vehicleType"] == 2
    assert plan["mission"]["plannedHomePosition"][:2] == [37.95, 124.7]
    items = plan["mission"]["items"]
    assert commands(plan) == [WAYPOINT, WAYPOINT]
    assert all(isinstance(i["command"], int) and len(i["params"]) == 7 for i in items)
    assert [i["params"][4:6] for i in items] == [[37.98, 124.66], [37.98, 124.74]]
    assert items[0]["params"][6] > 0  # drones fly above the ground


@pytest.mark.parametrize(
    "play_id, vid, expected",
    [
        ("watch", "d2", [LOITER_UNLIM]),  # watch_target in the air: orbit
        ("go_home", "usv", [RTL]),
        ("approach", "usv", [DO_SET_MODE]),  # approach_target: FOLLOW mode
        ("standby", "ugv", [DO_SET_MODE]),  # hold on the ground: HOLD mode
        ("standby", "d2", [LOITER_UNLIM]),
        ("landing", "ugv", [WAYPOINT]),
    ],
)
def test_entry_step_action_maps_to_the_decision_0011_command(play_id, vid, expected):
    plan, _ = run(play_id, {vid: play_id})[vid]
    assert commands(plan) == expected


def test_follow_mode_number_depends_on_the_vehicle():
    plan, _ = run("approach", {"usv": "approach"})["usv"]
    assert plan["mission"]["items"][0]["params"][:2] == [1, 6]  # rover/boat FOLLOW = 6
    assert plan["mission"]["vehicleType"] == 11


def test_action_the_vehicle_cannot_do_gives_an_empty_mission():
    plan, script = run("watch", {"ugv": "watch"})["ugv"]  # no watch_target on the ground
    assert commands(plan) == [] and "'watch'" in script


@pytest.mark.parametrize("play_id", sorted(PLAYS))
def test_every_demo_play_compiles_to_a_valid_python_script(tmp_path, play_id):
    play = PLAYS[play_id]
    vid = next(v.id for v in SC.vehicles if v.domain in play.domains)
    _, script = run(play_id, {vid: play_id})[vid]
    path = tmp_path / f"{vid}_{play_id}.py"
    path.write_text(script, encoding="utf-8")
    py_compile.compile(str(path), doraise=True)
    assert "from pymavlink import mavutil" in script
    assert all(repr(s.id) in script for s in play.steps) and f"ENTRY = {play.entry!r}" in script
