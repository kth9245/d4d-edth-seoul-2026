"""PLY-11 check_operation: 작전 전체 검사 — 작전이 기체에 줄 수 있는 모든 (기체, 플레이)를 모아 플레이마다 check_play
모으는 곳: 시작 배정(assign), 예비(reserve: 빠진 기체의 플레이), 전환 버튼(switches), 플레이 보고 선택지(choices).
없는 플레이를 가리키면 오류. 예상 귀환 배터리는 기체별로 가장 낮은 값.
SPEC: modules/play/SPEC.md#PLY-11
"""

from contracts.models import Operation, Play, PlayCheck, ValidationIssue, VehicleSpec
from modules.play.actions.check_play import check_play


def _pairs(op: Operation, plays: dict[str, Play]) -> list[tuple[str, str]]:
    out = list(op.assign.items())
    out += [(r, op.assign[v]) for v, rs in op.reserve.items() if v in op.assign for r in rs]
    out += [pair for sw in op.switches for pair in sw.play_by_vehicle.items()]
    choices = [c for p in plays.values() for s in p.steps if s.report for c in s.report.choices]
    return out + [pair for c in choices for pair in c.play_by_vehicle.items()]


def check_operation(
    op: Operation, plays: dict[str, Play], specs: dict[str, VehicleSpec]
) -> PlayCheck:
    pairs = _pairs(op, plays)
    issues = [
        ValidationIssue(code="missing_play", message=f"{v}에 없는 플레이: {p}")
        for v, p in pairs
        if p not in plays
    ]
    est: dict[str, float] = {}
    for pid in sorted({p for _, p in pairs if p in plays}):
        recv = {v: pid for v, p in pairs if p == pid}
        chk = check_play(
            plays[pid], op.model_copy(update={"assign": recv, "reserve": {}, "switches": []}), specs
        )
        issues += [i.model_copy(update={"message": f"[{pid}] {i.message}"}) for i in chk.issues]
        for v, b in chk.est_return_battery.items():
            est[v] = min(b, est.get(v, 100.0))
    return PlayCheck(ok=not issues, issues=issues, est_return_battery=est)
