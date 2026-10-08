"""SPEC.md table helpers shared by guard, checks and scripts (stdlib only)."""

import re
from dataclasses import astuple, dataclass
from pathlib import Path

SPEC_HEADER = (
    "| id | 액션 | 입력 | 출력 | 완료 기준 | 담당 | 상태 |\n|---|---|---|---|---|---|---|\n"
)
PREFIX_RE = re.compile(r"<!--\s*prefix:\s*([A-Z]+)\s*-->")


@dataclass
class SpecRow:
    id: str
    action: str
    inputs: str
    outputs: str
    done: str
    owner: str
    status: str


def parse_spec(text: str) -> tuple[str | None, list[SpecRow]]:
    m = PREFIX_RE.search(text)
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.startswith("|") or len(cells) != 7:
            continue
        if cells[0] == "id" or set(cells[0]) <= set("-: "):
            continue
        rows.append(SpecRow(*cells))
    return (m.group(1) if m else None), rows


def spec_actions(spec_path: Path) -> set[str]:
    if not spec_path.exists():
        return set()
    return {r.action for r in parse_spec(spec_path.read_text(encoding="utf-8"))[1]}


def next_id(prefix: str, rows: list[SpecRow]) -> str:
    nums = [int(r.id.split("-")[-1]) for r in rows if r.id.split("-")[-1].isdigit()]
    return f"{prefix}-{max(nums, default=0) + 1:02d}"


def _line(row: SpecRow) -> str:
    cells = [str(c).replace("|", "/").replace("\n", " ") for c in astuple(row)]
    return "| " + " | ".join(cells) + " |\n"


def append_row(spec_path: Path, row: SpecRow) -> None:
    text = spec_path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    spec_path.write_text(text + _line(row), encoding="utf-8")


def replace_row(spec_path: Path, row: SpecRow) -> None:
    """Rewrite the one table line whose id matches row.id (owner/status takeover)."""
    lines = spec_path.read_text(encoding="utf-8").splitlines(keepends=True)
    for i, line in enumerate(lines):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) == 7 and cells[0] == row.id:
            lines[i] = _line(row)
            break
    else:
        raise KeyError(row.id)
    spec_path.write_text("".join(lines), encoding="utf-8")
