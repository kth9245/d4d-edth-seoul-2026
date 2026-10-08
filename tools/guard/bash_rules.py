"""Shell-command rules for the guard (Bash / shell tools). Stdlib only."""

import re

ACCEPT_RX = re.compile(r"decide\.py\s+accept")
POLICY_BLOCK = [
    re.compile(r">>?\s*['\"]?\S*decisions/POLICY\.md"),
    re.compile(r"\bsed\s+(?:-\S+\s+)*-\S*i\S*[^|;&\n]*decisions/POLICY\.md"),
    re.compile(r"\btee\b[^|;&\n]*decisions/POLICY\.md"),
]
ASK_REASON = (
    "[guard] AI가 결정 확정(`decide.py accept`)을 실행하려 합니다. "
    "사람이 이 결정을 확정하기로 했다면 승인하세요."
)


def _command(payload: dict) -> str | None:
    ti = payload.get("tool_input") or {}
    cmd = ti.get("command")
    if isinstance(cmd, list):
        cmd = " ".join(str(c) for c in cmd)
    if not isinstance(cmd, str) or "*** Begin Patch" in cmd or ti.get("file_path"):
        return None
    return cmd


def is_accept(payload: dict) -> bool:
    """True when the shell command confirms a decision (`decide.py accept`)."""
    cmd = _command(payload)
    return bool(cmd and ACCEPT_RX.search(cmd))


def check_bash(payload: dict, allow_accept: bool = False) -> str | None:
    """Block POLICY.md writes, and decision confirmation unless the caller asks a human instead."""
    cmd = _command(payload)
    if cmd is None:
        return None
    if any(rx.search(cmd) for rx in POLICY_BLOCK):
        return (
            "[guard] `decisions/POLICY.md` 수정은 사람만 할 수 있습니다. "
            "이 명령을 실행하지 말고 사람에게 직접 고쳐 달라고 요청하세요."
        )
    if not allow_accept and ACCEPT_RX.search(cmd):
        return (
            "[guard] 이 도구에서는 AI가 결정 확정(`decide.py accept`)을 실행할 수 없습니다. "
            "사람에게 `! uv run python scripts/decide.py accept NNNN --by <이름>`을 직접 실행해 달라고 요청하세요."
        )
    return None
