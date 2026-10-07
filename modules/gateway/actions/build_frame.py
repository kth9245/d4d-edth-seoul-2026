"""GW-01 build_frame: 한 시점의 결과를 계약 Frame으로 묶기
SPEC: modules/gateway/SPEC.md#GW-01
"""

from contracts.models import Assessment, Frame, Response, Track


def build_frame(
    t_ms: int, tracks: list[Track], assessments: list[Assessment], responses: list[Response]
) -> Frame:
    return Frame(t_ms=t_ms, tracks=tracks, assessments=assessments, responses=responses)
