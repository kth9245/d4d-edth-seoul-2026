"""Decision records. AI runs `new` (proposal). Only humans run `accept`.

Usage: python scripts/decide.py new "<title>" [--modules a,b]
       python scripts/decide.py accept NNNN --by <name>
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

TEMPLATE = """---
id: {id}
title: {title}
status: 제안            # 제안 / 확정 / 폐기
decided_by: null        # 확정 시 사람 이름
date: {date}
modules: [{modules}]
supersedes: null
---
## 결정

## 이유

## 버린 대안

## 영향
"""


def slugify(title: str) -> str:
    s = re.sub(r"\s+", "-", title.strip().lower())
    s = re.sub(r"[^0-9a-z가-힣-]", "", s).strip("-")[:40]
    return s or "decision"


def cmd_new(log: Path, title: str, modules: str) -> None:
    nums = [int(p.name[:4]) for p in log.glob("[0-9][0-9][0-9][0-9]-*.md")]
    nid = f"{max(nums, default=0) + 1:04d}"
    mods = ", ".join(m.strip() for m in modules.split(",") if m.strip())
    path = log / f"{nid}-{slugify(title)}.md"
    path.write_text(TEMPLATE.format(id=nid, title=title, date=date.today().isoformat(),
                                    modules=mods), encoding="utf-8")
    print(f"제안 생성: {path}  (확정은 사람이 `python scripts/decide.py accept {nid} --by 이름`)")


def cmd_accept(log: Path, nid: str, by: str) -> None:
    matches = list(log.glob(f"{nid}-*.md"))
    if not matches:
        print(f"결정 {nid} 를 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)
    p = matches[0]
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"^status:.*$", "status: 확정", text, count=1, flags=re.M)
    text = re.sub(r"^decided_by:.*$", f"decided_by: {by}", text, count=1, flags=re.M)
    text = re.sub(r"^date:.*$", f"date: {date.today().isoformat()}", text, count=1, flags=re.M)
    p.write_text(text, encoding="utf-8")
    print(f"확정: {p}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("title")
    n.add_argument("--modules", default="")
    n.add_argument("--root", default=argparse.SUPPRESS)
    acc = sub.add_parser("accept")
    acc.add_argument("id")
    acc.add_argument("--by", required=True)
    acc.add_argument("--root", default=argparse.SUPPRESS)
    a = ap.parse_args()
    log = Path(a.root) / "decisions" / "log"
    log.mkdir(parents=True, exist_ok=True)
    if a.cmd == "new":
        cmd_new(log, a.title, a.modules)
    else:
        cmd_accept(log, a.id, a.by)


if __name__ == "__main__":
    main()
