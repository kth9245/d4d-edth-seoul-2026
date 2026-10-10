from pathlib import Path

import pytest

from contracts.models import Command, PassedCommand, Scenario
from modules.mavlink.actions.mavlink_lines import mavlink_lines

ROOT = Path(__file__).resolve().parents[3]
SC = Scenario.model_validate_json(
    (ROOT / "demo" / "scenarios" / "baengnyeong_night.json").read_text(encoding="utf-8")
)
SPECS = {v.id: v for v in SC.vehicles}
T0 = SC.operation.started_ms  # 21:00:00 KST


def passed(vid, kind, params=None, t_ms=T0 + 70_000):
    cmd = Command(id=f"cmd-{vid}-{t_ms}", vehicle_id=vid, kind=kind, params=params or {})
    return PassedCommand(command=cmd, checks=[], passed_ms=t_ms)


def test_route_becomes_mission_items_then_mission_start():
    route = [{"lat": 37.98, "lon": 124.66, "alt_m": 0}, {"lat": 37.98, "lon": 124.74, "alt_m": 0}]
    assert mavlink_lines([passed("d1", "follow_route", {"route": route})], SPECS) == [
        "21:01:10 d1 MISSION_ITEM_INT seq0 MAV_CMD_NAV_WAYPOINT(16) 0 0 0 0 37.98 124.66 50",
        "21:01:10 d1 MISSION_ITEM_INT seq1 MAV_CMD_NAV_WAYPOINT(16) 0 0 0 0 37.98 124.74 50",
        "21:01:10 d1 COMMAND_LONG MAV_CMD_MISSION_START(300) 0 0 0 0 0 0 0",
    ]


@pytest.mark.parametrize(
    "kind, params, line",
    [
        ("return_home", {}, "21:01:10 usv COMMAND_LONG MAV_CMD_NAV_RETURN_TO_LAUNCH(20) 0 0 0 0 0 0 0"),
        ("keep_distance", {"target_id": "t1", "distance_m": 200},
         "21:01:10 usv COMMAND_LONG MAV_CMD_DO_SET_MODE(176) 1 6 0 0 0 0 0"),  # FOLLOW (Rover)
    ],
)  # fmt: skip
def test_rtl_and_mode_change_are_one_command_long(kind, params, line):
    assert mavlink_lines([passed("usv", kind, params)], SPECS) == [line]


def test_strike_has_no_mavlink_message():
    assert mavlink_lines([passed("d4", "strike", {"target_id": "t1"})], SPECS) == []


def test_lines_follow_the_order_the_commands_passed():
    out = mavlink_lines(
        [
            passed("usv", "return_home", t_ms=T0 + 10_000),
            passed("ugv", "return_home", t_ms=T0 + 20_000),
        ],
        SPECS,
    )
    assert [line[:12] for line in out] == ["21:00:10 usv", "21:00:20 ugv"]
