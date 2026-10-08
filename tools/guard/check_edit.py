"""Edit guard for Claude Code (Edit/Write) and Codex (apply_patch). Stdlib only.

Usage (hook): python3 tools/guard/check_edit.py pre|post [--ask-accept|--defer-accept] < hook JSON
Exit 0 = allow, exit 2 = block (reason on stderr, shown to the AI).
--ask-accept (Claude Code): `decide.py accept` shows the human a permission prompt.
--defer-accept (Codex): simple `decide.py accept` passes; .codex/rules makes Codex prompt.
"""

import json
import os
import re
import subprocess
import sys
import traceback
from fnmatch import fnmatch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.guard.bash_rules import ASK_REASON, check_bash, is_accept  # noqa: E402
from tools.guard.edits import (  # noqa: E402,F401
    ALWAYS,
    CONFIRMED_RE,
    CONTRACTS,
    INFRA,
    PROTECTED,
    Edit,
    current_branch,
    extract_edits,
)
from tools.spec import spec_actions  # noqa: E402


def _after_edit(payload: dict, e: Edit) -> str:
    """Text of an existing file after Claude Edit/MultiEdit replacements (best effort)."""
    ti = payload.get("tool_input") or {}
    if not e.path.exists() or "content" in ti:
        return ""
    text = e.path.read_text(encoding="utf-8")
    for p in ti.get("edits") or [ti]:
        if p.get("old_string"):
            text = text.replace(p["old_string"], p.get("new_string", ""), 1)
    return text


def check_pre(
    payload: dict, root: Path, branch: str, freeze: bool, accept_mode: str = "block"
) -> str | None:
    blocked = check_bash(payload, accept_mode)
    if blocked:
        return blocked
    for e in extract_edits(payload):
        try:
            rel = e.path.relative_to(root.resolve()).as_posix()
        except ValueError:
            continue
        if any(fnmatch(rel, pat) for pat in PROTECTED):
            return (
                f"[guard] `{rel}`은 보호 파일입니다(자동 생성·정책·비밀값). 직접 수정하지 마세요."
            )
        if rel.startswith("decisions/log/"):
            if e.path.exists() and CONFIRMED_RE.search(e.path.read_text(encoding="utf-8")):
                return f"[guard] `{rel}`은 확정된 결정입니다. 바꾸려면 사람에게 요청하세요."
            if CONFIRMED_RE.search(e.new_text) or CONFIRMED_RE.search(_after_edit(payload, e)):
                return "[guard] AI는 결정을 `확정`으로 쓸 수 없습니다. `제안`으로 두고 사람에게 확정을 요청하세요."
        m = re.fullmatch(r"modules/([^/]+)/actions/([a-z0-9_]+)\.py", rel)
        if m and e.is_new and not freeze and m.group(2) != "__init__":
            if m.group(2) not in spec_actions(root / "modules" / m.group(1) / "SPEC.md"):
                return (
                    f"[guard] 액션 `{m.group(2)}`이 modules/{m.group(1)}/SPEC.md에 없습니다. "
                    f'`uv run python scripts/new_action.py {m.group(1)} {m.group(2)} "설명"`으로 만드세요.'
                )
    return None


def check_post(payload: dict, root: Path, freeze: bool) -> str | None:
    edits = extract_edits(payload)
    for e in edits:
        if (
            "decisions/log/" in e.path.as_posix()
            and e.path.exists()
            and e.path.suffix == ".md"
            and CONFIRMED_RE.search(e.path.read_text(encoding="utf-8"))
        ):
            return (
                f"[guard] `{e.path.name}`이 `확정` 상태가 되었습니다. AI는 결정을 확정할 수 없습니다. "
                "`status: 제안`으로 되돌리고 사람에게 확정을 요청하세요."
            )
    if freeze:
        return None
    for e in edits:
        if not e.path.exists() or e.path.suffix not in (".py", ".ts", ".tsx"):
            continue
        rel = (
            e.path.relative_to(root.resolve()).as_posix()
            if e.path.is_relative_to(root.resolve())
            else ""
        )
        limit = 80 if re.fullmatch(r"modules/[^/]+/actions/[^/]+\.py", rel) else 200
        n = len(e.path.read_text(encoding="utf-8").splitlines())
        if rel and n > limit and "knowledge/spikes/" not in rel:
            return (
                f"[guard] `{rel}`이 {n}줄로 기준 {limit}줄을 넘었습니다. "
                "역할별로 액션(새 SPEC 행)이나 파일을 쪼개세요."
            )
    return None


def _run(mode: str, raw: bytes, accept_mode: str = "block") -> str | None:
    payload = json.loads(raw.decode("utf-8"))
    cwd = payload.get("cwd") or os.getcwd()
    r = subprocess.run(
        ["git", "-C", cwd, "rev-parse", "--show-toplevel"], capture_output=True, text=True
    )
    if r.returncode != 0:
        return None
    root = Path(r.stdout.strip())
    freeze = os.environ.get("KDTH_FREEZE") == "1"
    if mode == "pre":
        msg = check_pre(payload, root, current_branch(root), freeze, accept_mode)
        if msg is None and accept_mode == "ask" and is_accept(payload):
            return ASK
        return msg
    return check_post(payload, root, freeze)


ASK = "<ask>"


def _ask_output() -> dict:
    """Claude Code PreToolUse output that shows the human a permission prompt."""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": ASK_REASON,
        }
    }


def _log_error(exc: Exception) -> None:
    try:
        gd = subprocess.run(
            ["git", "rev-parse", "--git-dir"], capture_output=True, text=True
        ).stdout.strip()
        tb = traceback.extract_tb(exc.__traceback__)[-1]
        line = f"{type(exc).__name__}: {exc} ({Path(tb.filename).name}:{tb.lineno})\n"
        if gd:
            with open(Path(gd) / "guard-errors.log", "a", encoding="utf-8") as f:
                f.write(line)
    except Exception:
        pass


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "pre"
    try:
        flags = sys.argv[2:]
        accept_mode = (
            "ask" if "--ask-accept" in flags else "defer" if "--defer-accept" in flags else "block"
        )
        msg = _run(mode, sys.stdin.buffer.read(), accept_mode)
    except Exception as exc:  # fail open on malformed payloads / unexpected errors
        _log_error(exc)
        sys.exit(0)
    if msg is ASK:
        print(json.dumps(_ask_output(), ensure_ascii=False))
        sys.exit(0)
    if msg:
        print(msg, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
