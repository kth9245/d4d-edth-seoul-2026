"""Ownership rules and edit extraction for the guard. Stdlib only."""

import os
import re
import subprocess
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path

PROTECTED = [
    ".env",
    ".env.*",
    "decisions/POLICY.md",
    "tasks/BOARD.md",
    "knowledge/INDEX.md",
    "decisions/INDEX.md",
    "contracts/schema/*",
    "modules/cop-ui/src/contracts.gen.ts",
]
ALWAYS = [
    "knowledge/*",
    "decisions/log/*",
    "demo/BUILT_HERE.md",
    "demo/scenarios/*",
    "pyproject.toml",
    "uv.lock",
]
INFRA = [
    "AGENTS.md",
    "README.md",
    ".gitignore",
    "modules/__init__.py",
    "tests/*",
    "scripts/*",
    "tools/*",
    ".claude/*",
    ".codex/*",
    ".agents/*",
    ".githooks/*",
    "shared/*",
    "demo/*",
    "docs/*",
]
CONTRACTS = ["contracts/*", "modules/cop-ui/src/contracts.gen.ts"]
PATCH_RE = re.compile(r"^\*\*\* (Add|Update|Delete) File: (.+)$|^\*\*\* Move to: (.+)$", re.M)
CONFIRMED_RE = re.compile(r"^\+?status:\s*[\"']?확정", re.M)


@dataclass
class Edit:
    path: Path
    new_text: str
    is_new: bool


def extract_edits(payload: dict) -> list[Edit]:
    ti = payload.get("tool_input") or {}
    cwd = Path(payload.get("cwd") or os.getcwd())
    fp = ti.get("file_path") or ti.get("notebook_path")
    if fp:
        p = (cwd / fp).resolve()
        text = ti.get("content") or ti.get("new_string") or ""
        text += "".join(e.get("new_string", "") for e in ti.get("edits") or [])
        return [Edit(p, text, not p.exists())]
    cmd = ti.get("command")
    if isinstance(cmd, list):
        cmd = "\n".join(cmd)
    if not isinstance(cmd, str) or "*** Begin Patch" not in cmd:
        return []
    edits, blocks = [], re.split(r"(?=^\*\*\* (?:Add|Update|Delete) File: )", cmd, flags=re.M)
    for block in blocks:
        for m in PATCH_RE.finditer(block):
            rel = m.group(2) or m.group(3)
            edits.append(
                Edit((cwd / rel.strip()).resolve(), block, m.group(1) == "Add" or bool(m.group(3)))
            )
    return edits


def current_branch(root: Path) -> str:
    g = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "rev-parse",
            "--git-path",
            "rebase-merge/head-name",
            "--git-path",
            "rebase-apply/head-name",
        ],
        capture_output=True,
        text=True,
    )
    for line in g.stdout.splitlines():
        head = root / line
        if head.exists():
            return head.read_text().strip().removeprefix("refs/heads/")
    r = subprocess.run(
        ["git", "-C", str(root), "branch", "--show-current"], capture_output=True, text=True
    )
    return r.stdout.strip()


def allowed(rel: str, branch: str, modules: set[str]) -> bool:
    if any(fnmatch(rel, pat) for pat in ALWAYS):
        return True
    prefix = branch.split("/", 1)[0] if "/" in branch else ""
    if prefix == "infra":
        return any(fnmatch(rel, pat) for pat in INFRA)
    if prefix == "contracts":
        return any(fnmatch(rel, pat) for pat in CONTRACTS)
    return bool(prefix) and rel.startswith(f"modules/{prefix}/")
