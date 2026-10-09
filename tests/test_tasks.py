import pytest

from tools.tasks import (
    Refused,
    apply,
    dump_event,
    next_id,
    normalize_id,
    parse_log,
    replay,
)

AT = "2026-10-10T12:00:00+09:00"


def add(iid, parent=None, assign=None, spec=None):
    return {
        "at": AT,
        "by": "kth9245",
        "op": "add",
        "id": iid,
        "title": f"t {iid}",
        "parent": parent,
        "assign": assign,
        "slot": "1",
        "spec": spec,
    }


def ev(op, iid, by="최동호", **kw):
    return {"at": AT, "by": by, "op": op, "id": iid, **kw}


def test_normalize_id():
    assert normalize_id("2-17") == "Part2-17"
    assert normalize_id(" part2-17.1 ") == "Part2-17.1"
    assert normalize_id("Part2-17") == "Part2-17"
    assert normalize_id("2") == "Part2"


def test_replay_builds_every_status():
    items = replay(
        [
            add("Part1-1"),
            add("Part1-2"),
            add("Part1-3"),
            add("Part1-4"),
            ev("start", "Part1-2"),
            ev("start", "Part1-3"),
            ev("block", "Part1-3", text="계약 없음"),
            ev("start", "Part1-4"),
            ev("done", "Part1-4"),
            ev("drop", "Part1-1", by="kth9245", text="빼는 순서 1"),
        ]
    )
    assert [items[f"Part1-{k}"].status for k in (1, 2, 3, 4)] == ["뺌", "진행중", "막힘", "완료"]
    assert items["Part1-2"].owner == "최동호" and items["Part1-2"].since == AT
    assert items["Part1-3"].entries == [(AT, "최동호", "block", "계약 없음")]


def test_start_refuses_someone_elses_item_until_take():
    items = replay([add("Part2-17"), ev("start", "Part2-17", by="황승주")])
    with pytest.raises(Refused, match="황승주.*--take"):
        apply(items, "start", "최동호", "2-17")
    e = apply(items, "start", "최동호", "2-17", take=True, at=AT)
    assert e == {
        "at": AT,
        "by": "최동호",
        "op": "start",
        "id": "Part2-17",
        "take": True,
        "from": "황승주",
    }


def test_start_refuses_own_running_and_closed_items():
    items = replay(
        [
            add("Part2-1"),
            add("Part2-2"),
            ev("start", "Part2-1"),
            ev("start", "Part2-2"),
            ev("done", "Part2-2"),
        ]
    )
    with pytest.raises(Refused, match="이미 내가 진행중"):
        apply(items, "start", "최동호", "2-1")
    with pytest.raises(Refused, match="완료"):
        apply(items, "start", "최동호", "2-2")
    assert apply(items, "start", "최동호", "2-2", take=True, at=AT)["from"] is None


def test_owner_restarts_blocked_item():
    items = replay([add("Part2-1"), ev("start", "Part2-1"), ev("block", "Part2-1", text="x")])
    assert apply(items, "start", "최동호", "2-1", at=AT)["op"] == "start"


def test_done_needs_children_closed_and_owner_or_take():
    items = replay(
        [
            add("Part2-17"),
            add("Part2-17.1", parent="Part2-17"),
            ev("start", "Part2-17", by="황승주"),
        ]
    )
    with pytest.raises(Refused, match="Part2-17.1"):
        apply(items, "done", "황승주", "2-17")
    items = replay(
        [
            add("Part2-17"),
            add("Part2-17.1", parent="Part2-17"),
            ev("start", "Part2-17", by="황승주"),
            ev("done", "Part2-17.1"),
        ]
    )
    assert items["Part2-17.1"].owner == "최동호"  # done straight from 예정 sets the owner
    with pytest.raises(Refused, match="황승주 담당"):
        apply(items, "done", "최동호", "2-17")
    assert apply(items, "done", "최동호", "2-17", take=True, at=AT)["take"] is True


def test_add_numbers_children_and_new_top_level_items():
    items = replay([add("Part2-17"), add("Part2-20"), add("Part2-17.1", parent="Part2-17")])
    assert next_id(items, "Part2-17") == "Part2-17.2"
    assert next_id(items, "Part2") == "Part2-21"
    e = apply(items, "add", "황승주", "2-17", text="스텁 Frame", at=AT)
    assert e == {
        "at": AT,
        "by": "황승주",
        "op": "add",
        "id": "Part2-17.2",
        "title": "스텁 Frame",
        "parent": "Part2-17",
        "assign": None,
        "slot": "1",
        "spec": None,
    }
    top = apply(items, "add", "kth9245", "2", text="통합 버그", assign="최동호", at=AT)
    assert (top["id"], top["parent"], top["slot"]) == ("Part2-21", None, None)
    with pytest.raises(Refused, match="없는 상위"):
        apply(items, "add", "kth9245", "9-9", text="x")
    with pytest.raises(Refused, match="배정"):
        apply(items, "add", "kth9245", "2-17", text="x", assign="철수")


def test_text_ops_need_text_and_block_needs_my_running_item():
    items = replay(
        [
            add("Part2-1"),
            add("Part2-2"),
            ev("start", "Part2-1", by="황승주"),
            ev("start", "Part2-2"),
            ev("done", "Part2-2"),
        ]
    )
    with pytest.raises(Refused, match="내용"):
        apply(items, "decide", "최동호", "2-1", text="  ")
    with pytest.raises(Refused, match="진행중인 항목이 아님"):
        apply(items, "block", "최동호", "2-1", text="막힘")
    with pytest.raises(Refused, match="완료"):
        apply(items, "drop", "kth9245", "2-2", text="뺌")
    with pytest.raises(Refused, match="없는 번호"):
        apply(items, "note", "최동호", "2-99", text="x")


def test_text_is_collapsed_to_one_line():
    items = replay([add("Part2-1")])
    e = apply(items, "decide", "최동호", "2-1", text="watch_point/sea를\n  hold로 ", at=AT)
    assert e["text"] == "watch_point/sea를 hold로"
    assert apply(items, "add", "최동호", "2-1", text="a\nb", at=AT)["title"] == "a b"


def test_name_outside_team_is_refused():
    items = replay([add("Part2-1")])
    for name in ("", "dongho", "철수"):
        with pytest.raises(Refused, match="GIT_NAMES"):
            apply(items, "start", name, "2-1")


def test_event_time_is_kst_by_default():
    e = apply(replay([add("Part2-1")]), "note", "최동호", "2-1", text="x")
    assert e["at"].endswith("+09:00") and len(e["at"]) == 25


def test_parse_log_names_bad_line():
    with pytest.raises(ValueError, match="2번째 줄"):
        parse_log(dump_event(add("Part1-1")) + "\n{oops\n")


def test_replay_names_bad_record():
    with pytest.raises(ValueError, match="1번째 기록"):
        replay([ev("start", "Part9-9")])


def test_dump_event_keeps_korean_and_key_order():
    line = dump_event(ev("note", "Part2-1", text="한글"))
    assert line.startswith('{"at": "2026-10-10T12:00:00+09:00", "by": "최동호", "op": "note"')
    assert "한글" in line
