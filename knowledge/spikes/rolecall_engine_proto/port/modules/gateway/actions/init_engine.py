"""GW-02 init_engine: 시나리오로 작전 시작 상태를 만든다 (contracts/API.md §3 시작 상태)
기체는 home·ready, play_id = op.assign, step_id = 그 플레이 entry, t_ms = started_ms, 배정 "작전 배정".
SPEC: modules/gateway/SPEC.md#GW-02
"""

from contracts.models import Assignment, Metrics, RunState, Scenario, VehicleState
from modules.gateway.engine_state import EngineState


def init_engine(scenario: Scenario) -> EngineState:
    op, plays = scenario.operation, {p.id: p for p in scenario.plays}

    def start(v) -> VehicleState:
        pid = op.assign.get(v.id)
        return VehicleState(id=v.id, t_ms=op.started_ms, pos=v.home, heading_deg=0,
                            battery_pct=100, status="ready", play_id=pid,
                            step_id=plays[pid].entry if pid else None)  # fmt: skip

    assigns = [
        Assignment(vehicle_id=v, play_id=p, since_ms=op.started_ms, reason="작전 배정")
        for v, p in op.assign.items()
    ]
    return EngineState(
        t_ms=op.started_ms,
        scenario=scenario,
        specs={v.id: v for v in scenario.vehicles},
        plays=plays,
        states=[start(v) for v in scenario.vehicles],
        targets=[],
        reports=[],
        assignments=assigns,
        blocks=[],
        injections=[],
        metrics=Metrics(),
        run=RunState(status="running", speed=scenario.speed),
    )
