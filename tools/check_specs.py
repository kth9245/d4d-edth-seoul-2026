"""Commit check: every action is in SPEC.md and has a test; file length limits. Stdlib only."""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.spec import parse_spec  # noqa: E402

SKIP_DIRS = {"node_modules", "dist", ".venv", "__pycache__", "spikes"}
CODE_DIRS = ["modules", "shared", "contracts", "scripts", "tools"]
GENERATED = {"contracts.gen.ts"}


def _spec_problems(mod: Path) -> list[str]:
    out = []
    rows = (
        parse_spec((mod / "SPEC.md").read_text(encoding="utf-8"))[1]
        if (mod / "SPEC.md").exists()
        else []
    )
    registered = {r.action: r for r in rows}
    files = {p.stem for p in (mod / "actions").glob("*.py") if p.stem != "__init__"}
    for name in sorted(files - registered.keys()):
        out.append(
            f"modules/{mod.name}/actions/{name}.py: SPEC.md에 없는 액션입니다 (scripts/new_action.py 사용)."
        )
    for name in sorted(files):
        if not (mod / "tests" / f"test_{name}.py").exists():
            out.append(
                f"modules/{mod.name}: 액션 {name}의 테스트 파일 tests/test_{name}.py가 없습니다."
            )
    for name, row in registered.items():
        if name not in files and row.status != "예정":
            out.append(
                f"modules/{mod.name}/SPEC.md: {row.id} {name} 상태가 '{row.status}'인데 액션 파일이 없습니다."
            )
    return out


def _code_files(root: Path, paths: list[str] | None):
    if paths is not None:
        yield from (
            root / r for r in paths if r.split("/")[0] in CODE_DIRS and (root / r).is_file()
        )
        return
    for d in CODE_DIRS:
        yield from (root / d).rglob("*")


def _length_problems(root: Path, paths: list[str] | None = None) -> list[str]:
    out = []
    for p in _code_files(root, paths):
        if p.suffix not in (".py", ".ts", ".tsx") or p.name in GENERATED:
            continue
        if SKIP_DIRS & set(p.relative_to(root).parts):
            continue
        rel = p.relative_to(root).as_posix()
        limit = (
            80
            if p.parent.name == "actions" and rel.startswith("modules/") and p.suffix == ".py"
            else 200
        )
        n = len(p.read_text(encoding="utf-8").splitlines())
        if n > limit:
            out.append(f"{rel}: {n}줄 (기준 {limit}줄). 쪼개세요.")
    return out


def problems(root: Path, paths: list[str] | None = None) -> list[str]:
    out = []
    touched = (
        None
        if paths is None
        else {r.split("/")[1] for r in paths if r.startswith("modules/") and r.count("/") >= 2}
    )
    for mod in sorted((root / "modules").glob("*/")):
        if (mod / "__init__.py").exists() and (touched is None or mod.name in touched):
            out += _spec_problems(mod)
    return out + _length_problems(root, paths)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("paths", nargs="*", help="check only modules/files touched by these paths")
    a = ap.parse_args()
    found = problems(Path(a.root), a.paths or None)
    if not found:
        return
    freeze = os.environ.get("KDTH_FREEZE") == "1"
    print(("[경고] " if freeze else "[check_specs] ") + "\n".join(found), file=sys.stderr)
    sys.exit(0 if freeze else 1)


if __name__ == "__main__":
    main()
