"""RT-20 raid_idle: a 24h vehicle whose raid job is gone (enemy down, or it cannot follow) is asked home or hold."""

from modules.runtime.actions.raid_idle import raid_idle
from modules.runtime.actions.relief_due import START
from modules.runtime.tests.test_fleet_choices import ROLES, vs
from modules.runtime.tests.test_raid_choices import LAND, RAID, SEA, SPECS, _at, _role, tg

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


def test_an_idle_vehicle_in_the_air_takes_the_enemy_it_sees():  # user 10/11: the original auto job
    from modules.runtime.actions.raid_idle import auto_watch

    roles = RAID | {"watch": _role("watch", "air")}
    boat = tg("boat1", "usv", SEA.pos, 10, seen=("d2", "d3", "usv", "ugv"))
    states = [vs("d2", "standby", "wait"), vs("d3", "standby", "wait", "ready"), vs("usv", "go_home", "return"),
              vs("ugv", "standby", "wait"), vs("d4", "standby", "wait", battery=25)]  # fmt: skip
    by = {s.id: s for s in auto_watch(states, [boat], SPECS, LAND, roles)}
    assert (by["d2"].role_id, by["d2"].target_id) == ("watch", "boat1")
    assert [by[v] for v in ("d3", "usv", "ugv", "d4")] == states[
        1:
    ]  # at base, taken, wrong domain, battery
    alone = [vs("usv", "go_home", "return")]
    assert auto_watch(alone, [boat], SPECS, LAND, roles)[0].role_id == "track_sea"
    assert (
        auto_watch(alone, [ASHORE.model_copy(update={"seen_by": ["usv"]})], SPECS, LAND, roles)
        == alone
    )
    assert auto_watch(states, [boat], SPECS, LAND, ROLES) == states  # night: untouched
