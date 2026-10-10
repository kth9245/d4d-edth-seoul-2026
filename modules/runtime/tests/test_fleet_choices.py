from contracts.models import (
    Action,
    Choice,
    Condition,
    Exit,
    GeoPoint,
    Operation,
    Play,
    Polygon,
    Report,
    ReportSpec,
    Step,
    VehicleState,
)
from modules.runtime.actions.fleet_choices import fleet_choices

HOME = GeoPoint(lat=37.95, lon=124.70)
SQ = Polygon(points=[GeoPoint(lat=37.9, lon=124.5), GeoPoint(lat=38.1, lon=124.5),
                     GeoPoint(lat=38.1, lon=124.9)])  # fmt: skip
OP = Operation(id="op", name="op", area=SQ, zone=SQ, vehicle_ids=["d1", "d2", "d3", "d4"],
               rotation=["d1", "d2", "d3", "d4"], rotation_plays=["coast_a", "coast_b"],
               rotation_pools={"coast_a": ["d1", "d3"], "coast_b": ["d2", "d4"]})  # fmt: skip


def coast(pid: str, name: str, auto: bool = True) -> Play:
    patrol = Step(id="patrol", name="p", do=Action(kind="patrol_route", params={"route": []}),
                  on=[Exit(cond=Condition(kind="target_found"), go_step="report")])  # fmt: skip
    rep = Step(id="report", name="r", do=Action(kind="watch_target", params={"target": "nearest"}),
               report=ReportSpec(text="미식별 선박 접근", auto_choices=auto))  # fmt: skip
    return Play(
        id=pid, name=name, domains=["air"], steps=[patrol, rep], entry="patrol", approved=True
    )


PLAYS = {
    "coast_a": coast("coast_a", "해안 순찰 A · 북"),
    "coast_b": coast("coast_b", "해안 순찰 B · 남"),
    "watch": Play(id="watch", name="w", domains=["air"], entry="w", approved=True,
                  steps=[Step(id="w", name="w", do=Action(kind="watch_target", params={"target": "operator"}))]),
}  # fmt: skip


def vs(vid, play, step, status="active", target=None, battery=100.0) -> VehicleState:
    return VehicleState(id=vid, t_ms=0, pos=HOME, heading_deg=0, battery_pct=battery, status=status,
                        play_id=play, step_id=step, entered_step=True, target_id=target)  # fmt: skip


CARD = Report(id="rep-d1-1", t_ms=1, kind="target_detected", vehicle_id="d1", target_id="boat1",
              text="미식별 선박 접근")  # fmt: skip


def labels(rep: Report) -> list[str]:
    return [c.id for c in rep.choices]


def test_choices_for_every_other_drone_then_keep():
    states = [vs("d1", "coast_a", "report", target="boat1"), vs("d2", "coast_b", "patrol"),
              vs("d3", None, None, "ready"), vs("d4", "coast_b", "patrol", "returning")]  # fmt: skip
    rep = fleet_choices(CARD, states, OP, PLAYS)
    assert labels(rep) == ["take_d2", "take_d3", "join_d2_d1", "join_d3_d1", "keep"]
    take = rep.choices[0]
    assert take.label == "d2 → 발생 지역 순찰(해안 순찰 A · 북)" and take.play_by_vehicle == {
        "d2": "coast_a"
    }
    join = rep.choices[2]
    assert join.play_by_vehicle == {"d2": "watch"} and join.target_by_vehicle == {"d2": "boat1"}
    assert rep.choices[-1] == Choice(id="keep", label="전 기체 현 임무 유지")


def test_join_lists_every_hovering_drone():
    states = [vs("d1", "coast_a", "report", target="boat1"), vs("d2", "coast_b", "report", target="boat2"),
              vs("d3", None, None, "ready"), vs("d4", None, None, "maintenance", battery=40)]  # fmt: skip
    rep = fleet_choices(CARD, states, OP, PLAYS)
    assert labels(rep) == ["take_d3", "join_d3_d1", "join_d3_d2", "keep"]
    assert rep.choices[2].target_by_vehicle == {"d3": "boat2"}


def test_card_without_auto_choices_is_unchanged():
    plays = {**PLAYS, "coast_a": coast("coast_a", "A", auto=False)}
    states = [vs("d1", "coast_a", "report", target="boat1"), vs("d3", None, None, "ready")]
    assert fleet_choices(CARD, states, OP, plays) == CARD


def static_play(pid: str, name: str) -> Play:  # an old-flow patrol: a card with its own choice
    p = coast(pid, name)
    rep = p.steps[1].model_copy(
        update={
            "report": ReportSpec(
                text="미식별 선박 접근",
                auto_choices=True,
                choices=[Choice(id="approach", label="근접 확인", play_by_vehicle={"d1": "watch"})],
            )
        }
    )
    return p.model_copy(update={"steps": [p.steps[0], rep]})


STATIC_PLAYS = {**PLAYS, "coast_a": static_play("coast_a", "해안 순찰 A")}


def test_planned_choices_stay_first_and_the_fleet_choices_follow_without_keep():
    states = [vs("d1", "coast_a", "report", target="boat1"), vs("d3", None, None, "ready")]
    rep = fleet_choices(CARD, states, OP, STATIC_PLAYS)
    assert labels(rep) == ["approach", "take_d3", "join_d3_d1"]  # no 'keep': the card has its own


def test_choices_are_the_same_when_made_again_for_an_open_card():  # decision 0046: rebuilt every tick
    states = [vs("d1", "coast_a", "report", target="boat1"), vs("d3", None, None, "ready")]
    once = fleet_choices(CARD, states, OP, STATIC_PLAYS)
    assert labels(fleet_choices(once, states, OP, STATIC_PLAYS)) == labels(once)


def test_a_drone_with_its_own_open_card_is_not_asked():  # decision 0046: never drop a card
    states = [vs("d1", "coast_a", "report", target="boat1"), vs("d3", None, None, "ready"),
              vs("d4", None, None, "ready").model_copy(update={"pending_report_id": "rep-d4-1"})]  # fmt: skip
    rep = fleet_choices(CARD, states, OP, STATIC_PLAYS)
    assert labels(rep) == ["approach", "take_d3", "join_d3_d1"]  # nothing for d4
