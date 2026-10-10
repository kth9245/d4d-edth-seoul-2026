"""Regenerate BOARD/INDEX files and the AGENTS.md policy block. Never blocks commits."""

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.frontmatter import parse  # noqa: E402
from tools.spec import parse_spec  # noqa: E402

BEGIN, END = "<!-- POLICY:BEGIN -->", "<!-- POLICY:END -->"
GENERATED = "<!-- 자동 생성 파일 (scripts/sync_docs.py). 직접 수정하지 마세요. -->\n"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def build_board(root: Path) -> str:
    lines = [GENERATED, "# 작업판\n", "| 모듈 | id | 액션 | 담당 | 상태 |", "|---|---|---|---|---|"]
    for spec in sorted((root / "modules").glob("*/SPEC.md")):
        for r in parse_spec(_read(spec))[1]:
            lines.append(f"| {spec.parent.name} | {r.id} | {r.action} | {r.owner} | {r.status} |")
    return "\n".join(lines) + "\n"


def build_knowledge_index(root: Path) -> str:
    groups: dict[str, list[str]] = {}
    for card in sorted((root / "knowledge" / "cards").glob("*.md")):
        m, _ = parse(_read(card))
        tags = " ".join(f"`{t}`" for t in m.get("tags") or [])
        line = f"- [{m.get('title', card.stem)}](cards/{card.name}) — {m.get('summary', '')} {tags} ({m.get('confidence', '?')})"
        for mod in m.get("modules") or ["general"]:
            groups.setdefault(mod, []).append(line)
    out = [GENERATED, "# 지식 목차\n"]
    for mod in sorted(groups):
        out += [f"## {mod}", *groups[mod], ""]
    return "\n".join(out)


def build_decision_index(root: Path) -> str:
    out = [
        GENERATED,
        "# 결정 목록\n",
        "| id | 제목 | 상태 | 결정자 | 모듈 |",
        "|---|---|---|---|---|",
    ]
    for doc in sorted((root / "decisions" / "log").glob("*.md")):
        m, _ = parse(_read(doc))
        mods = ", ".join(m.get("modules") or [])
        out.append(
            f"| [{m.get('id', doc.stem)}](log/{doc.name}) | {m.get('title', '')} | "
            f"{m.get('status', '')} | {m.get('decided_by') or ''} | {mods} |"
        )
    return "\n".join(out) + "\n"


def apply_policy(agents_text: str, policy_text: str) -> str:
    if BEGIN not in agents_text or END not in agents_text:
        return agents_text
    body = "\n".join(
        line for line in policy_text.strip().splitlines() if not line.startswith("# ")
    ).strip()
    head, rest = agents_text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return f"{head}{BEGIN}\n{body}\n{END}{tail}"


def _write(p: Path, text: str) -> None:
    if p.parent.exists() and (not p.exists() or _read(p) != text):
        p.write_text(text, encoding="utf-8")


def sync(root: Path) -> bool:
    _write(root / "tasks" / "BOARD.md", build_board(root))
    _write(root / "knowledge" / "INDEX.md", build_knowledge_index(root))
    _write(root / "decisions" / "INDEX.md", build_decision_index(root))
    agents, policy = root / "AGENTS.md", root / "decisions" / "POLICY.md"
    if not (agents.exists() and policy.exists()):
        return False
    new = apply_policy(_read(agents), _read(policy))
    if new == _read(agents):
        return False
    agents.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", action="store_true")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    a = ap.parse_args()
    if sync(Path(a.root)) and a.stage:
        subprocess.run(["git", "add", "AGENTS.md"], cwd=a.root, check=False)


if __name__ == "__main__":
    main()
