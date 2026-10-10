"""RT-20 raid_idle: a 24h vehicle whose raid job is gone (enemy down, or it cannot follow) is asked home or hold."""

from modules.runtime.actions.raid_idle import raid_idle
from modules.runtime.actions.relief_due import START
from modules.runtime.tests.test_fleet_choices import ROLES, vs
from modules.runtime.tests.test_raid_choices import LAND, RAID, SEA, SPECS, _at, tg

ASHORE = tg("e_ugv1", "ugv", _at(0, 0), 30)


def run(states, targets, reports=(), roles=RAID):
    return raid_idle(list(reports), states, list(targets), SPECS, LAND, roles, 500)


def test_neutralized_target_frees_both_trackers():
    gone = SEA.model_copy(update={"neutralized_ms": 400})
    out = run(
        [vs("d3", "watch", "watch", target="boat1"), vs("usv", "track_sea", "s", target="boat1")],
        [gone],
    )
    assert [r.id for r in out] == ["raid-idle-d3-500", "raid-idle-usv-500"]
    assert out[0].text == "d3: boat1 제거됨, 임무 없음" and out[0].vehicle_id == "d3"
    assert [c.id for c in out[1].choices] == ["home_usv", "hold_usv"]


def test_usv_cannot_follow_ashore_and_ugv_cannot_follow_to_sea():
    out = run([vs("usv", "track_sea", "s", target="e_ugv1"), vs("ugv", "track_ground", "s", target="boat1")],
              [ASHORE, SEA])  # fmt: skip
    assert out[0].text == "usv: 추적 불가: e_ugv1 지상 진입, 수상정은 땅에 못 오름"
    assert out[1].text == "ugv: 추적 불가: boat1 해상 진입, 지상로봇은 바다에 못 들어감"


def test_drone_battery_too_low_to_keep_tracking():
    out = run([vs("d3", "watch", "watch", target="boat1", battery=START - 1)], [SEA])
    assert out[0].text == f"d3: 추적 불가: 배터리 {START - 1:.0f}%"
    assert run([vs("d3", "watch", "watch", target="boat1")], [SEA]) == []


def test_no_new_card_while_one_is_open():
    gone = SEA.model_copy(update={"neutralized_ms": 400})
    states = [vs("d3", "watch", "watch", target="boat1")]
    (first,) = run(states, [gone])
    assert run(states, [gone], reports=[first]) == []


def test_night_operation_gets_nothing():
    gone = SEA.model_copy(update={"neutralized_ms": 400})
    assert run([vs("d3", "watch", "watch", target="boat1")], [gone], roles=ROLES) == []
