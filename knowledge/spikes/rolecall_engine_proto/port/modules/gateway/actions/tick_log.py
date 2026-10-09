"""GW-07 tick_log: 이번 틱의 기록 줄(Frame.log). [대본]은 사건 대본, [계산]은 엔진이 계산한 것(09 4.5)
시각은 KST(결정 0012).
SPEC: modules/gateway/SPEC.md#GW-07
"""

from datetime import datetime

from contracts.models import Block, Scenario, TickInputs
from shared.kst import KST


def tick_log(
    scenario: Scenario, t_ms: int, dt_ms: int, inputs: TickInputs, blocks: list[Block]
) -> list[str]:
    hhmm = datetime.fromtimestamp(t_ms / 1000, KST).strftime("%H:%M:%S")
    start = scenario.operation.started_ms
    lines = [
        f"[대본] {hhmm} {ev.kind} {ev.params.get('id', '')}"
        for ev in scenario.events
        if t_ms - dt_ms < start + ev.offset_ms <= t_ms
    ]
    lines += [f"[계산] {hhmm} 결정 {d.id} → {d.choice_id}" for d in inputs.decisions]
    lines += [f"[계산] {hhmm} 전환 {i.id} {i.status}" for i in inputs.injections]
    lines += [f"[계산] {hhmm} 직접 조종 {d.id} {d.vehicle_id}" for d in inputs.direct]
    lines += [f"[계산] {hhmm} 차단 {b.vehicle_id} {b.reason.value}" for b in blocks]
    return lines
