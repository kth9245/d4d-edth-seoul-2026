"""SIM-04 load_scenario_json: 시나리오 JSON을 Scenario로 읽고 시작 시각·배정을 검사
SPEC: modules/sim/SPEC.md#SIM-04
"""

from pathlib import Path

from pydantic import ValidationError

from contracts.models import Scenario


def load_scenario_json(path: str | Path) -> Scenario:
    try:
        sc = Scenario.model_validate_json(Path(path).read_text(encoding="utf-8"))
    except ValidationError as e:
        raise ValueError(f"{path}: {e}") from e
    op, play_ids = sc.operation, {p.id for p in sc.plays}
    if op.started_ms is None:
        raise ValueError(f"{path}: operation.started_ms가 비었습니다 (결정 0018)")
    bad = {v: p for v, p in op.assign.items() if p not in play_ids or v not in op.vehicle_ids}
    if bad:
        raise ValueError(f"{path}: operation.assign이 없는 기체·플레이를 가리킵니다 {bad}")
    return sc
