import py_compile
import sys
import types
from pathlib import Path

import pytest

from contracts.models import Scenario
from modules.mavlink.actions.compile_mavlink import compile_mavlink
from modules.role import load_role

ROOT = Path(__file__).resolve().parents[3]
SC = Scenario.model_validate_json(
    (ROOT / "demo" / "scenarios" / "baengnyeong_night.json").read_text(encoding="utf-8")
)
SPECS = {v.id: v for v in SC.vehicles}
ROLES = {p.stem: load_role(p) for p in (ROOT / "demo" / "roles").glob("*.json")}
WAYPOINT, LOITER_UNLIM, RTL, DO_SET_MODE = 16, 17, 20, 176


def run(role_id, assign):
    op = SC.operation.model_copy(update={"assign": assign})
    return compile_mavlink(ROLES[role_id], op, SPECS)


def commands(plan):
    return [i["command"] for i in plan["mission"]["items"]]


def test_only_vehicles_assigned_this_role_get_a_program():
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
    "role_id, vid, expected",
    [
        ("watch", "d2", [LOITER_UNLIM]),  # watch_target in the air: orbit
        ("go_home", "usv", [RTL]),
        ("approach", "usv", [DO_SET_MODE]),  # approach_target: FOLLOW mode
        ("standby", "ugv", [DO_SET_MODE]),  # hold on the ground: HOLD mode
        ("standby", "d2", [LOITER_UNLIM]),
        ("landing", "ugv", [WAYPOINT]),
    ],
)
def test_entry_step_action_maps_to_the_decision_0011_command(role_id, vid, expected):
    plan, _ = run(role_id, {vid: role_id})[vid]
    assert commands(plan) == expected


def test_follow_mode_number_depends_on_the_vehicle():
    plan, _ = run("approach", {"usv": "approach"})["usv"]
    assert plan["mission"]["items"][0]["params"][:2] == [1, 6]  # rover/boat FOLLOW = 6
    assert plan["mission"]["vehicleType"] == 11


def test_action_the_vehicle_cannot_do_gives_an_empty_mission():
    plan, script = run("approach", {"ugv": "approach"})["ugv"]  # no approach_target on the ground
    assert commands(plan) == [] and "'approach'" in script


@pytest.mark.parametrize("role_id", sorted(ROLES))
def test_every_demo_role_compiles_to_a_valid_python_script(tmp_path, role_id):
    role = ROLES[role_id]
    vid = next(v.id for v in SC.vehicles if v.domain in role.domains)
    _, script = run(role_id, {vid: role_id})[vid]
    path = tmp_path / f"{vid}_{role_id}.py"
    path.write_text(script, encoding="utf-8")
    py_compile.compile(str(path), doraise=True)
    assert "from pymavlink import mavutil" in script
    assert all(repr(s.id) in script for s in role.steps) and f"ENTRY = {role.entry!r}" in script


class _Done(Exception):
    pass


class _Msg:
    def __init__(self, kind, **fields):
        self.kind = kind
        self.__dict__.update(fields)

    def get_type(self):
        return self.kind


class _FakeLink:
    """Stands in for pymavlink's connection: answers each mission upload, then hands out the scripted ground
    signals (STATUSTEXT) one per read and raises _Done when they run out."""

    def __init__(self, signals):
        self.target_system = self.target_component = 1
        self.events = [_Msg("STATUSTEXT", text=t) for t in signals]
        self.upload = []
        self.mav = types.SimpleNamespace(
            mission_count_send=self._count,
            mission_item_int_send=lambda *a: None,
            mission_set_current_send=lambda *a: None,
        )

    def _count(self, _system, _component, n):
        self.upload = [_Msg("MISSION_REQUEST_INT", seq=i) for i in range(n)] + [_Msg("MISSION_ACK")]

    def wait_heartbeat(self):
        pass

    def set_mode_auto(self):
        pass

    def recv_match(self, type, blocking=True, timeout=None):
        wanted = [type] if isinstance(type, str) else type
        if self.upload and self.upload[0].get_type() in wanted:
            return self.upload.pop(0)
        if not self.events:
            raise _Done
        return self.events.pop(0)


def _load_script(role_id, vid, signals, monkeypatch):
    _, script = run(role_id, {vid: role_id})[vid]
    link = _FakeLink(signals)
    fake = types.ModuleType("pymavlink")
    fake.mavutil = types.SimpleNamespace(
        mavlink_connection=lambda _address: link,
        mavlink=types.SimpleNamespace(MAV_FRAME_GLOBAL_RELATIVE_ALT_INT=6),
    )
    monkeypatch.setitem(sys.modules, "pymavlink", fake)
    monkeypatch.setattr(sys, "argv", [f"{vid}_{role_id}.py"])
    ns = {"__name__": f"{vid}_{role_id}"}
    exec(compile(script, f"{vid}_{role_id}.py", "exec"), ns)
    return ns


def _run_script(role_id, vid, signals, monkeypatch, capsys):
    """Runs the generated program until it ends or the signals run out; returns the steps it entered."""
    ns = _load_script(role_id, vid, signals, monkeypatch)
    try:
        ns["main"]()
    except _Done:
        pass
    out = capsys.readouterr().out
    return [line.split(" step ")[1] for line in out.splitlines() if " step " in line], out


def test_choice_that_leaves_the_reporter_in_its_role_takes_that_choice_exit(monkeypatch, capsys):
    # decision 0031: '수상정 인계' sends only usv away, so d2 takes report's operator_choice exit to patrol2
    signals = ["target_found", "choice:handoff", "target_found", "choice:keep"]
    steps, out = _run_script("patrol_b", "d2", signals, monkeypatch, capsys)
    assert steps == ["patrol", "report", "patrol2", "report2", "keep"]
    assert "last step" in out


def test_choice_that_moves_the_vehicle_names_the_role_it_moves_to(monkeypatch, capsys):
    steps, out = _run_script(
        "patrol_a", "d1", ["target_found", "choice:approach"], monkeypatch, capsys
    )
    assert steps == ["patrol", "report"]
    assert "starts role watch" in out  # '근접 확인' sends d1 to watch


def test_operator_choice_exit_is_true_only_for_its_own_choice(monkeypatch):
    exit_true = _load_script("patrol_b", "d2", [], monkeypatch)["exit_true"]
    assert exit_true("operator_choice", {"choice": "keep"}, {"choice": "keep"}, 0, 0)
    assert not exit_true("operator_choice", {"choice": "keep"}, {"choice": "handoff"}, 0, 0)
    assert not exit_true("operator_choice", {"choice": "keep"}, {}, 0, 0)
