"""RT-21 raid_auto: done_return sends a striker home once its target is down, outside the 24h raid (brute force 10/11)."""

from modules.runtime.actions.raid_auto import done_return
from modules.runtime.tests.test_fleet_choices import ROLES, vs
from modules.runtime.tests.test_raid_choices import RAID, SEA, _role

OTHER = ROLES | {"go_home": _role("go_home", "air"), "strike": _role("strike", "air"),
                 "point_strike": _role("point_strike", "air")}  # fmt: skip


def test_a_striker_whose_target_is_down_goes_home():
    gone = SEA.model_copy(update={"neutralized_ms": 400})
    states = [vs("a1", "point_strike", "s", target="boat1"), vs("d2", "strike", "s", target="boat1"),
              vs("d3", "watch", "watch", target="boat1")]  # fmt: skip
    out = {s.id: s for s in done_return(states, [gone], OTHER)}
    assert out["a1"].role_id == out["d2"].role_id == "go_home" and out["a1"].target_id is None
    assert out["d3"] == states[2]  # a watcher keeps its own rules (decision 0066)


def test_a_live_target_or_the_24h_raid_leaves_it():
    states = [vs("d2", "strike", "s", target="boat1")]
    assert done_return(states, [SEA], OTHER) == states
    gone = SEA.model_copy(update={"neutralized_ms": 400})
    assert (
        done_return(states, [gone], RAID | {"go_home": _role("go_home", "air")}) == states
    )  # 24h asks (RT-20)
