"""PLY-04 check_return_battery: 기체별 예상 귀환 배터리 — home → Role의 좌표들(순서대로) → home 경로 길이로 추정
만충 출발, 소모 = 이동 시간 / 체공 시간. 30% 미만이면 오류. Role 영역(domains)이 아닌 기체는 건너뛴다.
SPEC: modules/role/SPEC.md#PLY-04
"""

from contracts.models import GeoPoint, Role, Step, ValidationIssue, VehicleSpec
from shared.geo import dist_m

MIN_PCT = 30


def _points(step: Step) -> list[GeoPoint]:
    p = step.do.params
    pts = [p["target"]] if isinstance(p.get("target"), dict) else []
    return [GeoPoint(**q) for q in pts + list(p.get("route", []))]


def check_return_battery(
    role: Role, specs: dict[str, VehicleSpec]
) -> tuple[list[ValidationIssue], dict[str, float]]:
    pts = [q for s in role.steps for q in _points(s)]
    issues, est = [], {}
    for vid, sp in specs.items():
        if sp.domain not in role.domains:
            continue
        path = [sp.home, *pts, sp.home]
        secs = sum(dist_m(a, b) for a, b in zip(path, path[1:], strict=False)) / sp.speed_mps
        est[vid] = pct = round(100 - secs / (sp.endurance_min * 60) * 100, 1)
        if pct < MIN_PCT:
            msg = f"{vid} 예상 귀환 배터리 {pct}% ({MIN_PCT}% 미만)"
            issues.append(ValidationIssue(code="low_return_battery", message=msg))
    return issues, est
