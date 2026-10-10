"""PLY-13 draft_cache_key: AI 초안 캐시 키: sha256(운용자 문장·작전 지역·작전 구역). 작전 이름·목적·실행 중 칸은 넣지 않음(결정 0057)
같은 지역·구역의 새 작전·24시간 작전도 시연 문장의 캐시 초안을 받는다(정책 1: 시연 중 외부 호출 없음).
SPEC: modules/role/SPEC.md#PLY-13
"""

import hashlib
import json

from contracts.models import Operation


def draft_cache_key(text: str, op: Operation) -> str:
    def points(poly):
        return [[p.lat, p.lon] for p in poly.points]

    key = {"text": text.strip(), "area": points(op.area), "zone": points(op.zone)}
    return hashlib.sha256(json.dumps(key, ensure_ascii=False).encode("utf-8")).hexdigest()
