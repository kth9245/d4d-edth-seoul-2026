"""PLY-08 list_templates: demo/roles/*.json 중 template=True Role만 파일 이름 순으로 돌려준다
SPEC: modules/role/SPEC.md#PLY-08
"""

from pathlib import Path

from contracts.models import Role
from modules.role.actions.load_role import load_role

ROLES = Path(__file__).resolve().parents[3] / "demo" / "roles"


def list_templates() -> list[Role]:
    roles = (load_role(p) for p in sorted(ROLES.glob("*.json")))
    return [p for p in roles if p.template]
