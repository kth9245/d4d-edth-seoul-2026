"""Render the task ledger (decision 0013): tasks/NOW.md and the terminal views. Pure."""

import re
from collections import Counter

from tools.tasks import CLOSED, TEAM, Item, children

HEADER = "<!-- 자동 생성 파일 (scripts/task.py). 직접 수정하지 마세요. -->"
KIND = {"note": "메모", "decide": "결정", "block": "막힘", "drop": "뺌"}
NONE = "- (없음)"


def hhmm(at: str) -> str:
    """'2026-10-10T12:03:15+09:00' -> '10/10 12:03' (the log already stores KST)."""
    return f"{int(at[5:7])}/{int(at[8:10])} {at[11:16]}"


def _key(it: Item) -> list[int]:
    return [int(n) for n in re.findall(r"\d+", it.id)]


def _of(items: dict[str, Item], status: str) -> list[Item]:
    return sorted((i for i in items.values() if i.status == status), key=_key)


def line(it: Item, items: dict[str, Item]) -> str:
    s = f"- **{it.id}** {it.title}"
    if it.status in ("진행중", "막힘"):
        s += f" — {it.owner}, {hhmm(it.since)}부터"
    elif it.status == "완료":
        s += f" — {it.owner}, {hhmm(it.since)}"
    kids = children(items, it.id)
    if kids:
        s += f" · 하위 {sum(k.status in CLOSED for k in kids)}/{len(kids)} 완료"
    if it.spec:
        s += f" · {it.spec}"
    why = [e[3] for e in it.entries if e[2] == {"막힘": "block", "뺌": "drop"}.get(it.status)]
    return s + (f" — {why[-1]}" if why else "")


def _doing(items: dict[str, Item]) -> list[str]:
    doing = _of(items, "진행중")
    many = Counter(i.owner for i in doing)
    return [line(i, items) for i in doing] + [
        f"- ⚠ {who} 진행중 {n}개" for who, n in many.items() if n > 1
    ]


def _decisions(items: dict[str, Item], n: int) -> list[str]:
    ds = sorted(
        (
            (e[0], e[1], it.id, e[3])
            for it in items.values()
            for e in it.entries
            if e[2] == "decide"
        ),
        reverse=True,
    )
    return [f"- {hhmm(at)} {by} · {iid} · {text}" for at, by, iid, text in ds[:n]]


def _section(title: str, rows: list[str]) -> list[str]:
    return ["", f"## {title}", *(rows or [NONE])]


def render_now(items: dict[str, Item], last_at: str) -> str:
    out = [
        HEADER,
        "",
        "# 지금 작업판",
        "",
        f"마지막 기록 {hhmm(last_at)} KST · 상세(입력·출력·완료 기준)는 docs/research/09 6절 · "
        "기록은 `uv run python scripts/task.py`로만",
    ]
    out += _section("진행중", _doing(items))
    out += _section("막힘", [line(i, items) for i in _of(items, "막힘")])
    out += ["", "## 예정"]
    planned = _of(items, "예정")
    others = sorted({i.assign for i in planned if i.assign and i.assign not in TEAM})
    for who in (*TEAM, *others, None):
        rows = [line(i, items) for i in planned if i.assign == who]
        if rows:
            out += ["", f"### {who or '누구나'}", *rows]
    if not planned:
        out.append(NONE)
    out += _section("최근 결정", _decisions(items, 10))
    done = sorted(_of(items, "완료"), key=lambda i: i.since, reverse=True)
    out += _section("완료", [line(i, items) for i in done])
    out += _section("뺌", [line(i, items) for i in _of(items, "뺌")])
    return "\n".join(out) + "\n"


def render_show(items: dict[str, Item], me: str) -> str:
    planned = _of(items, "예정")
    out = [
        "진행중",
        *(_doing(items) or [NONE]),
        "막힘",
        *([line(i, items) for i in _of(items, "막힘")] or [NONE]),
        f"내 예정 ({me})",
        *([line(i, items) for i in planned if i.assign == me] or [NONE]),
        f"누구나 예정 {sum(i.assign is None for i in planned)}개 · 전체는 task.py show --all",
        "최근 결정",
        *(_decisions(items, 5) or [NONE]),
    ]
    return "\n".join(out) + "\n"


def render_item(items: dict[str, Item], iid: str) -> str:
    it = items[iid]
    out = [
        line(it, items),
        f"  상태 {it.status} · 배정 {it.assign or '누구나'} · 통합 {it.slot or '-'}",
    ]
    out += ["  " + line(k, items) for k in sorted(children(items, iid), key=_key)]
    out += [f"  {hhmm(at)} {by} {KIND[kind]}: {text}" for at, by, kind, text in it.entries]
    return "\n".join(out) + "\n"
