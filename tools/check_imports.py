"""Commit check: module boundaries via AST. Stdlib only."""

import argparse
import ast
import sys
from pathlib import Path

TOPS = ("modules", "shared", "contracts")
SKIP = {"node_modules", ".venv", "__pycache__", "dist"}


def _imports(tree: ast.AST) -> list[str]:
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.append(node.module)
    return names


def _violation(rel: Path, name: str) -> str | None:
    parts, top = name.split("."), rel.parts[0]
    if parts[0] == "knowledge":
        return "knowledge(실험 코드·문서)는 import할 수 없습니다"
    if top in ("shared", "contracts") and parts[0] == "modules":
        return f"{top}는 modules를 import할 수 없습니다"
    if top == "modules" and parts[0] == "modules" and len(parts) >= 3 and parts[1] != rel.parts[1]:
        return f"다른 모듈 내부입니다. `from modules.{parts[1]} import ...`(공개 API)만 쓰세요"
    return None


def _files(root: Path, paths: list[str] | None):
    if paths is not None:
        for rel in paths:
            p = root / rel
            if rel.endswith(".py") and rel.split("/")[0] in TOPS and p.exists():
                yield p
        return
    for top in TOPS:
        yield from (root / top).rglob("*.py")


def problems(root: Path, paths: list[str] | None = None) -> list[str]:
    out = []
    for p in _files(root, paths):
        rel = p.relative_to(root)
        if SKIP & set(rel.parts):
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError as e:
            out.append(f"{rel}: 문법 오류 {e.msg} (line {e.lineno})")
            continue
        for name in _imports(tree):
            why = _violation(rel, name)
            if why:
                out.append(f"{rel.as_posix()}: import {name} — {why}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("paths", nargs="*", help="check only these files (default: whole repo)")
    a = ap.parse_args()
    found = problems(Path(a.root), a.paths or None)
    if found:
        print("[check_imports]\n" + "\n".join(found), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
