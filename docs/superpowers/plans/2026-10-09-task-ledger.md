# Task Ledger Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `scripts/task.py`로 09 문서 6절 번호표 항목의 시작·완료·하위 항목·막힘·작업 중 결정을 기록하고, 기록만 담은 커밋을 origin/main에 즉시 push해 세 사람이 같은 작업판(`tasks/NOW.md`)을 보게 한다.

**Architecture:** 정본은 덧붙이기만 하는 `tasks/log.jsonl`. 쓰기 명령은 매번 origin/main의 로그를 다시 읽어 상태를 계산하고(`tools/tasks.py`), 검사를 통과하면 이벤트 한 줄을 붙이고 NOW.md를 다시 만들어(`tools/tasks_view.py`), 임시 index로 origin/main 위에 두 파일만 바꾼 커밋을 만들어 push한다(`tools/gitpush.py`). 거절되면 최신 로그로 처음부터 다시 한다. `tools/ledger.py`가 이 셋을 묶어 CLI(`scripts/task.py`)와 `new_action.py`에 제공한다.

**Tech Stack:** Python 3.11+ 표준 라이브러리만(json, dataclasses, subprocess, tempfile), git 저수준 명령(read-tree, hash-object, update-index, write-tree, commit-tree), pytest, bash(ship.sh).

**Spec:** `docs/superpowers/specs/2026-10-09-task-ledger-design.md` (결정 0012·0013·0014)

## Global Constraints

- 시각: 사람이 읽는 시각은 전부 KST. 이벤트 `at`은 `shared.kst.now_kst().isoformat(timespec="seconds")` → `2026-10-10T12:03:15+09:00`. 기계 시간대(`date.today()`, `time.localtime`)를 쓰지 않는다(결정 0012).
- 팀 명단: `TEAM = ("kth9245", "황승주", "최동호")`. 명단 밖 이름의 쓰기는 거부하고 `git config user.name <한글 이름>`을 안내한다.
- 상태는 정확히 `예정` · `진행중` · `막힘` · `완료` · `뺌`.
- 이벤트 키 순서: `at, by, op, id` 다음에 op별 필드. `json.dumps(..., ensure_ascii=False)`.
- 기록 push가 바꾸는 경로는 `tasks/log.jsonl`, `tasks/NOW.md` 둘뿐. 작업 폴더·실제 index·HEAD·로컬 브랜치는 건드리지 않는다.
- `tools/`·`shared/`는 표준 라이브러리만. 액션 아닌 `.py`는 200줄 이하. ruff line-length 100.
- subprocess로 텍스트를 주고받을 때는 `text=True, encoding="utf-8"`(한글).
- TDD(결정 0014): 각 Task는 실패 테스트 → 실패 확인 → 구현 → 통과 → 커밋. 작업 위치는 이 세션의 worktree(브랜치 `infra/rolecall-idea-revision`). push는 Task 9에서 사람 확인 뒤에만.
- 테스트 실행: `uv run pytest -q <경로>`.

## Review Focus

1. 제목·내용에 줄바꿈이나 연속 공백이 들어온 경우 → 한 줄로 합쳐 저장한다(NOW.md 목록이 깨지지 않게). Task 2 `test_text_is_collapsed_to_one_line`.
2. origin의 `tasks/log.jsonl`에 손으로 고친 깨진 줄·없는 번호를 가리키는 기록이 있는 경우 → 모든 명령이 traceback 대신 "n번째 줄/기록"을 말하고 exit 1. Task 2 `test_parse_log_names_bad_line`·`test_replay_names_bad_record`, Task 5 `test_corrupt_log_is_reported_not_traceback`.
3. 저장소 하위 폴더나 다른 worktree에서 `task.py`를 실행하는 경우 → `git rev-parse --show-toplevel`로 루트를 찾아 정상 동작. Task 5 `test_show_from_subdirectory`.
4. `new_action.py --root`가 git 저장소의 최상위가 아닌 경우(테스트 임시 폴더, 다른 저장소 안의 하위 폴더) → 엉뚱한 저장소에 fetch·push하지 않고 경고만. Task 6 `test_claim_skips_ledger_when_root_is_not_repo_top`.
5. `git config user.name`이 비었거나 영문 아이디인 경우 → 기록 거부 + 고칠 명령 안내. Task 2 `test_name_outside_team_is_refused`, Task 5 `test_name_outside_team_refused`.

---

### Task 1: KST 기준 시각 (결정 0012 반영)

**Files:**
- Create: `shared/kst.py`
- Modify: `scripts/decide.py` (import 줄과 `date.today()` 두 곳)
- Modify: `shared/log.py` (Formatter)
- Test: `tests/test_kst.py`(새로), `tests/test_decide.py`, `tests/test_log.py`

**Interfaces:**
- Produces: `shared.kst.KST: timezone`(UTC+9, 이름 "KST"), `shared.kst.now_kst() -> datetime`, `shared.log.KSTFormatter(logging.Formatter)`

- [ ] **Step 1: Write the failing tests**

`tests/test_kst.py`:
```python
from datetime import timedelta

from shared.kst import KST, now_kst


def test_now_kst_has_plus_nine_offset():
    assert KST.utcoffset(None) == timedelta(hours=9)
    assert now_kst().isoformat(timespec="seconds").endswith("+09:00")
```

`tests/test_decide.py` 맨 위 import에 `import os`와 `from shared.kst import now_kst`를 더하고, 기존 `test_accept_sets_status_owner_and_date`의 마지막 줄을 `assert meta["date"] == now_kst().date().isoformat()`로 바꾸고, 파일 끝에 추가:
```python
def test_dates_are_kst_whatever_the_machine_timezone(tmp_path):
    # UTC-12 differs from KST during 00:00-20:59 KST and UTC+14 during 19:00-23:59 KST,
    # so at any moment at least one of the two runs catches a machine-local date.
    (tmp_path / "decisions" / "log").mkdir(parents=True)
    for i, tz in enumerate(("Etc/GMT+12", "Etc/GMT-14"), 1):
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "new", f"t{i}", "--root", str(tmp_path)],
            env={**os.environ, "TZ": tz},
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, r.stderr
        p = next((tmp_path / "decisions" / "log").glob(f"{i:04d}-*.md"))
        meta, _ = parse(p.read_text(encoding="utf-8"))
        assert meta["date"] == now_kst().date().isoformat(), tz
```

