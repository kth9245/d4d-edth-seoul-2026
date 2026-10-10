"""PLY-08 list_templates: demo/plays/*.json 중 template=True 플레이만 파일 이름 순으로 돌려준다
SPEC: modules/play/SPEC.md#PLY-08
"""

from pathlib import Path

from contracts.models import Play
from modules.play.actions.load_play import load_play

PLAYS = Path(__file__).resolve().parents[3] / "demo" / "plays"


def list_templates() -> list[Play]:
    plays = (load_play(p) for p in sorted(PLAYS.glob("*.json")))
    return [p for p in plays if p.template]
