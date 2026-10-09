"""Task ledger model (decision 0013): replay tasks/log.jsonl and validate one new event. Pure.

The log is append-only JSON lines; state is always recomputed from the whole log, so a
retry after a rejected push validates against the newest state.
Spec: docs/superpowers/specs/2026-10-09-task-ledger-design.md
"""

import json
import re
from dataclasses import dataclass, field

from shared.kst import now_kst

TEAM = ("kth9245", "황승주", "최동호")
CLOSED = ("완료", "뺌")
TOP_RE = re.compile(r"Part\d+")
TEXT_OPS = ("block", "decide", "note", "drop")


class Refused(Exception):
    """The command is not allowed in the current state; nothing is written."""


@dataclass
class Item:
    id: str
    title: str
    parent: str | None = None
    assign: str | None = None
    owner: str | None = None
    status: str = "예정"
    slot: str | None = None
    spec: str | None = None
    since: str = ""
    entries: list[tuple[str, str, str, str]] = field(default_factory=list)  # (at, by, kind, text)


def normalize_id(raw: str) -> str:
    """'2-17' / ' part2-17.1 ' -> 'Part2-17(.1)'; '2' -> 'Part2' (top level, for add)."""
    return "Part" + re.sub(r"^part", "", raw.strip(), flags=re.I)


def parse_log(text: str) -> list[dict]:
    events = []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise ValueError(f"tasks/log.jsonl {n}번째 줄을 읽을 수 없음: {e}") from e
    return events


def dump_event(ev: dict) -> str:
    return json.dumps(ev, ensure_ascii=False)


def replay(events: list[dict]) -> dict[str, Item]:
    items: dict[str, Item] = {}
    for n, e in enumerate(events, 1):
        try:
            _step(items, e)
        except (KeyError, TypeError) as err:
            raise ValueError(f"tasks/log.jsonl {n}번째 기록이 잘못됨: {err!r}") from err
    return items


def _step(items: dict[str, Item], e: dict) -> None:
    op, at, by = e["op"], e["at"], e["by"]
    if op == "add":
        items[e["id"]] = Item(
            e["id"],
            e["title"],
            e.get("parent"),
            e.get("assign"),
            slot=e.get("slot"),
            spec=e.get("spec"),
            since=at,
        )
        return
    it = items[e["id"]]
    if op == "start":
        it.status, it.owner, it.since = "진행중", by, at
    elif op == "done":
        it.status, it.since = "완료", at
        if it.owner is None or e.get("take"):
            it.owner = by
    elif op in ("block", "drop"):
        it.status, it.since = ("막힘" if op == "block" else "뺌"), at
    if op in TEXT_OPS:
        it.entries.append((at, by, op, e["text"]))


def children(items: dict[str, Item], parent: str) -> list[Item]:
    return [i for i in items.values() if i.parent == parent]


def next_id(items: dict[str, Item], parent: str) -> str:
    if TOP_RE.fullmatch(parent):
        ks = [
            int(i.id.split("-")[1])
            for i in items.values()
            if i.parent is None and i.id.startswith(parent + "-")
        ]
        return f"{parent}-{max(ks, default=0) + 1}"
    ns = [int(i.id.rsplit(".", 1)[1]) for i in children(items, parent)]
    return f"{parent}.{max(ns, default=0) + 1}"


def apply(items, op, by, target, text="", take=False, assign=None, at=None) -> dict:
    """Validate one command against the current state and return its event. Raises Refused."""
    if by not in TEAM:
        raise Refused(
            f"팀 명단 {TEAM} 밖의 이름 {by!r}: "
            "이 저장소에서 `git config user.name <한글 이름>` (리드는 kth9245)"
        )
    target, text = normalize_id(target), " ".join(text.split())
    ev = {"at": at or now_kst().isoformat(timespec="seconds"), "by": by, "op": op}
    if op == "add":
        return {**ev, **_add(items, target, text, assign)}
    it = items.get(target)
    if it is None:
        raise Refused(f"없는 번호: {target} (task.py show --all)")
    ev["id"] = target
    if op == "start":
        return {**ev, **_start(it, by, take)}
    if op == "done":
        return {**ev, **_done(items, it, by, take)}
    if op not in TEXT_OPS:
        raise Refused(f"모르는 명령: {op}")
    if not text:
        raise Refused(f"{op}에는 내용이 필요함")
    if op == "block" and (it.owner != by or it.status not in ("진행중", "막힘")):
        raise Refused(f"{target}는 내가 진행중인 항목이 아님 (먼저 task.py start)")
    if op == "drop" and it.status == "완료":
        raise Refused(f"{target}는 이미 완료")
    return {**ev, "text": text}


def _add(items: dict[str, Item], parent: str, title: str, assign: str | None) -> dict:
    if not title:
        raise Refused("add에는 제목이 필요함")
    top = TOP_RE.fullmatch(parent) is not None
    if not (top or parent in items):
        raise Refused(f"없는 상위 번호: {parent}")
    if assign is not None and assign not in TEAM:
        raise Refused(f"팀 명단 밖의 배정: {assign!r}")
    return {
        "id": next_id(items, parent),
        "title": title,
        "parent": None if top else parent,
        "assign": assign,
        "slot": None if top else items[parent].slot,
        "spec": None,
    }


def _start(it: Item, by: str, take: bool) -> dict:
    if it.status in CLOSED and not take:
        raise Refused(f"{it.id}는 이미 {it.status}. 다시 열려면 --take")
    if it.status == "진행중" and it.owner == by:
        raise Refused(f"{it.id}는 이미 내가 진행중")
    if it.status in ("진행중", "막힘") and it.owner != by and not take:
        when = it.since[5:16].replace("T", " ")
        raise Refused(
            f"{it.id}는 {it.owner}가 {when}부터 {it.status}. 도우려면 task.py add로 "
            "하위 항목을 만들어 start, 넘겨받으려면 채팅에 알리고 --take"
        )
    return {"take": take, "from": it.owner if it.owner not in (None, by) else None}


def _done(items: dict[str, Item], it: Item, by: str, take: bool) -> dict:
    if it.status in CLOSED:
        raise Refused(f"{it.id}는 이미 {it.status}")
    left = [c.id for c in children(items, it.id) if c.status not in CLOSED]
    if left:
        raise Refused(f"{it.id}의 하위 항목이 남음: {', '.join(left)}")
    if it.owner not in (None, by) and not take:
        raise Refused(f"{it.id}는 {it.owner} 담당. 대신 끝내려면 --take")
    return {"take": take}