`tests/test_log.py` 끝에 추가(맨 위 import에 `import time`, `from shared.log import FORMAT, KSTFormatter`):
```python
def test_formatter_writes_kst_even_when_machine_is_utc(monkeypatch):
    monkeypatch.setenv("TZ", "UTC")
    time.tzset()
    try:
        rec = logging.LogRecord("kdth.x", logging.INFO, __file__, 1, "hi", None, None)
        rec.created, rec.msecs = 0.0, 0.0
        out = KSTFormatter(FORMAT).format(rec)
        assert out.startswith("1970-01-01 09:00:00,000+0900 I kdth.x: hi")
    finally:
        monkeypatch.undo()
        time.tzset()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest -q tests/test_kst.py tests/test_decide.py tests/test_log.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'shared.kst'`(세 파일 모두 import 단계에서).

- [ ] **Step 3: Write the implementation**

`shared/kst.py`:
```python
"""KST (UTC+9, no daylight saving) for every human-visible time (decision 0012).

Use this instead of the machine's local time: teammates' WSL may run in UTC.
"""

from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9), "KST")


def now_kst() -> datetime:
    return datetime.now(KST)
```

`scripts/decide.py`: `from datetime import date` 줄을 지우고, `from pathlib import Path` 뒤에 추가:
```python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.kst import now_kst  # noqa: E402
```
`cmd_new`의 `date=date.today().isoformat()`를 `date=now_kst().date().isoformat()`로, `cmd_accept`의 `f"date: {date.today().isoformat()}"`를 `f"date: {now_kst().date().isoformat()}"`로 바꾼다.

`shared/log.py`: `import os` 뒤에 `from datetime import datetime`, `from pathlib import Path` 뒤에 `from shared.kst import KST`를 넣고, `ROOT = ...` 줄 다음에 추가:
```python
class KSTFormatter(logging.Formatter):
    """asctime in KST whatever the machine timezone (decision 0012)."""

    def formatTime(self, record, datefmt=None):
        t = datetime.fromtimestamp(record.created, KST)
        return t.strftime("%Y-%m-%d %H:%M:%S") + f",{int(record.msecs):03d}+0900"
```
`setup_logging` 안의 `fmt = logging.Formatter(FORMAT)`를 `fmt = KSTFormatter(FORMAT)`로 바꾼다.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest -q tests/test_kst.py tests/test_decide.py tests/test_log.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add shared/kst.py shared/log.py scripts/decide.py tests/test_kst.py tests/test_decide.py tests/test_log.py
git commit -m "decision 0012: KST for decision dates and log timestamps (shared/kst.py), independent of machine timezone"
```

---

### Task 2: 기록 모델 — 다시 읽기와 검사 (`tools/tasks.py`)

**Files:**
- Create: `tools/tasks.py`
- Test: `tests/test_tasks.py`

**Interfaces:**
- Consumes: `shared.kst.now_kst`
- Produces:
  - `TEAM: tuple[str, ...]`, `CLOSED = ("완료", "뺌")`, `TOP_RE`(`Part\d+`)
  - `class Refused(Exception)`
  - `@dataclass Item(id, title, parent=None, assign=None, owner=None, status="예정", slot=None, spec=None, since="", entries=[])` — entries는 `(at, by, kind, text)` 튜플 목록, kind ∈ note/decide/block/drop
  - `normalize_id(raw: str) -> str`
  - `parse_log(text: str) -> list[dict]` (깨진 줄 → `ValueError("tasks/log.jsonl n번째 줄 ...")`)
  - `dump_event(ev: dict) -> str`
  - `replay(events: list[dict]) -> dict[str, Item]` (잘못된 기록 → `ValueError("... n번째 기록 ...")`)
  - `children(items, parent: str) -> list[Item]`
  - `next_id(items, parent: str) -> str`
  - `apply(items, op, by, target, text="", take=False, assign=None, at=None) -> dict` (새 이벤트, items는 바꾸지 않음, 거부는 `Refused`)

- [ ] **Step 1: Write the failing tests**

`tests/test_tasks.py`:
```python
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
        with pytest.raises(Refused, match="git config user.name"):
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest -q tests/test_tasks.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'tools.tasks'`

- [ ] **Step 3: Write the implementation**

`tools/tasks.py`:
```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest -q tests/test_tasks.py`
Expected: PASS (14 tests)

- [ ] **Step 5: Commit**

```bash
git add tools/tasks.py tests/test_tasks.py
git commit -m "task ledger: replay and validate model (tools/tasks.py)"
```

---

### Task 3: 작업판 그리기 (`tools/tasks_view.py`)

**Files:**
- Create: `tools/tasks_view.py`
- Test: `tests/test_tasks_view.py`

**Interfaces:**
- Consumes: `tools.tasks.TEAM, CLOSED, Item, children`
- Produces:
  - `HEADER: str`
  - `hhmm(at: str) -> str` (`"2026-10-10T12:03:15+09:00"` → `"10/10 12:03"`)
  - `line(it: Item, items) -> str`
  - `render_now(items, last_at: str) -> str` (NOW.md 전체)
  - `render_show(items, me: str) -> str` (터미널 요약)
  - `render_item(items, iid: str) -> str` (항목 하나 + 하위 + 메모·결정)

- [ ] **Step 1: Write the failing tests**

`tests/test_tasks_view.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest -q tests/test_tasks_view.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'tools.tasks_view'`

- [ ] **Step 3: Write the implementation**

`tools/tasks_view.py`:
```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest -q tests/test_tasks_view.py`
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add tools/tasks_view.py tests/test_tasks_view.py
git commit -m "task ledger: NOW.md and terminal views (tools/tasks_view.py)"
```

---

### Task 4: tasks/만 바꾼 커밋을 origin/main에 즉시 push (`tools/gitpush.py`)

**Files:**
- Create: `tools/gitpush.py`
- Create: `tests/ledger_fixtures.py` (pytest가 모으지 않는 도우미, Task 5·6도 씀)
- Test: `tests/test_gitpush.py`

**Interfaces:**
- Produces:
  - `LOG = "tasks/log.jsonl"`, `NOW = "tasks/NOW.md"`
  - `class OfflineError(Exception)`, `class PushFailed(Exception)`
  - `fetch(root: Path) -> bool`
  - `read_remote_file(root: Path, path: str) -> str` (없으면 `""`)
  - `fetch_age_min(root: Path) -> int | None`
  - `commit_files(root: Path, base: str, files: dict[str, str], message: str) -> str`
  - `changed_paths(root: Path, base: str, sha: str) -> set[str]`
  - `push_tasks(root: Path, build: Callable[[str], tuple[str, str, str]], retries: int = 5) -> str` — `build(old_log) -> (new_log, now_md, message)`, 재시도마다 최신 로그로 다시 호출, push한 커밋 sha 반환
