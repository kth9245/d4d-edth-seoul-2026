"""PLY-01 load_role: Role JSON을 읽고 잘못된 값은 위치(필드 경로·줄)와 함께 ValueError로 알린다
SPEC: modules/role/SPEC.md#PLY-01
"""

from pathlib import Path

from pydantic import ValidationError

from contracts.models import Role


def load_role(path: str | Path) -> Role:
    path = Path(path)
    try:
        return Role.model_validate_json(path.read_text(encoding="utf-8"))
    except ValidationError as e:
        lines = [f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()]
        raise ValueError(f"Role 파일 오류 {path.name}:\n" + "\n".join(lines)) from None
