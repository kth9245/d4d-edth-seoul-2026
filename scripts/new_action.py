"""Create SPEC row + action file + failing test in one step.

Usage: uv run python scripts/new_action.py <module> <verb_noun> "<description>"
       [--inputs ..] [--outputs ..] [--done ..] [--owner ..]
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.spec import SpecRow, append_row, next_id, parse_spec  # noqa: E402

NAME_RE = re.compile(r"^[a-z]+(_[a-z0-9]+)+$")

ACTION_TMPL = '''"""{id} {name}: {desc}
SPEC: modules/{module}/SPEC.md#{id}
"""


def {name}(*args, **kwargs):
    raise NotImplementedError
'''

TEST_TMPL = """import pytest

from modules.{module}.actions.{name} import {name}


def test_{name}():
    pytest.fail("{id}: replace with a real test for {name}")
    {name}()
"""


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(1)


def git_user() -> str:
    r = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
    return r.stdout.strip() or "?"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("module")
    ap.add_argument("action")
    ap.add_argument("desc")
    ap.add_argument("--inputs", default="")
    ap.add_argument("--outputs", default="")
    ap.add_argument("--done", default="")
    ap.add_argument("--owner", default=None)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    a = ap.parse_args()

    if not NAME_RE.match(a.action):
        fail(f"액션 이름은 verb_noun 형식의 snake_case여야 합니다: {a.action}")
    mod = Path(a.root) / "modules" / a.module
    if not (mod / "__init__.py").exists():
        fail(f"Python 모듈이 없습니다: modules/{a.module}")
    spec = mod / "SPEC.md"
    action_file = mod / "actions" / f"{a.action}.py"
    test_file = mod / "tests" / f"test_{a.action}.py"
    prefix, rows = parse_spec(spec.read_text(encoding="utf-8"))
    if action_file.exists() or any(r.action == a.action for r in rows):
        fail(f"이미 있는 액션입니다: {a.module}.{a.action}")
    if not prefix:
        fail(f"SPEC.md 첫 줄에 <!-- prefix: XXX --> 가 없습니다: {spec}")

    sid = next_id(prefix, rows)
    owner = a.owner or git_user()
    append_row(spec, SpecRow(sid, a.action, a.inputs, a.outputs, a.done, owner, "진행중"))
    for pkg in (mod / "actions", mod / "tests"):
        pkg.mkdir(exist_ok=True)
        (pkg / "__init__.py").touch()
    fmt = {"id": sid, "name": a.action, "desc": a.desc, "module": a.module}
    action_file.write_text(ACTION_TMPL.format(**fmt), encoding="utf-8")
    test_file.write_text(TEST_TMPL.format(**fmt), encoding="utf-8")
    print(f"{sid} 생성: {action_file.relative_to(a.root)}, {test_file.relative_to(a.root)}")
    print("다음: 테스트를 실제 동작으로 고친 뒤 액션을 구현해 통과시키세요.")


if __name__ == "__main__":
    main()
