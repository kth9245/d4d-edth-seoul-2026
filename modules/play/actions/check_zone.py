"""PLY-05 check_zone: step의 목적지(move_to target 좌표)·경로점(patrol_route route)이 작전 구역 밖이면 오류
표적 id("nearest" 등)는 좌표가 아니라서 보지 않는다. 판정은 safety.point_in_polygon.
SPEC: modules/play/SPEC.md#PLY-05
"""

from contracts.models import GeoPoint, Operation, Play, Step, ValidationIssue
from modules.safety import point_in_polygon


def _points(step: Step) -> list[GeoPoint]:
    p = step.do.params
    pts = [p["target"]] if isinstance(p.get("target"), dict) else []
    return [GeoPoint(**q) for q in pts + list(p.get("route", []))]


def check_zone(play: Play, op: Operation) -> list[ValidationIssue]:
    return [
        ValidationIssue(
            code="outside_zone",
            step_id=s.id,
            message=f"작전 구역 밖 경로점({q.lat:.4f}, {q.lon:.4f})",
        )  # fmt: skip
        for s in play.steps
        for q in _points(s)
        if not point_in_polygon(q, op.zone)
    ]
