"""RT-18 raid_cards: candidates and choices of the 24h step-by-step raid cards (user 10/10)."""

from modules.runtime.actions.raid_cards import (
    act_choices,
    free,
    idle_choices,
    pick_choices,
    trackers,
)
from modules.runtime.tests.test_fleet_choices import OP, vs
from modules.runtime.tests.test_raid_choices import SEA, SPECS, tg


def ids(choices) -> list[str]:
    return [c.id for c in choices]


def test_act_choices_strike_and_observe():
    ch = act_choices("d1", "e_drone")
    assert ids(ch) == ["strike_d1", "observe_d1"]
    assert ch[0].role_by_vehicle == {"d1": "strike"} and ch[0].target_by_vehicle == {
        "d1": "e_drone"
    }
    assert ch[1].role_by_vehicle == {} and "e_drone" in ch[0].label


def test_trackers_skip_seers_and_busy():
    states = [vs("d1", "coast_a", "report"), vs("d2", "watch", "watch", target="x"),
              vs("d3", None, None, "ready").model_copy(update={"pending_report_id": "r"}),
              vs("d4", "coast_b", "patrol"), vs("usv", None, None, "ready"), vs("ugv", None, None, "ready")]  # fmt: skip
    got = trackers(states, SPECS, [SEA], exclude=set())
    assert [s.id for s in got] == ["d4", "usv", "ugv"]
    assert [s.id for s in trackers(states, SPECS, [SEA], exclude={"usv"})] == ["d4", "ugv"]


def test_free_includes_routine_patrol_and_standby():
    states = [vs("d1", "coast_a", "patrol"), vs("d2", "standby", "wait", "ready"), vs("d3", None, None, "ready"),
              vs("d4", "watch", "watch", target="x"), vs("usv", "focus_orbit", "s"), vs("ugv", None, None, "ready")]  # fmt: skip
    assert [s.id for s in free(states, OP, exclude={"ugv"})] == ["d1", "d2", "d3"]


def test_pick_choices_track_has_skip_and_allstay():
    cands = [vs("d3", None, None, "ready"), vs("usv", None, None, "ready")]
    track = pick_choices("track", cands, "e_usv", lambda s: "watch")
    assert ids(track) == ["track_d3", "track_usv", "track_skip", "track_allstay"]
    assert track[0].label == "d3 → e_usv 추적" and track[0].target_by_vehicle == {"d3": "e_usv"}
    assert [c.label for c in track[2:]] == ["선택 기체는 옮기지 않음", "전체 대기"]
    focus = pick_choices("focus", cands, "e_usv", lambda s: "focus_orbit")
    assert ids(focus)[-1] == "focus_skip" and focus[0].label == "d3 → e_usv 발견 지점 집중 순찰"
    assert (
        pick_choices("cover", cands, "e_usv", lambda s: "coast_a")[0].label
        == "d3 → e_usv 발견 지점 대체 순찰"
    )


def test_idle_choices():
    ch = idle_choices("d3")
    assert ids(ch) == ["home_d3", "hold_d3"]
    assert [c.role_by_vehicle for c in ch] == [{"d3": "go_home"}, {"d3": "standby"}]
    assert [c.label for c in ch] == ["d3 → 기지 복귀", "d3 → 현재 위치에서 대기"]


def test_unused_tg_helper_kept():  # sea target fixture shared with RT-16 tests
    assert tg("x", "usv", SEA.pos, 1).seen_by == ["d1"]


def test_track_skip_says_the_picked_vehicles_stay():  # user 10/11: not the same as 전체 대기
    track = pick_choices("track", [vs("d3", None, None, "ready")], "e_usv", lambda s: "watch")
    assert track[-2].label == "선택 기체는 옮기지 않음"
    assert pick_choices("focus", [], "e_usv", lambda s: "focus_orbit")[-1].label == "대기"