- Produces (tests): `tests.ledger_fixtures.sh(cwd, *args) -> str`, `make_repo(tmp, name="kth9245") -> (remote, work)`, `clone(tmp, remote, dirname, name) -> Path`, `remote_file(remote, path) -> str`, `seed(work, events: list[dict]) -> None`

- [ ] **Step 1: Write the fixtures and the failing tests**

`tests/ledger_fixtures.py`:
```python
"""Bare remote + clone repos for task ledger tests (no test_ prefix: not collected)."""

import subprocess
from pathlib import Path


def sh(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout


def config(repo: Path, name: str) -> None:
    sh(repo, "config", "user.name", name)
    sh(repo, "config", "user.email", "t@t")


def make_repo(tmp: Path, name: str = "kth9245") -> tuple[Path, Path]:
    remote, work = tmp / "remote.git", tmp / "work"
    sh(tmp, "init", "-q", "--bare", "-b", "main", str(remote))
    work.mkdir()
    sh(work, "init", "-q", "-b", "main")
    config(work, name)
    (work / "README.md").write_text("r\n")
    sh(work, "add", "-A")
    sh(work, "commit", "-qm", "base")
    sh(work, "remote", "add", "origin", str(remote))
    sh(work, "push", "-q", "-u", "origin", "main")
    return remote, work


def clone(tmp: Path, remote: Path, dirname: str, name: str) -> Path:
    d = tmp / dirname
    sh(tmp, "clone", "-q", str(remote), str(d))
    config(d, name)
    return d


def remote_file(remote: Path, path: str) -> str:
    r = subprocess.run(
        ["git", "show", f"main:{path}"],
        cwd=remote,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return r.stdout if r.returncode == 0 else ""


def seed(work: Path, events: list[dict]) -> None:
    """Put a log on origin/main through the real push path."""
    from tools.gitpush import push_tasks
    from tools.tasks import dump_event

    text = "".join(dump_event(e) + "\n" for e in events)
    push_tasks(work, lambda old: (text, "now\n", "task: seed"))
```

`tests/test_gitpush.py`:
```python
import pytest

from tests.ledger_fixtures import clone, make_repo, remote_file, sh
from tools.gitpush import (
    OfflineError,
    changed_paths,
    commit_files,
    fetch,
    fetch_age_min,
    push_tasks,
)
from tools.tasks import Refused


def test_push_changes_only_tasks_files_and_leaves_checkout_alone(tmp_path):
    remote, work = make_repo(tmp_path)
    (work / "README.md").write_text("dirty\n")
    (work / "new.txt").write_text("untracked\n")
    head, status = sh(work, "rev-parse", "HEAD"), sh(work, "status", "--porcelain")
    sha = push_tasks(work, lambda old: (old + "a\n", "now\n", "task: x"))
    assert sh(work, "rev-parse", "HEAD") == head
    assert sh(work, "status", "--porcelain") == status
    assert sh(remote, "rev-parse", "main").strip() == sha
    assert remote_file(remote, "tasks/log.jsonl") == "a\n"
    assert remote_file(remote, "tasks/NOW.md") == "now\n"
    assert changed_paths(work, sha + "~1", sha) == {"tasks/log.jsonl", "tasks/NOW.md"}
    assert "task: x" in sh(remote, "log", "-1", "--format=%s", "main")


def test_retry_rebuilds_from_the_newer_remote_log(tmp_path):
    remote, work = make_repo(tmp_path)
    mate = clone(tmp_path, remote, "mate", "황승주")
    seen = []

    def build(old):
        seen.append(old)
        if len(seen) == 1:  # a teammate pushes between our fetch and our push
            push_tasks(mate, lambda o: (o + "mate\n", "n\n", "task: mate"))
        return old + "me\n", "n\n", "task: me"

    push_tasks(work, build)
    assert seen == ["", "mate\n"]
    assert remote_file(remote, "tasks/log.jsonl") == "mate\nme\n"


def test_offline_raises_and_pushes_nothing(tmp_path):
    remote, work = make_repo(tmp_path)
    sh(work, "remote", "set-url", "origin", str(tmp_path / "nowhere.git"))
    with pytest.raises(OfflineError):
        push_tasks(work, lambda old: (old + "a\n", "n\n", "task: x"))
    assert remote_file(remote, "tasks/log.jsonl") == ""


def test_refusal_inside_build_pushes_nothing(tmp_path):
    remote, work = make_repo(tmp_path)

    def build(old):
        raise Refused("no")

    with pytest.raises(Refused):
        push_tasks(work, build)
    assert remote_file(remote, "tasks/log.jsonl") == ""


def test_changed_paths_sees_files_outside_tasks(tmp_path):
    _, work = make_repo(tmp_path)
    assert fetch(work)
    base = sh(work, "rev-parse", "origin/main").strip()
    sha = commit_files(work, base, {"tasks/log.jsonl": "a\n", "README.md": "x\n"}, "m")
    assert changed_paths(work, base, sha) == {"tasks/log.jsonl", "README.md"}


def test_fetch_age_after_fetch_is_zero(tmp_path):
    _, work = make_repo(tmp_path)
    assert fetch(work)
    assert fetch_age_min(work) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest -q tests/test_gitpush.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'tools.gitpush'`

- [ ] **Step 3: Write the implementation**

