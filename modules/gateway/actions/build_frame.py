"""GW-01 build_frame: 한 시점의 결과를 계약 LegacyFrame으로 묶기
SPEC: modules/gateway/SPEC.md#GW-01
"""

from contracts.models import Assessment, LegacyFrame, Response, Track


def build_frame(
    t_ms: int, tracks: list[Track], assessments: list[Assessment], responses: list[Response]
) -> LegacyFrame:
    return LegacyFrame(t_ms=t_ms, tracks=tracks, assessments=assessments, responses=responses)
