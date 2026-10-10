"""PLY-01 load_play: 플레이 JSON을 읽고 잘못된 값은 위치(필드 경로·줄)와 함께 ValueError로 알린다
SPEC: modules/play/SPEC.md#PLY-01
"""

from pathlib import Path

from pydantic import ValidationError

from contracts.models import Play


def load_play(path: str | Path) -> Play:
    path = Path(path)
    try:
        return Play.model_validate_json(path.read_text(encoding="utf-8"))
    except ValidationError as e:
        lines = [f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()]
        raise ValueError(f"플레이 파일 오류 {path.name}:\n" + "\n".join(lines)) from None