`tools/gitpush.py`:
```python
"""Commit tasks/ files straight onto origin/main and push (decision 0013). Stdlib only.

The commit is built with git plumbing on a temporary index, so the work tree, the real
index, HEAD and local branches are never touched. Only LOG and NOW may change; anything
else aborts before the push.
"""

import os
import subprocess
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

LOG, NOW = "tasks/log.jsonl", "tasks/NOW.md"
ALLOWED = {LOG, NOW}


class OfflineError(Exception):
    """origin is unreachable or missing."""


class PushFailed(Exception):
    """origin kept rejecting the push."""


def _git(root: Path, *args: str, stdin: str | None = None, env: dict | None = None) -> str:
    r = subprocess.run(
        ["git", *args],
        cwd=root,
        input=stdin,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if r.returncode != 0:
        raise subprocess.CalledProcessError(r.returncode, ["git", *args], r.stdout, r.stderr)
    return r.stdout


def fetch(root: Path) -> bool:
    r = subprocess.run(["git", "fetch", "-q", "origin", "main"], cwd=root, capture_output=True)
    return r.returncode == 0


def read_remote_file(root: Path, path: str) -> str:
    r = subprocess.run(
        ["git", "show", f"origin/main:{path}"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return r.stdout if r.returncode == 0 else ""


def fetch_age_min(root: Path) -> int | None:
    """Minutes since the last fetch (FETCH_HEAD mtime); None if never fetched."""
    p = Path(_git(root, "rev-parse", "--git-path", "FETCH_HEAD").strip())
    p = p if p.is_absolute() else root / p
    return int((time.time() - p.stat().st_mtime) // 60) if p.exists() else None


def commit_files(root: Path, base: str, files: dict[str, str], message: str) -> str:
    """A commit whose tree is base's tree with `files` replaced. Not pushed."""
    with tempfile.TemporaryDirectory() as d:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(d) / "index")}
        _git(root, "read-tree", base, env=env)
        for path, text in files.items():
            blob = _git(root, "hash-object", "-w", "--stdin", stdin=text).strip()
            _git(root, "update-index", "--add", "--cacheinfo", f"100644,{blob},{path}", env=env)
        tree = _git(root, "write-tree", env=env).strip()
    return _git(root, "commit-tree", tree, "-p", base, "-m", message).strip()


def changed_paths(root: Path, base: str, sha: str) -> set[str]:
    return set(_git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", base, sha).split())


def push_tasks(root: Path, build: Callable[[str], tuple[str, str, str]], retries: int = 5) -> str:
    """build(old_log) -> (new_log, now_md, message). Called again with the fresh remote log
    after every rejected push, so validation and numbering always see the newest state."""
    last = ""
    for _ in range(retries):
        if not fetch(root):
            raise OfflineError("origin에 연결할 수 없음")
        base = _git(root, "rev-parse", "origin/main").strip()
        new_log, now_md, message = build(read_remote_file(root, LOG))
        sha = commit_files(root, base, {LOG: new_log, NOW: now_md}, message)
        extra = changed_paths(root, base, sha) - ALLOWED
        if extra:
            raise RuntimeError(f"tasks/ 밖 파일이 바뀜: {sorted(extra)}")
        r = subprocess.run(
            ["git", "push", "-q", "origin", f"{sha}:refs/heads/main"],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if r.returncode == 0:
            return sha
        last = r.stderr.strip()
    raise PushFailed(f"push가 {retries}번 거절됨: {last}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest -q tests/test_gitpush.py`
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add tools/gitpush.py tests/ledger_fixtures.py tests/test_gitpush.py
git commit -m "task ledger: push tasks/-only commits onto origin/main with plumbing (tools/gitpush.py)"
```

---

### Task 5: 기록 동작 묶음과 CLI (`tools/ledger.py`, `scripts/task.py`)

**Files:**
- Create: `tools/ledger.py`
- Create: `scripts/task.py`
- Test: `tests/test_task_cli.py`

**Interfaces:**
- Consumes: Task 2 `apply, parse_log, replay, dump_event, normalize_id, Refused, Item`; Task 3 `render_now, render_show, render_item`; Task 4 `push_tasks, fetch, fetch_age_min, read_remote_file, LOG, NOW, OfflineError, PushFailed`
- Produces:
  - `tools.ledger.git_name(root: Path) -> str`
  - `tools.ledger.is_repo_top(root: Path) -> bool`
  - `tools.ledger.load(root: Path) -> tuple[dict[str, Item], str | None]` (두 번째 값: 오프라인 안내 또는 None)
  - `tools.ledger.write(root, op, target, by, text="", take=False, assign=None) -> tuple[dict, str, dict[str, Item]]` (이벤트, 커밋 sha, 기록 뒤 상태)
  - `tools.ledger.start_for_spec(root, spec_id, by, take=False) -> str | None` (Task 6이 씀)
  - `tools.ledger.seed(root, text) -> int`
  - CLI: `uv run python scripts/task.py <show|start|done|add|block|decide|note|drop|seed> [번호|파일] ["내용"] [--take] [--assign 이름] [--all]`

- [ ] **Step 1: Write the failing tests**

`tests/test_task_cli.py`:
```python
import subprocess
import sys
from pathlib import Path

from tests.ledger_fixtures import clone, make_repo, remote_file, seed, sh
from tools.gitpush import push_tasks

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "task.py"
ITEM = {
    "at": "2026-10-10T12:00:00+09:00",
    "by": "kth9245",
    "op": "add",
    "id": "Part2-17",
    "title": "틱 루프",
    "parent": None,
    "assign": "최동호",
    "slot": "1",
    "spec": "SIM-08",
}


