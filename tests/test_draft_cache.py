"""AI draft cache (Part1-5, decision 0028): one cached Play per demo sentence, named sha256(prompt).
Fails after an edit to modules/play/draft_prompt.md or the demo operation's name/purpose/area/zone:
rerun `uv run python scripts/make_draft_cache.py` (GROK_KEY in .env, internet).
"""

import hashlib
import json
from pathlib import Path

import pytest

from contracts.models import Play, Scenario
from modules.play import check_operation
from modules.play.actions.build_draft_prompt import build_draft_prompt

ROOT = Path(__file__).resolve().parent.parent
SC = Scenario.model_validate_json(
    (ROOT / "demo" / "scenarios" / "baengnyeong_night.json").read_text(encoding="utf-8")
)
SENTENCES = json.loads((ROOT / "demo" / "draft_sentences.json").read_text(encoding="utf-8"))
CACHE = ROOT / "demo" / "plays" / "cache"


@pytest.mark.parametrize("s", SENTENCES, ids=lambda s: s["id"])
def test_each_demo_sentence_has_a_cached_draft_with_the_expected_check(s):
    prompt = build_draft_prompt(s["text"], SC.operation)
    path = CACHE / f"{hashlib.sha256(prompt.encode('utf-8')).hexdigest()}.json"
    play = Play.model_validate_json(path.read_text(encoding="utf-8"))
    assert play.origin == "ai_draft" and not play.approved and not play.template
    spec = next(v for v in SC.vehicles if v.domain in play.domains)
    op = SC.operation.model_copy(
        update={"assign": {spec.id: play.id}, "reserve": {}, "switches": []}
    )
    codes = [i.code for i in check_operation(op, {play.id: play}, {spec.id: spec}).issues]
    assert codes == ([] if s["expect"] == "ok" else [s["expect"]])
