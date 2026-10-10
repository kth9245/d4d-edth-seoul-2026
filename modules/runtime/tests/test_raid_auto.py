"""RT-21 raid_auto: done_return sends a striker home once its target is down, outside the 24h raid (brute force 10/11)."""

from contracts.models import Action, Condition, Exit, Role, Step
from modules.runtime.actions.raid_auto import done_return
from modules.runtime.tests.test_fleet_choices import ROLES, vs
from modules.runtime.tests.test_raid_choices import RAID, SEA, _role


def _r(rid: str, *kinds: str, out: bool = False) -> Role:
    on = [Exit(cond=Condition(kind="target_neutralized"), go_step="s1")] if out else []
    steps = [
        Step(id=f"s{i}", name="x", do=Action(kind=k), on=on if i == len(kinds) - 1 else [])
        for i, k in enumerate(kinds)
    ]
    return Role(id=rid, name=rid, domains=["air"], entry="s0", approved=True, steps=steps)


OTHER = ROLES | {"go_home": _role("go_home", "air"), "strike": _r("strike", "strike_target"),
                 "point_strike": _r("point_strike", "strike_target"), "watch": _r("watch", "watch_target"),
                 "patrol_x": _r("patrol_x", "patrol_route", "watch_target"),
                 "recon": _r("recon", "patrol_route", "watch_target", out=True)}  # fmt: skip


def test_a_striker_whose_target_is_down_goes_home():
    gone = SEA.model_copy(update={"neutralized_ms": 400})
    states = [vs("a1", "point_strike", "s0", target="boat1"), vs("d2", "strike", "s0", target="boat1"),
              vs("d3", "watch", "s0", target="boat1"), vs("d4", "patrol_x", "s1", target="boat1"),
              vs("r1", "recon", "s1", target="boat1")]  # fmt: skip
    out = {s.id: s for s in done_return(states, [gone], OTHER)}
    assert (
        out["a1"].role_id == out["d2"].role_id == out["d3"].role_id == "go_home"
        and out["a1"].target_id is None
    )
    assert (out["d4"].role_id, out["d4"].step_id, out["d4"].target_id) == (
        "patrol_x",
        "s0",
        None,
    )  # back on patrol
    assert out["r1"] == states[4]  # its own target_neutralized exit decides (decision 0066)


def test_a_live_target_or_the_24h_raid_leaves_it():
    states = [vs("d2", "strike", "s0", target="boat1")]
    assert done_return(states, [SEA], OTHER) == states
    gone = SEA.model_copy(update={"neutralized_ms": 400})
    assert (
        done_return(states, [gone], RAID | {"go_home": _role("go_home", "air")}) == states
    )  # 24h asks (RT-20)
