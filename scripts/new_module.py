"""Scaffold a new pipeline module.

Usage: uv run python scripts/new_module.py <name> <PREFIX>
Creates modules/<name>/{__init__.py, AGENTS.md, SPEC.md, actions/, tests/}.
Then work on a branch named `<name>/<topic>` and add actions with scripts/new_action.py.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.spec import SPEC_HEADER  # noqa: E402

AGENTS_TMPL = """# {name} — (한 줄 역할을 적으세요)

- 책임: (이 모듈이 하는 일을 한두 줄로)
- 입력: (타입, `contracts/models.py` 기준) / 출력: (타입)
- 공개 API(`__init__.py`): (다른 모듈이 import할 함수)
- 새 동작은 `/new-action`(= `uv run python scripts/new_action.py {name} <verb_noun> "<설명>"`)으로 시작한다.
- 담당: (이름). 브랜치 `{name}/<주제>`.
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("prefix")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z][a-z0-9_]*", a.name):
        sys.exit(f"모듈 이름은 소문자 snake_case여야 합니다: {a.name}")
    if not re.fullmatch(r"[A-Z]{2,5}", a.prefix):
        sys.exit(f"PREFIX는 대문자 2~5자여야 합니다: {a.prefix}")
    mod = Path(a.root) / "modules" / a.name
    if mod.exists():
        sys.exit(f"이미 있는 모듈입니다: modules/{a.name}")
    for pkg in (mod, mod / "actions", mod / "tests"):
        pkg.mkdir(parents=True, exist_ok=True)
        (pkg / "__init__.py").touch()
    (mod / "AGENTS.md").write_text(AGENTS_TMPL.format(name=a.name), encoding="utf-8")
    (mod / "SPEC.md").write_text(
        f"<!-- prefix: {a.prefix} -->\n# {a.name} SPEC\n\n" + SPEC_HEADER, encoding="utf-8"
    )
    print(f"modules/{a.name} 생성. 브랜치 `{a.name}/<주제>`에서 작업하세요.")
    print(f'다음: uv run python scripts/new_action.py {a.name} <verb_noun> "<설명>"')


if __name__ == "__main__":
    main()