def task(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def setup(tmp_path, name="최동호"):
    remote, work = make_repo(tmp_path, name)
    seed(work, [ITEM])
    return remote, work


def last_event(remote) -> str:
    return remote_file(remote, "tasks/log.jsonl").splitlines()[-1]


def test_start_pushes_and_leaves_checkout_alone(tmp_path):
    remote, work = setup(tmp_path)
    (work / "README.md").write_text("dirty\n")
    head, status = sh(work, "rev-parse", "HEAD"), sh(work, "status", "--porcelain")
    r = task(work, "start", "2-17")
    assert r.returncode == 0, r.stderr
    assert "Part2-17 시작: 최동호" in r.stdout and "KST (main " in r.stdout
    assert '"op": "start"' in last_event(remote) and '"by": "최동호"' in last_event(remote)
    assert "- **Part2-17** 틱 루프 — 최동호" in remote_file(remote, "tasks/NOW.md")
    assert (sh(work, "rev-parse", "HEAD"), sh(work, "status", "--porcelain")) == (head, status)


def test_second_person_is_refused_until_take(tmp_path):
    remote, work = setup(tmp_path)
    mate = clone(tmp_path, remote, "mate", "황승주")
    assert task(work, "start", "2-17").returncode == 0
    r = task(mate, "start", "2-17")
    assert r.returncode == 1 and "최동호" in r.stderr and "--take" in r.stderr
    r = task(mate, "start", "2-17", "--take")
    assert r.returncode == 0, r.stderr
    assert '"from": "최동호"' in last_event(remote)


def test_start_of_someone_elses_assignment_warns(tmp_path):
    remote, _ = setup(tmp_path)
    mate = clone(tmp_path, remote, "mate", "황승주")
    r = task(mate, "start", "2-17")
    assert r.returncode == 0 and "배정: 최동호" in r.stdout


def test_name_outside_team_refused(tmp_path):
    remote, work = setup(tmp_path, name="철수")
    r = task(work, "start", "2-17")
    assert r.returncode == 1 and "git config user.name" in r.stderr
    assert len(remote_file(remote, "tasks/log.jsonl").splitlines()) == 1


def test_offline_fails_without_writing(tmp_path):
    remote, work = setup(tmp_path)
    sh(work, "remote", "set-url", "origin", str(tmp_path / "nowhere.git"))
    r = task(work, "start", "2-17")
    assert r.returncode == 1 and "기록 못 올림" in r.stderr
    assert len(remote_file(remote, "tasks/log.jsonl").splitlines()) == 1


def test_add_and_done_rules(tmp_path):
    _, work = setup(tmp_path)
    r = task(work, "add", "2-17", "스텁 Frame")
    assert r.returncode == 0 and "Part2-17.1 스텁 Frame 추가" in r.stdout
    assert task(work, "start", "2-17").returncode == 0
    r = task(work, "done", "2-17")
    assert r.returncode == 1 and "Part2-17.1" in r.stderr
    assert task(work, "done", "2-17.1").returncode == 0
    assert task(work, "done", "2-17").returncode == 0


def test_show_from_subdirectory(tmp_path):
    _, work = setup(tmp_path)
    (work / "sub").mkdir()
    assert task(work, "start", "2-17").returncode == 0
    assert task(work, "note", "2-17", "스텁 목록은 engine.py 머리").returncode == 0
    assert task(work, "decide", "2-17", "스텁은 예시 JSON").returncode == 0
    out = task(work / "sub", "show").stdout
    assert "진행중" in out and "**Part2-17**" in out and "스텁은 예시 JSON" in out
    assert "메모: 스텁 목록은 engine.py 머리" in task(work / "sub", "show", "2-17").stdout
    assert "# 지금 작업판" in task(work / "sub", "show", "--all").stdout


def test_seed_only_once(tmp_path):
    _, work = setup(tmp_path)
    f = tmp_path / "seed.jsonl"
    f.write_text(
        '{"at": "2026-10-10T12:00:00+09:00", "by": "kth9245", "op": "add", '
        '"id": "Part1-1", "title": "x", "parent": null, "assign": null, '
        '"slot": null, "spec": null}\n',
        encoding="utf-8",
    )
    r = task(work, "seed", str(f))
    assert r.returncode == 1 and "이미 기록" in r.stderr


def test_seed_pushes_log_and_board(tmp_path):
    remote, work = make_repo(tmp_path)
    f = tmp_path / "seed.jsonl"
    f.write_text(
        '{"at": "2026-10-10T12:00:00+09:00", "by": "kth9245", "op": "add", '
        '"id": "Part1-1", "title": "계약", "parent": null, "assign": "kth9245", '
        '"slot": "밤", "spec": null}\n',
        encoding="utf-8",
    )
    r = task(work, "seed", str(f))
    assert r.returncode == 0 and "항목 1개" in r.stdout
    assert "### kth9245" in remote_file(remote, "tasks/NOW.md")


def test_corrupt_log_is_reported_not_traceback(tmp_path):
    _, work = setup(tmp_path)
    push_tasks(work, lambda old: (old + "{oops\n", "n\n", "task: break"))
    r = task(work, "show")
    assert r.returncode == 1 and "2번째 줄" in r.stderr and "Traceback" not in r.stderr
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest -q tests/test_task_cli.py`
Expected: FAIL — `scripts/task.py`가 없어 CLI가 exit 2(`can't open file`)를 내므로 returncode·출력 단언이 전부 실패. 마지막 테스트는 `push_tasks` import는 되지만 같은 이유로 실패.

- [ ] **Step 3: Write `tools/ledger.py`**

```python
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


def start_for_spec(root: Path, spec_id: str, by: str, take: bool = False) -> str | None:
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
    return it.id


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
```

- [ ] **Step 4: Write `scripts/task.py`**

```python
"""Task ledger CLI (decision 0013). Run anywhere inside the repo or a worktree.

uv run python scripts/task.py show [번호] [--all]
uv run python scripts/task.py start|done <번호> [--take]
uv run python scripts/task.py add <상위 번호|PartN> "제목" [--assign 이름]
uv run python scripts/task.py block|decide|note|drop <번호> "내용"
uv run python scripts/task.py seed <파일>          (리드, 처음 한 번)
"""

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.gitpush import NOW, OfflineError, PushFailed, read_remote_file  # noqa: E402
from tools.ledger import git_name, load, seed, write  # noqa: E402
from tools.tasks import Refused, normalize_id  # noqa: E402
from tools.tasks_view import render_item, render_show  # noqa: E402

VERB = {
    "start": "시작",
    "done": "완료",
    "add": "추가",
    "block": "막힘",
    "decide": "결정 기록",
    "note": "메모",
    "drop": "뺌",
}


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(1)


def repo_root() -> Path:
    r = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, encoding="utf-8"
    )
    if r.returncode != 0:
        fail("git 저장소 안에서 실행하세요")
    return Path(r.stdout.strip())


def show(root: Path, me: str, target: str | None, all_: bool) -> None:
    items, note = load(root)
    if note:
        print(note)
    if all_:
        print(read_remote_file(root, NOW) or "(기록 없음)", end="")
    elif target:
        tid = normalize_id(target)
        if tid not in items:
            fail(f"없는 번호: {tid}")
        print(render_item(items, tid), end="")
    else:
        print(render_show(items, me), end="")


def main() -> None:
    ap = argparse.ArgumentParser(description="할 일 기록 (결정 0013)")
    ap.add_argument("cmd", choices=["show", "seed", *VERB])
    ap.add_argument("target", nargs="?")
    ap.add_argument("text", nargs="?", default="")
    ap.add_argument("--take", action="store_true")
    ap.add_argument("--assign")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    root = repo_root()
    me = git_name(root)
    try:
        if a.cmd == "show":
            return show(root, me, a.target, a.all)
        if not a.target:
            fail("번호가 필요함")
        if a.cmd == "seed":
            n = seed(root, Path(a.target).read_text(encoding="utf-8"))
            return print(f"seed: 항목 {n}개를 main에 올림")
        ev, sha, items = write(root, a.cmd, a.target, me, a.text, a.take, a.assign)
    except Refused as e:
        fail(f"거부: {e}")
    except (OfflineError, PushFailed) as e:
        fail(f"기록 못 올림({e}). 네트워크를 확인하고 다시 실행하세요")
    except ValueError as e:
        fail(f"기록 파일 오류: {e}. 리드에게 알리세요")
    title = f" {ev['title']}" if a.cmd == "add" else ""
    print(f"{ev['id']}{title} {VERB[a.cmd]}: {me} {ev['at'][11:16]} KST (main {sha[:7]})")
    assign = items[ev["id"]].assign
    if a.cmd == "start" and assign not in (None, me):
        print(f"참고: 배정: {assign} — 채팅에 알리세요")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest -q tests/test_task_cli.py tests/test_tasks.py tests/test_tasks_view.py tests/test_gitpush.py`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add tools/ledger.py scripts/task.py tests/test_task_cli.py
git commit -m "task ledger: scripts/task.py CLI (show/start/done/add/block/decide/note/drop/seed) via tools/ledger.py"
```

---

### Task 6: `new_action.py`가 연결된 번호표 항목을 먼저 시작

**Files:**
- Modify: `scripts/new_action.py` (import 3줄, `claim_ledger` 함수, `existing` 분기에서 `replace_row` 앞 호출, 새 행 생성 뒤 안내 1줄)
- Test: `tests/test_new_action.py`

**Interfaces:**
- Consumes: `tools.ledger.start_for_spec(root, spec_id, by, take) -> str | None`, `tools.tasks.Refused`, `tools.gitpush.OfflineError, PushFailed`
- Produces: `new_action.py`가 `예정` 행을 가져가거나 `--take`할 때, 그 SPEC id에 연결된 항목이 남의 진행중이면 SPEC·파일을 바꾸지 않고 exit 1. 연결이 없거나 오프라인이면 경고만 하고 계속.

- [ ] **Step 1: Write the failing tests**

`tests/test_new_action.py` 끝에 추가(맨 위 import에 `from tests.ledger_fixtures import clone, make_repo, remote_file, seed`):
```python
LINKED = {
    "at": "2026-10-10T12:00:00+09:00",
    "by": "kth9245",
    "op": "add",
    "id": "Part2-1",
    "title": "tracking predict_tracks",
    "parent": None,
    "assign": "최동호",
    "slot": "1",
    "spec": "TRK-01",
}


def planned_repo(tmp_path, root_sub=""):
    remote, work = make_repo(tmp_path, "최동호")
    root = work / root_sub if root_sub else work
    mod = make_module(root)
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "tracking",
            "predict_tracks",
            "x",
            "--planned",
            "--root",
            str(root),
            "--owner",
            "최동호",
        ],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    seed(work, [LINKED])
    return remote, work, root, mod


