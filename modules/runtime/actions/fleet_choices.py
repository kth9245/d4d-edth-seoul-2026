"""RT-11 fleet_choices: 해안 순찰 발견 카드의 선택지를 그때 함대 상황으로 만든다(사용자 지시, 드론만)
발견한 드론은 표적 위에서 감시(호버링)를 계속한다. 다른 교대 드론마다 "발생 지역 순찰"(발견한 드론이 비운 해안)과
"감시 중인 드론 Y와 함께 감시"(Y마다, 표적은 target_by_vehicle), 그리고 "전 기체 현 임무 유지".
step.report.auto_choices가 아닌 카드는 그대로 돌려준다.
SPEC: modules/runtime/SPEC.md#RT-11
"""

from contracts.models import Choice, Operation, Play, Report, VehicleState

WATCH_PLAY = "watch"


def _step(s: VehicleState, plays: dict[str, Play]):
    play = plays.get(s.play_id or "")
    return next((st for st in play.steps if st.id == s.step_id), None) if play else None


def watching(s: VehicleState, plays: dict[str, Play]) -> bool:  # hovering over its target
    step = _step(s, plays)
    return bool(s.target_id and step and step.do.kind.value == "watch_target")


def fleet_choices(
    rep: Report, states: list[VehicleState], op: Operation, plays: dict[str, Play]
) -> Report:
    me = next((s for s in states if s.id == rep.vehicle_id), None)
    step = _step(me, plays) if me else None
    if not (step and step.report and step.report.auto_choices):
        return rep
    coast = plays[me.play_id]
    crew = [s for s in states if s.id in op.rotation]
    hover = [s for s in crew if s.status.value == "active" and watching(s, plays)]
    hover = [me, *(s for s in hover if s.id != me.id)] if me.target_id else hover
    busy = {s.id for s in hover}
    others = [
        s
        for s in crew
        if s.id not in busy
        and s.play_id != coast.id
        and (
            (s.status.value == "active" and s.play_id in op.rotation_plays)
            or (s.status.value == "ready" and s.battery_pct >= 99.9)
        )
    ]
    take = [
        Choice(id=f"take_{x.id}", label=f"{x.id} → 발생 지역 순찰({coast.name})",
               play_by_vehicle={x.id: coast.id})
        for x in others
    ]  # fmt: skip
    join = [
        Choice(id=f"join_{x.id}_{y.id}", label=f"{x.id} → {y.id}와 함께 감시({y.target_id})",
               play_by_vehicle={x.id: WATCH_PLAY}, target_by_vehicle={x.id: y.target_id})
        for x in others
        for y in hover
    ]  # fmt: skip
    keep = Choice(id="keep", label="전 기체 현 임무 유지")
    return rep.model_copy(update={"choices": [*take, *join, keep]})
