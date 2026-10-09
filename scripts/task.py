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
    except subprocess.CalledProcessError as e:
        lines = (e.stderr or "").strip().splitlines()
        fail(f"git 명령 실패: {lines[-1] if lines else e}")
    title = f" {ev['title']}" if a.cmd == "add" else ""
    print(f"{ev['id']}{title} {VERB[a.cmd]}: {me} {ev['at'][11:16]} KST (main {sha[:7]})")
    assign = items[ev["id"]].assign
    if a.cmd == "start" and assign not in (None, me):
        print(f"참고: 배정: {assign} — 채팅에 알리세요")


if __name__ == "__main__":
    main()
