"""GW-08 check_saved_play: 저장할 플레이 검사: check_play + 그 플레이로 바꾼 작전의 check_operation에서 새로 생긴 오류
check_play만으로는 선택지가 없는 플레이를 가리키는 것, 선택지로 이 플레이를 받는 기체의 영역·능력을 못 잡는다.
작전 전체 검사를 저장 전·후로 돌려 이 저장 때문에 새로 생긴 오류만 더한다(원래 있던 남의 오류로 저장을 막지 않음).
SPEC: modules/gateway/SPEC.md#GW-08
"""

from contracts.models import Play, PlayCheck, Scenario, ValidationIssue
from modules.play import check_operation, check_play


def _key(i: ValidationIssue) -> tuple[str, str | None, str]:
    # check_operation prefixes "[play id] "; strip it so the same issue from both checks matches
    msg = (
        i.message.split("] ", 1)[1]
        if i.message.startswith("[") and "] " in i.message
        else i.message
    )
    return i.code, i.step_id, msg


def check_saved_play(play: Play, scenario: Scenario) -> PlayCheck:
    op, specs = scenario.operation, {v.id: v for v in scenario.vehicles}
    plays = {p.id: p for p in scenario.plays}
    own = check_play(play, op, specs)
    known = {_key(i) for i in own.issues}
    known |= {_key(i) for i in check_operation(op, plays, specs).issues}
    after = check_operation(op, {**plays, play.id: play}, specs).issues
    new = []
    for i in after:
        if _key(i) not in known:
            known.add(_key(i))
            new.append(i)
    issues = own.issues + new
    return PlayCheck(ok=not issues, issues=issues, est_return_battery=own.est_return_battery)
