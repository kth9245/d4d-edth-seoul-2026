"""Shell-command rules for the guard (Bash / shell tools). Stdlib only."""

import re

BASH_BLOCK = [
    re.compile(r"decide\.py\s+accept"),
    re.compile(r">>?\s*['\"]?\S*decisions/POLICY\.md"),
    re.compile(r"\bsed\s+(?:-\S+\s+)*-\S*i\S*[^|;&\n]*decisions/POLICY\.md"),
    re.compile(r"\btee\b[^|;&\n]*decisions/POLICY\.md"),
]


def check_bash(payload: dict) -> str | None:
    """Block AI-run decision confirmation / POLICY.md writes via shell commands."""
    ti = payload.get("tool_input") or {}
    cmd = ti.get("command")
    if isinstance(cmd, list):
        cmd = " ".join(str(c) for c in cmd)
    if not isinstance(cmd, str) or "*** Begin Patch" in cmd or ti.get("file_path"):
        return None
    if any(rx.search(cmd) for rx in BASH_BLOCK):
        return (
            "[guard] 결정 확정(`decide.py accept`)과 `decisions/POLICY.md` 수정은 사람만 할 수 있습니다. "
            "이 명령을 실행하지 말고 사람에게 직접 실행해 달라고 요청하세요."
        )
    return None
