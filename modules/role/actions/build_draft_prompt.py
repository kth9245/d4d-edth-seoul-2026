"""PLY-12 build_draft_prompt: AI 초안 프롬프트 조립(결정 0028, change_cot식 절 구조, JSON 출력)
본문은 modules/role/draft_prompt.md. 작전에서는 name·purpose·area·zone만 넣는다.
started_ms·assign 등 실행 중 바뀌는 칸을 넣으면 캐시 키 sha256(prompt)가 실행 중에 달라진다.
SPEC: modules/role/SPEC.md#PLY-12
"""

import json
from pathlib import Path

from contracts.models import Operation, Polygon

TEMPLATE = Path(__file__).resolve().parents[1] / "draft_prompt.md"


def _points(poly: Polygon) -> str:
    return json.dumps([p.model_dump() for p in poly.points], ensure_ascii=False)


def build_draft_prompt(text: str, op: Operation) -> str:
    fill = {
        "op_name": op.name,
        "op_purpose": op.purpose or "(없음)",
        "area": _points(op.area),
        "zone": _points(op.zone),
        "text": text.strip(),  # last, so braces inside the operator text stay as written
    }
    out = TEMPLATE.read_text(encoding="utf-8")
    for key, value in fill.items():
        out = out.replace("{" + key + "}", value)
    return out
