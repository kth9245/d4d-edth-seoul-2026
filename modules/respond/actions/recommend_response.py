"""RSP-01 recommend_response: 분류·위협도 임계값으로 대응 추천
SPEC: modules/respond/SPEC.md#RSP-01
"""

from contracts.models import Assessment, ObjectClass, Response, ResponseKind


def recommend_response(assessment: Assessment) -> Response:
    kind = ResponseKind.OBSERVE
    if assessment.object_class == ObjectClass.DRONE:
        if assessment.threat >= 0.9:
            kind = ResponseKind.HARD_KILL
        elif assessment.threat >= 0.7:
            kind = ResponseKind.SOFT_KILL
    reason = f"{assessment.object_class.value} 위협도 {assessment.threat:.2f}"
    return Response(track_id=assessment.track_id, kind=kind, reason=reason)
