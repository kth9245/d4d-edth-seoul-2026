"""Decision 0052: rename play to role in code, API, data and screen text, in one pass.

Rerunnable: on already renamed files it changes nothing. Teammates with work that was not pushed before
the rename: rebase onto main, run this, then run the tests.
History stays as written (decisions, knowledge notes, docs, tasks, BUILT_HERE), except the spike code
under knowledge/spikes/ that tests run against the contracts; the generated contract files
are rebuilt by scripts/gen_contracts.py and scripts/gen_examples.py, not renamed here.
Usage: uv run python scripts/rename_play_role.py
"""

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = (
    "decisions/",
    "knowledge/",
    "docs/",
    "tasks/",
    "demo/BUILT_HERE.md",
    "contracts/schema/",
    "contracts/examples/",
    "modules/cop-ui/src/contracts.gen.ts",
    "scripts/rename_play_role.py",
    "tests/test_rename_play_role.py",
)
# "display" and "replay" keep their play (a lowercase letter before it); "newplay" is a class name of ours
WORD = re.compile(r"newplay|(?<![A-Z])PLAY|Play|(?<![a-z])play")
SAME = {"newplay": "newrole", "PLAY": "ROLE", "Play": "Role"}
# 플레이 ends in a vowel, Role (롤) in ㄹ: the object, subject, topic and "and" particles change
KOREAN = re.compile(r"플레이([를가는와]?)")
PARTICLE = {"를": "을", "가": "이", "는": "은", "와": "과"}


def rename_text(s: str) -> str:
    s = KOREAN.sub(lambda m: "Role" + PARTICLE.get(m.group(1), m.group(1)), s)
    return WORD.sub(lambda m: SAME.get(m.group(0), "role"), s)


def rename_path(p: str) -> str:
    return WORD.sub(lambda m: SAME.get(m.group(0), "role"), p)


def should_touch(p: str) -> bool:
    return p.startswith("knowledge/spikes/") or not p.startswith(
        SKIP
    )  # the spike is code the tests run


def _files() -> tuple[list[str], set[str]]:
    def ls(*args: str) -> list[str]:
        out = subprocess.run(
            ["git", "ls-files", "-z", *args], cwd=ROOT, capture_output=True, check=True
        )
        return [f for f in out.stdout.decode("utf-8").split("\0") if f]

    tracked = ls("--cached")
    return tracked + ls("--others", "--exclude-standard"), set(tracked)


def main() -> None:
    files, tracked = _files()
    edited, moved, left = 0, 0, set()
    for f in files:
        p = ROOT / f
        if not should_touch(f) or not p.is_file() or p.is_symlink():
            continue
        try:
            s = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if (new := rename_text(s)) != s:
            p.write_text(new, encoding="utf-8")
            edited += 1
        if (to := rename_path(f)) != f:
            (ROOT / to).parent.mkdir(parents=True, exist_ok=True)
            if f in tracked:
                subprocess.run(["git", "mv", f, to], cwd=ROOT, check=True)
            else:
                p.rename(ROOT / to)
            moved += 1
            left.add(p.parent)
    for d in sorted(
        left, key=lambda x: len(x.parts), reverse=True
    ):  # old folders: only caches remain
        if d.exists() and all(c.name == "__pycache__" for c in d.iterdir()):
            shutil.rmtree(d)
    print(f"play -> role: {edited} files edited, {moved} moved (decision 0052)")
    print("next: uv run python scripts/gen_contracts.py && uv run python scripts/gen_examples.py")


if __name__ == "__main__":
    main()