def claim(root, owner, *extra):
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "tracking",
            "predict_tracks",
            "x",
            *extra,
            "--root",
            str(root),
            "--owner",
            owner,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_claim_starts_linked_plan_item(tmp_path):
    remote, _, root, mod = planned_repo(tmp_path)
    r = claim(root, "최동호")
    assert r.returncode == 0, r.stderr
    assert "Part2-1 시작" in r.stdout
    last = remote_file(remote, "tasks/log.jsonl").splitlines()[-1]
    assert '"op": "start"' in last and '"by": "최동호"' in last
    assert (mod / "actions" / "predict_tracks.py").exists()


def test_claim_refused_when_someone_else_started_the_item(tmp_path):
    from tools.ledger import write

    remote, _, root, mod = planned_repo(tmp_path)
    write(clone(tmp_path, remote, "mate", "황승주"), "start", "Part2-1", "황승주")
    before = (mod / "SPEC.md").read_text(encoding="utf-8")
    r = claim(root, "최동호")
    assert r.returncode == 1 and "황승주" in r.stderr
    assert (mod / "SPEC.md").read_text(encoding="utf-8") == before
    assert not (mod / "actions" / "predict_tracks.py").exists()


def test_claim_skips_ledger_when_root_is_not_repo_top(tmp_path):
    remote, _, root, mod = planned_repo(tmp_path, root_sub="inner")
    r = claim(root, "최동호")
    assert r.returncode == 0, r.stderr
    assert "경고: 할 일 기록 못 올림" in r.stderr
    assert len(remote_file(remote, "tasks/log.jsonl").splitlines()) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest -q tests/test_new_action.py`
Expected: 새 테스트 3개 FAIL — `test_claim_starts_linked_plan_item`은 stdout에 "Part2-1 시작" 없음, `test_claim_refused...`는 returncode 0, `test_claim_skips...`는 "경고" 없음. 기존 테스트는 PASS.

- [ ] **Step 3: Write the implementation**

`scripts/new_action.py`의 `from tools.spec import ...` 줄 뒤에:
```python
from tools.gitpush import OfflineError, PushFailed  # noqa: E402
from tools.ledger import start_for_spec  # noqa: E402
from tools.tasks import Refused  # noqa: E402
```
`git_user` 함수 뒤에:
```python
def claim_ledger(root: Path, spec_id: str, owner: str, take: bool) -> None:
    """Start the plan item linked to this SPEC row first, so two people cannot both claim it."""
    try:
        item = start_for_spec(root, spec_id, owner, take)
    except Refused as e:
        fail(f"할 일 기록이 거부함: {e}")
    except (OfflineError, PushFailed) as e:
        print(f"경고: 할 일 기록 못 올림({e}). 나중에 `task.py start <번호>`", file=sys.stderr)
        return
    if item:
        print(f"할 일 기록: {item} 시작")
    else:
        print("할 일 기록: 이 SPEC 행과 연결된 번호표 항목 없음 (필요하면 task.py add)")
