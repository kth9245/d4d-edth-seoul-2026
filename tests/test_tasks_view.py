from tools.tasks import replay
from tools.tasks_view import HEADER, hhmm, line, render_item, render_now, render_show

T1, T2, T3 = ("2026-10-10T12:03:15+09:00", "2026-10-10T13:20:00+09:00", "2026-10-10T14:00:00+09:00")


def add(iid, parent=None, assign=None, spec=None):
    return {
        "at": T1,
        "by": "kth9245",
        "op": "add",
        "id": iid,
        "title": f"제목 {iid}",
        "parent": parent,
        "assign": assign,
        "slot": "1",
        "spec": spec,
    }


def ev(op, iid, by="최동호", at=T1, **kw):
    return {"at": at, "by": by, "op": op, "id": iid, **kw}


ITEMS = replay(
    [
        add("Part2-17", assign="최동호", spec="SIM-08"),
        add("Part2-17.1", parent="Part2-17"),
        add("Part2-17.2", parent="Part2-17"),
        add("Part2-1", assign="최동호"),
        add("Part3-7", assign="황승주"),
        add("Part1-9", assign="kth9245"),
        add("Part3-15"),
        add("Part1-5", assign="kth9245"),
        add("Part2-2", assign="최동호"),
        ev("start", "Part2-17"),
        ev("done", "Part2-17.1", at=T2),
        ev("start", "Part2-2"),
        ev("start", "Part3-7", by="황승주"),
        ev("block", "Part3-7", by="황승주", text="expand 표 None"),
        ev("decide", "Part3-7", by="황승주", at=T2, text="watch_point/sea를 hold로"),
        ev("decide", "Part2-17", at=T3, text="스텁은 예시 JSON"),
        ev("note", "Part2-17", text="스텁 목록은 engine.py 머리"),
        ev("drop", "Part1-5", by="kth9245", text="통합 2로"),
    ]
)


def test_hhmm():
    assert hhmm(T1) == "10/10 12:03"


def test_line_shows_owner_since_children_and_spec():
    assert line(ITEMS["Part2-17"], ITEMS) == (
        "- **Part2-17** 제목 Part2-17 — 최동호, 10/10 12:03부터 · 하위 1/2 완료 · SIM-08"
    )
    assert line(ITEMS["Part3-7"], ITEMS).endswith("— expand 표 None")
    assert line(ITEMS["Part1-5"], ITEMS).endswith("— 통합 2로")


def test_now_sections_in_order_and_grouped():
    now = render_now(ITEMS, T3)
    assert now.startswith(HEADER)
    heads = [
        "## 진행중",
        "## 막힘",
        "## 예정",
        "### kth9245",
        "### 최동호",
        "### 누구나",
        "## 최근 결정",
        "## 완료",
        "## 뺌",
    ]
    pos = [now.index(h) for h in heads]
    assert pos == sorted(pos)
    assert "마지막 기록 10/10 14:00 KST" in now
    assert "- ⚠ 최동호 진행중 2개" in now
    assert "### 황승주" not in now  # 황승주 has nothing planned
    decisions = now[now.index("## 최근 결정") : now.index("## 완료")]
    assert decisions.index("스텁은 예시 JSON") < decisions.index("watch_point/sea를 hold로")
    assert "스텁 목록은 engine.py 머리" not in now  # notes only in `show <번호>`


def test_planned_keeps_unknown_assignees_and_empty_sections_say_none():
    items = replay([add("Part9-1", assign="리드")])
    now = render_now(items, T1)
    assert "### 리드" in now and "- **Part9-1**" in now
    assert now.count("- (없음)") == 5  # 진행중, 막힘, 최근 결정, 완료, 뺌


def test_show_summarises_for_me():
    out = render_show(ITEMS, "최동호")
    assert out.index("진행중") < out.index("막힘") < out.index("내 예정 (최동호)")
    assert "**Part2-1**" in out and "**Part3-15**" not in out
    assert "누구나 예정 2개" in out  # Part3-15, Part2-17.2
    assert "watch_point/sea를 hold로" in out


def test_item_lists_children_and_all_entries():
    out = render_item(ITEMS, "Part2-17")
    assert "**Part2-17.1**" in out and "**Part2-17.2**" in out
    assert "메모: 스텁 목록은 engine.py 머리" in out and "결정: 스텁은 예시 JSON" in out
    assert "배정 최동호" in out
