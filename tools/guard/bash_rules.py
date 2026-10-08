"""Shell-command rules for the guard (Bash / shell tools). Stdlib only.

Decision confirmation (`decide.py accept`) has three modes:
  block - always blocked (default)
  ask   - Claude Code: hook returns permissionDecision "ask" (human approval prompt)
  defer - Codex: hook lets only the simple form through; .codex/rules/decide.rules
          (decision="prompt") makes Codex ask the human before running it
"""

import re

ACCEPT_RX = re.compile(r"decide\.py\s+accept")
SIMPLE_ACCEPT_RX = re.compile(
    r"\s*(?:uv\s+run\s+python|python3?)\s+scripts/decide\.py\s+accept\s+\w+(?:\s+--by\s+[\w.\-]+)?\s*"
)
WRAPPER_RX = re.compile(r"\s*(?:/bin/|/usr/bin/)?(?:ba|z)?sh\s+-l?c\s+(['\"])(.*)\1\s*", re.S)
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
        if (
            len(cmd) == 3
            and re.fullmatch(r"(?:\S*/)?(?:ba|z)?sh", str(cmd[0]))
            and cmd[1] in ("-c", "-lc")
        ):
            cmd = str(cmd[2])
        else:
            cmd = " ".join(str(c) for c in cmd)
    if not isinstance(cmd, str) or "*** Begin Patch" in cmd or ti.get("file_path"):
        return None
    m = WRAPPER_RX.fullmatch(cmd)
    return m.group(2) if m else cmd


def is_accept(payload: dict) -> bool:
    """True when the shell command confirms a decision (`decide.py accept`)."""
    cmd = _command(payload)
    return bool(cmd and ACCEPT_RX.search(cmd))


def check_bash(payload: dict, accept_mode: str = "block") -> str | None:
    """Block POLICY.md writes; handle decision confirmation per accept_mode."""
    cmd = _command(payload)
    if cmd is None:
        return None
    if any(rx.search(cmd) for rx in POLICY_BLOCK):
        return (
            "[guard] `decisions/POLICY.md` 수정은 사람만 할 수 있습니다. "
            "이 명령을 실행하지 말고 사람에게 직접 고쳐 달라고 요청하세요."
        )
    if not ACCEPT_RX.search(cmd) or accept_mode == "ask":
        return None
    if accept_mode == "defer":
        if SIMPLE_ACCEPT_RX.fullmatch(cmd):
            return None
        return (
            "[guard] 결정 확정은 다른 명령과 섞지 말고 "
            "`uv run python scripts/decide.py accept NNNN --by <이름>` 한 줄로만 실행하세요. "
            "Codex가 사람에게 승인을 묻습니다."
        )
    return (
        "[guard] 이 도구에서는 AI가 결정 확정(`decide.py accept`)을 실행할 수 없습니다. "
        "사람에게 `! uv run python scripts/decide.py accept NNNN --by <이름>`을 직접 실행해 달라고 요청하세요."
    )