```
`main()`의 `if existing is not None:` 분기에서 두 `fail(...)` 검사 바로 뒤, `row = replace(` 앞에:
```python
        claim_ledger(Path(a.root), existing.id, owner, a.take)
```
새 행(`append_row(... "진행중")`) 분기의 마지막 `print("다음: ...")` 뒤에:
```python
    print("번호표 항목이면 `uv run python scripts/task.py start <번호>`도 실행하세요.")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest -q tests/test_new_action.py`
Expected: PASS (기존 6개 + 새 3개). 기존 테스트의 `--root`는 git 저장소가 아니라 경고 경로를 탄다.

- [ ] **Step 5: Commit**

```bash
git add scripts/new_action.py tests/test_new_action.py
git commit -m "new_action: start the linked plan item in the ledger before claiming a SPEC row"
```

---

### Task 7: ship 중에 기록 커밋이 끼어들면 다시 push

**Files:**
- Modify: `scripts/ship.sh` (끝의 `git push ... || fail` 한 줄을 재시도 루프로)
- Test: `tests/test_ship.py`

**Interfaces:**
- Produces: ship의 push가 거절됐을 때 새로 들어온 커밋들이 `tasks/`만 바꿨으면 rebase 후 테스트 없이 다시 push(최대 3번). 다른 경로가 섞였으면 지금처럼 `push 실패` 메시지로 exit 1.

- [ ] **Step 1: Write the failing tests**

`tests/test_ship.py` 끝에 추가:
```python
def _push_mid_ship(work: Path, mate: Path, path: str) -> None:
    """Replace the clone's smoke step with a push of `path` from `mate`: a push landing mid-ship."""
    git(work, "update-index", "--skip-worktree", "scripts/smoke.py")
    (work / "scripts/smoke.py").write_text(
        "import pathlib, subprocess\n"
        f"m = pathlib.Path({str(mate)!r})\n"
        f"p = m / {path!r}\n"
        "p.parent.mkdir(parents=True, exist_ok=True)\n"
        "p.write_text('x\\n')\n"
        "g = ['git', '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'core.hooksPath=/dev/null']\n"
        f"subprocess.run(g + ['add', {path!r}], cwd=m, check=True)\n"
        "subprocess.run(g + ['commit', '-qm', 'mid-ship'], cwd=m, check=True)\n"
        "subprocess.run(g + ['push', '-q', 'origin', 'HEAD:main'], cwd=m, check=True)\n"
    )


def _ship_with_mid_push(tmp_path, path):
    remote, work = make_clone(tmp_path)
    mate = tmp_path / "mate"
    git(tmp_path, "clone", "-q", str(remote), str(mate))
    _push_mid_ship(work, mate, path)
    (work / "knowledge/inbox/mine.md").write_text("x\n")
    git(work, "add", "knowledge/inbox/mine.md")
    git(work, "commit", "-q", "-m", "mine note")
    return work, run_ship(work)


def test_ship_retries_when_only_task_records_landed_mid_ship(tmp_path):
    work, r = _ship_with_mid_push(tmp_path, "tasks/log.jsonl")
    assert r.returncode == 0, r.stdout + r.stderr
    log = git(work, "log", "--oneline", "origin/main")
    assert "mine note" in log and "mid-ship" in log


def test_ship_stops_when_other_files_landed_mid_ship(tmp_path):
    _, r = _ship_with_mid_push(tmp_path, "knowledge/inbox/mate.md")
    assert r.returncode == 1 and "push 실패" in r.stdout + r.stderr
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest -q tests/test_ship.py -k mid_ship`
Expected: `test_ship_retries_when_only_task_records_landed_mid_ship` FAIL(returncode 1, "push 실패"). `test_ship_stops...`는 PASS(지금 동작과 같음).

- [ ] **Step 3: Write the implementation**

`scripts/ship.sh`의 이 줄을:
```bash
git push -q origin HEAD:main || fail "push 실패. 누군가 먼저 push했을 수 있습니다. 다시 ship 하세요."
```
다음으로 바꾼다:
```bash
# A task.py record (tasks/ only, decision 0013) may land while tests run: rebase over it and retry.
pushed=0
for _ in 1 2 3; do
  if git push -q origin HEAD:main 2>/dev/null; then pushed=1; break; fi
  git fetch -q origin || break
  [ -n "$(git diff --name-only HEAD...origin/main | grep -v '^tasks/')" ] && break
  git rebase -q origin/main || fail "rebase 충돌(기록 커밋 위). 'git status' 확인 후 다시 ship."
done
[ "$pushed" = 1 ] || fail "push 실패. 누군가 먼저 push했을 수 있습니다. 다시 ship 하세요."
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest -q tests/test_ship.py`
Expected: PASS (기존 + 새 2개)

- [ ] **Step 5: Commit**

```bash
git add scripts/ship.sh tests/test_ship.py
git commit -m "ship.sh: when only tasks/ records landed mid-ship, rebase and push again"
```

---

### Task 8: 보호 파일, 규칙, 스킬

**Files:**
- Modify: `tools/guard/edits.py` (PROTECTED에 2줄)
- Modify: `tests/test_guard.py` (`test_protected_files` 목록에 2줄)
- Modify: `tests/test_agent_config.py` (`test_skills_shared_via_symlink`의 이름 목록에 `"task"`)
- Create: `.agents/skills/task/SKILL.md` (`.claude/skills`는 `.agents/skills`로의 심볼릭 링크)
- Modify: `.agents/skills/new-action/SKILL.md` (6단계 뒤 한 줄)
- Modify: `AGENTS.md` ("담당" 절 끝 막힘 문장, 새 "할 일 기록" 절)

**Interfaces:**
- Produces: guard가 `tasks/log.jsonl`·`tasks/NOW.md` 편집을 거부. 에이전트가 읽는 규칙과 `task` 스킬.

- [ ] **Step 1: Write the failing tests**

`tests/test_guard.py`의 `test_protected_files` 튜플에 `"tasks/log.jsonl",`과 `"tasks/NOW.md",`를 `"tasks/BOARD.md",` 다음에 넣는다.
`tests/test_agent_config.py`의 `for name in ("new-action", "new-module", "kb-save", "decide", "ship"):`를 `for name in ("new-action", "new-module", "kb-save", "decide", "ship", "task"):`로 바꾼다.

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest -q tests/test_guard.py tests/test_agent_config.py`
Expected: FAIL — `test_protected_files`(`AssertionError: tasks/log.jsonl`), `test_skills_shared_via_symlink`(`FileNotFoundError: .../task/SKILL.md`)

- [ ] **Step 3: Write the implementation**

`tools/guard/edits.py` PROTECTED의 `"tasks/BOARD.md",` 다음에:
```python
("tasks/log.jsonl",)
("tasks/NOW.md",)
```

`.agents/skills/task/SKILL.md`:
```markdown
---
name: task
description: Record work on the numbered plan (docs/research/09 §6, Part<n>-<k>). Use when starting, finishing, blocking or splitting a plan item, helping on someone else's item, or making a small decision mid-work.
---

All commands: `uv run python scripts/task.py ...`. Each write is pushed to main at once (decision 0013).

1. Before work: `task.py show` (one item with notes: `task.py show <번호>`; whole board: `--all`).
2. Start: `task.py start <번호>` (an action: `new_action.py` starts its linked item). Someone else's item in progress: `task.py add <번호> "<제목>"`, then start the new sub-item. Take over only after telling them in chat: `--take`.
3. After `scripts/ship.sh` succeeds: `task.py done <번호>`. Open sub-items block done.
4. Stuck for 5 minutes: `task.py block <번호> "<증상>"` and post the number in chat.
5. A decision that stays inside my item: `task.py decide <번호> "<결정>"`. Contracts, another person's module or policy: `/decide`, then `task.py decide <번호> "결정 NNNN 참조"`.
6. Note for whoever continues: `task.py note <번호> "<메모>"`. Item cut (09 §7): `task.py drop <번호> "<이유>"`.
7. Never edit `tasks/log.jsonl` or `tasks/NOW.md` by hand. "기록 못 올림" = network; retry later. "거부" = read the reason; do not work around it.
```

`.agents/skills/new-action/SKILL.md`의 6단계 줄(`6. Set the SPEC.md row status to `완료`.`) 다음에:
```markdown
7. After `scripts/ship.sh` succeeds: `uv run python scripts/task.py done <번호>` (task skill).
```

`AGENTS.md`: "담당" 절의 `남의 영역을 고치면 담당자에게 알린다. 막히면 5분 안에 "막힘: 번호, 함수, 증상"을 채팅에.`를 `남의 영역을 고치면 담당자에게 알린다.`로 바꾸고, `## 액션 규칙` 제목 바로 앞에 다음 절을 넣는다:
```markdown
## 할 일 기록 (결정 0013) — `uv run python scripts/task.py`, 자세히는 task 스킬
- 처음 한 번 `git config user.name <한글 이름>`(리드는 kth9245). 팀 명단 밖 이름은 기록이 거부된다.
- 작업 전 `task.py show`. 번호표 항목을 시작하면 `task.py start <번호>`(액션은 new_action.py가 대신). 남이 진행중이면 `task.py add <번호> "<제목>"`으로 하위 항목을 만들어 그것을 start.
- ship 성공 뒤 `task.py done <번호>`. 막히면 5분 안에 `task.py block <번호> "<증상>"`, 채팅에도 번호.
- 작업 중 결정: 내 항목 안에서 끝나는 선택은 `task.py decide <번호> "<결정>"`, 계약·남의 모듈·정책을 바꾸면 `/decide`.
- 현황 기준은 `task.py show`·`tasks/NOW.md`(SPEC 상태 칸은 액션 파일 관리용). `tasks/log.jsonl`·`NOW.md`는 task.py만 쓴다.

```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest -q tests/test_guard.py tests/test_agent_config.py tests/test_docs.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/guard/edits.py tests/test_guard.py tests/test_agent_config.py .agents/skills/task/SKILL.md .agents/skills/new-action/SKILL.md AGENTS.md
git commit -m "task ledger: protect tasks/log.jsonl and NOW.md, AGENTS.md rules, task skill"
```

---

### Task 9: 전체 검사, 처음 채우기 목록, main 반영 (사람 확인 두 번)

**Files:**
- Create (저장소 밖, 이 세션 scratchpad): `make_seed.py`, `seed.jsonl`
- 저장소 변경 없음(원격에 `tasks/log.jsonl`·`tasks/NOW.md`가 seed 커밋으로 생김)

- [ ] **Step 1: 전체 테스트**

Run: `uv run pytest -q tests modules`
Expected: PASS(실패 0). 실패하면 superpowers:systematic-debugging으로 원인부터.

- [ ] **Step 2: 처음 채우기 목록 만들기**

scratchpad에 `make_seed.py`:
```python
"""One-off: docs/research/09 §6 tables -> seed.jsonl for `task.py seed` (not committed)."""

import json
import re
import sys
from pathlib import Path

doc = Path(sys.argv[1]).read_text(encoding="utf-8")
sec = doc[doc.index("## 6. 사람별 계획") : doc.index("## 7. 빼는 순서")]
SPEC = {
    **{f"Part2-{k}": f"SIM-{k + 4:02d}" for k in range(1, 6)},
    "Part2-6": "SNS-02",
    **{f"Part2-{k}": f"SFT-{k - 6:02d}" for k in range(7, 10)},
    **{f"Part2-{k}": f"RT-{k - 9:02d}" for k in range(10, 17)},
    "Part2-20": "SIM-04",
    **{f"Part3-{k}": f"PLY-{k:02d}" for k in range(1, 10)},
    "Part3-15": "PLY-10",
}


def assign(iid: str) -> str | None:
    p, k = (int(x) for x in re.findall(r"\d+", iid))
    if p == 1 or (p == 3 and 10 <= k <= 14):
        return "kth9245"
    if p == 2:
        return "최동호" if k <= 6 or k >= 17 else "황승주"
    return "황승주" if k <= 9 else None


AT, AT_13 = "2026-10-09T23:00:00+09:00", "2026-10-09T02:28:09+09:00"
out = []
for row in sec.splitlines():
    cells = [c.strip() for c in row.split("|")]
    if len(cells) < 4 or cells[1].startswith("~~") or not re.match(r"Part\d+-\d+", cells[1]):
        continue
    iid = re.match(r"Part\d+-\d+", cells[1]).group()
    slot = re.match(r"[^(]*", cells[-2]).group().strip() or None
    out.append(
        {
            "at": AT,
            "by": "kth9245",
            "op": "add",
            "id": iid,
            "title": cells[2],
            "parent": None,
            "assign": assign(iid),
            "slot": slot,
            "spec": SPEC.get(iid),
        }
    )
for op in ("start", "done"):  # Part1-3 finished on 10/9 (commit 553d308)
    out.append(
        {
            "at": AT_13,
            "by": "kth9245",
            "op": op,
            "id": "Part1-3",
            **({"take": False, "from": None} if op == "start" else {"take": False}),
        }
    )
Path(sys.argv[2]).write_text(
    "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in out), encoding="utf-8"
)
for e in out[:-2]:
    print(
        f"{e['id']:9} {e['assign'] or '누구나':7} {e['slot'] or '-':5} {e['spec'] or '':7} {e['title']}"
    )
```
Run: `uv run python <scratchpad>/make_seed.py docs/research/09-rolecall-implementation-foundation.md <scratchpad>/seed.jsonl`
Expected: 약 48줄(Part1-6·1-8 제외). 번호·배정·통합·SPEC id가 설계 문서 2.5절과 같은지 눈으로 확인.

참고: `add`의 at(23:00)이 Part1-3 완료 기록의 at(02:28)보다 늦다. 상태 계산은 줄 순서를 따르므로 결과는 맞다. NOW.md의 완료 시각은 02:28로 보인다.

- [ ] **Step 3: 사람 확인 1 — 목록**

목록 전체와 "이미 끝난 것 = Part1-3뿐"을 리드에게 보여 주고, 배정·완료 표시를 고칠 것이 있는지 묻는다. 고치면 `make_seed.py`를 고쳐 다시 만든다.

- [ ] **Step 4: 사람 확인 2 — main 반영**

리드에게 "이 브랜치의 커밋(설계, 결정 0012~0014, 이 구현)을 `scripts/ship.sh`로 main에 올리고, 이어서 `task.py seed`로 첫 기록을 올릴까요?"를 묻는다. 승인 뒤:
Run: `scripts/ship.sh`
Expected: `[ship] 완료: ...`

- [ ] **Step 5: seed와 확인**

Run: `uv run python scripts/task.py seed <scratchpad>/seed.jsonl`
Expected: `seed: 항목 48개를 main에 올림`(개수는 Step 2 출력과 같음)
Run: `uv run python scripts/task.py show`
Expected: 진행중 `(없음)`, 내 예정(kth9245)에 Part1-1·1-2·1-4… 목록, 오류 없음.
Run: `git fetch -q origin && git show origin/main:tasks/NOW.md | head -20`
Expected: `# 지금 작업판`과 `## 완료` 아래 `**Part1-3**`.
