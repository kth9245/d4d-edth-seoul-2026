"""GW-06 build_frame_v2: 엔진 상태와 이번 틱 기록 줄로 화면에 보낼 Frame을 만든다
GW-01 build_frame(레거시 LegacyFrame)은 smoke가 쓰므로 통합 1까지 그대로 둔다.
SPEC: modules/gateway/SPEC.md#GW-06
"""

from contracts.models import Frame
from modules.gateway.engine_state import EngineState


def build_frame_v2(es: EngineState, log: list[str]) -> Frame:
    return Frame(
        t_ms=es.t_ms,
        run=es.run,
        vehicles=es.states,
        targets=es.targets,
        reports=es.reports,
        assignments=es.assignments,
        blocks=es.blocks,
        injections=es.injections,
        metrics=es.metrics,
        log=log,
    )
