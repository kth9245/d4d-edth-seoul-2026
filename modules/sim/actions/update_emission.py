"""SIM-14 update_emission: 적이 appear_offset_ms + emit_start_offset_ms 시각부터 emitting=True (결정 0039)
emit_start_offset_ms가 None인 적은 계속 무음. 한 번 켜지면 계속 방출한다.
SPEC: modules/sim/SPEC.md#SIM-14
"""

from contracts.models import Scenario, Target


def update_emission(scenario: Scenario, targets: list[Target], t_ms: int) -> list[Target]:
    start = scenario.operation.started_ms
    at = {
        e.id: start + e.appear_offset_ms + e.emit_start_offset_ms
        for e in scenario.enemies
        if e.emit_start_offset_ms is not None
    }
    return [
        t.model_copy(update={"emitting": True}) if t.id in at and t_ms >= at[t.id] else t
        for t in targets
    ]
