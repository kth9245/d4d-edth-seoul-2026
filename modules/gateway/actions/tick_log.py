"""GW-07 tick_log: 이번 틱의 기록 줄(Frame.log). [대본]은 사건 대본, [계산]은 엔진이 계산한 것(09 4.5)
시각은 KST(결정 0012). 타격 통과·무력화 줄은 결정 0033. 적 등장 줄은 결정 0032.
SPEC: modules/gateway/SPEC.md#GW-07
"""

from datetime import datetime

from contracts.models import Block, CommandKind, PassedCommand, Report, Scenario, TickInputs
from shared.kst import KST


def tick_log(
    scenario: Scenario,
    t_ms: int,
    dt_ms: int,
    inputs: TickInputs,
    blocks: list[Block],
    passed: list[PassedCommand] = (),
    hits: list[Report] = (),
) -> list[str]:
    hhmm = datetime.fromtimestamp(t_ms / 1000, KST).strftime("%H:%M:%S")
    start = scenario.operation.started_ms
    lines = [
        f"[대본] {hhmm} {ev.kind} {ev.params.get('id', '')}"
        for ev in scenario.events
        if t_ms - dt_ms < start + ev.offset_ms <= t_ms
    ]
    lines += [
        f"[대본] {hhmm} 적 등장 {e.id}"
        for e in scenario.enemies
        if t_ms - dt_ms < start + e.appear_offset_ms <= t_ms
    ]
    lines += [f"[계산] {hhmm} 결정 {d.id} → {d.choice_id}" for d in inputs.decisions]
    lines += [f"[계산] {hhmm} 전환 {i.id} {i.status}" for i in inputs.injections]
    lines += [f"[계산] {hhmm} 직접 조종 {d.id} {d.vehicle_id}" for d in inputs.direct]
    lines += [f"[계산] {hhmm} 차단 {b.vehicle_id} {b.reason.value}" for b in blocks]
    lines += [
        f"[계산] {hhmm} 타격 명령 통과: {c.vehicle_id} → {c.params.get('target_id')}, "
        f"운용자 결정 {c.provenance.decision_id} 확인"
        for c in (pc.command for pc in passed)
        if c.kind == CommandKind.strike
    ]
    lines += [f"[계산] {hhmm} {r.text}" for r in hits]
    return lines
