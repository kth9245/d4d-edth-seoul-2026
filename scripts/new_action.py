"""Create SPEC row + action file + failing test in one step; claim or take over an existing row.

Usage: uv run python scripts/new_action.py <module> <verb_noun> "<description>"
       [--inputs ..] [--outputs ..] [--done ..] [--owner ..] [--planned] [--take]

--planned  write only the SPEC row (status 예정, no files) so someone can claim it later.
           A row whose status is 예정 is claimed by running this script without flags.
--take     take over a row someone else started (owner cell -> me; files created if missing).
"""

import argparse
import re
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.spec import SpecRow, append_row, next_id, parse_spec, replace_row  # noqa: E402

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


def write_files(mod: Path, module: str, sid: str, name: str, desc: str) -> None:
    for pkg in (mod / "actions", mod / "tests"):
        pkg.mkdir(exist_ok=True)
        (pkg / "__init__.py").touch()
    fmt = {"id": sid, "name": name, "desc": desc, "module": module}
    (mod / "actions" / f"{name}.py").write_text(ACTION_TMPL.format(**fmt), encoding="utf-8")
    (mod / "tests" / f"test_{name}.py").write_text(TEST_TMPL.format(**fmt), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("module")
    ap.add_argument("action")
    ap.add_argument("desc")
    ap.add_argument("--inputs", default="")
    ap.add_argument("--outputs", default="")
    ap.add_argument("--done", default="")
    ap.add_argument("--owner", default=None)
    ap.add_argument("--planned", action="store_true", help="행만 적는다(상태 예정, 파일 없음)")
    ap.add_argument("--take", action="store_true", help="남이 시작한 행의 담당을 나로 바꾼다")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    a = ap.parse_args()

    if not NAME_RE.match(a.action):
        fail(f"액션 이름은 verb_noun 형식의 snake_case여야 합니다: {a.action}")
    mod = Path(a.root) / "modules" / a.module
    if not (mod / "__init__.py").exists():
        fail(f"Python 모듈이 없습니다: modules/{a.module}")
    spec = mod / "SPEC.md"
    action_file = mod / "actions" / f"{a.action}.py"
    prefix, rows = parse_spec(spec.read_text(encoding="utf-8"))
    if not prefix:
        fail(f"SPEC.md 첫 줄에 <!-- prefix: XXX --> 가 없습니다: {spec}")
    owner = a.owner or git_user()
    existing = next((r for r in rows if r.action == a.action), None)

    if existing is not None:
        if existing.status == "완료" and not a.take:
            fail(f"이미 끝난 액션입니다: {a.module}.{a.action}")
        if existing.status != "예정" and not a.take:
            fail(
                f"이미 있는 액션입니다: {a.module}.{a.action} (담당 {existing.owner}). "
                "가져가려면 --take"
            )
        row = replace(
            existing,
            inputs=a.inputs or existing.inputs,
            outputs=a.outputs or existing.outputs,
            done=a.done or existing.done,
            owner=owner,
            status="진행중" if existing.status == "예정" else existing.status,
        )
        replace_row(spec, row)
        what = "가져감" if existing.status != "예정" else "시작"
        print(f"{row.id} {what}: 담당 {existing.owner} → {owner}")
        if not action_file.exists():
            write_files(mod, a.module, row.id, a.action, a.desc)
            print(f"  생성: {action_file.relative_to(a.root)}, tests/test_{a.action}.py")
        return

    if action_file.exists():
        fail(f"SPEC.md에 없는 액션 파일이 이미 있습니다: {action_file.relative_to(a.root)}")
    sid = next_id(prefix, rows)
    if a.planned:
        append_row(spec, SpecRow(sid, a.action, a.inputs, a.outputs, a.done, owner, "예정"))
        print(
            f"{sid} 예정 행 추가 (파일 없음). 시작할 사람이 같은 명령을 플래그 없이 돌리면 가져갑니다."
        )
        return
    append_row(spec, SpecRow(sid, a.action, a.inputs, a.outputs, a.done, owner, "진행중"))
    write_files(mod, a.module, sid, a.action, a.desc)
    print(
        f"{sid} 생성: {action_file.relative_to(a.root)}, modules/{a.module}/tests/test_{a.action}.py"
    )
    print("다음: 테스트를 실제 동작으로 고친 뒤 액션을 구현해 통과시키세요.")


if __name__ == "__main__":
    main()
