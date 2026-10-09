"""Task ledger operations on the shared log (decision 0013): load for reading, write one event.

Used by scripts/task.py and scripts/new_action.py. Every write re-reads origin/main.
"""

import subprocess
from pathlib import Path

from tools.gitpush import LOG, OfflineError, fetch, fetch_age_min, push_tasks, read_remote_file
from tools.tasks import Item, Refused, apply, dump_event, parse_log, replay
from tools.tasks_view import render_now


def git_name(root: Path) -> str:
    r = subprocess.run(
        ["git", "config", "user.name"], cwd=root, capture_output=True, text=True, encoding="utf-8"
    )
    return r.stdout.strip()


def is_repo_top(root: Path) -> bool:
    r = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return r.returncode == 0 and Path(r.stdout.strip()).resolve() == root.resolve()


def load(root: Path) -> tuple[dict[str, Item], str | None]:
    """Latest items from origin/main, plus an offline note (None when the fetch worked)."""
    note = None
    if not fetch(root):
        age = fetch_age_min(root)
        note = f"오프라인: {age}분 전 기준" if age is not None else "오프라인: 받은 적 없음"
    return replay(parse_log(read_remote_file(root, LOG))), note


def write(
    root: Path,
    op: str,
    target: str,
    by: str,
    text: str = "",
    take: bool = False,
    assign: str | None = None,
) -> tuple[dict, str, dict[str, Item]]:
    """Validate against the latest remote log and push one event."""
    out: dict = {}

    def build(old: str) -> tuple[str, str, str]:
        events = parse_log(old)
        ev = apply(replay(events), op, by, target, text=text, take=take, assign=assign)
        events.append(ev)
        out["ev"], out["items"] = ev, replay(events)
        sep = "" if not old or old.endswith("\n") else "\n"
        return (
            old + sep + dump_event(ev) + "\n",
            render_now(out["items"], ev["at"]),
            f"task: {op} {ev['id']} {by}",
        )

    sha = push_tasks(root, build)
    return out["ev"], sha, out["items"]


def start_for_spec(root: Path, spec_id: str, by: str, take: bool = False) -> Item | None:
    """Start the plan item linked to a SPEC row (new_action.py). None if nothing is linked."""
    if not is_repo_top(root):
        raise OfflineError(f"{root}는 git 저장소 최상위가 아님")
    items, note = load(root)
    if note:
        raise OfflineError(note)
    it = next((i for i in items.values() if i.spec == spec_id), None)
    if it is None:
        return None
    if not (it.status == "진행중" and it.owner == by):
        write(root, "start", it.id, by, take=take)
    return it


def seed(root: Path, text: str) -> int:
    """First fill of the ledger (lead, once). Refused when origin already has a log."""
    events = parse_log(text)
    if not events:
        raise Refused("seed 파일이 비었음")
    items = replay(events)

    def build(old: str) -> tuple[str, str, str]:
        if old.strip():
            raise Refused("이미 기록이 있음: seed는 처음 한 번만")
        return text, render_now(items, events[-1]["at"]), f"task: seed {len(items)} items"

    push_tasks(root, build)
    return len(items)
