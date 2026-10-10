"""AI draft cache (Part1-5, decision 0028): one cached Role per demo sentence, named sha256(prompt).
Fails after an edit to modules/role/draft_prompt.md or the demo operation's name/purpose/area/zone:
rerun `uv run python scripts/make_draft_cache.py` (GROK_KEY in .env, internet).
"""

import hashlib
import json
from pathlib import Path

import pytest

from contracts.models import Role
from modules.role import check_operation
from modules.role.actions.build_draft_prompt import build_draft_prompt
from modules.sim import load_scenario_json

ROOT = Path(__file__).resolve().parent.parent
# through the loader so capabilities come from the ontology (decision 0038)
SC = load_scenario_json(ROOT / "demo" / "scenarios" / "baengnyeong_night.json")
SENTENCES = json.loads((ROOT / "demo" / "draft_sentences.json").read_text(encoding="utf-8"))
CACHE = ROOT / "demo" / "roles" / "cache"


@pytest.mark.parametrize("s", SENTENCES, ids=lambda s: s["id"])
def test_each_demo_sentence_has_a_cached_draft_with_the_expected_check(s):
    prompt = build_draft_prompt(s["text"], SC.operation)
    path = CACHE / f"{hashlib.sha256(prompt.encode('utf-8')).hexdigest()}.json"
    role = Role.model_validate_json(path.read_text(encoding="utf-8"))
    assert role.origin == "ai_draft" and not role.approved and not role.template
    spec = next(v for v in SC.vehicles if v.domain in role.domains)
    op = SC.operation.model_copy(
        update={"assign": {spec.id: role.id}, "reserve": {}, "switches": []}
    )
    codes = [i.code for i in check_operation(op, {role.id: role}, {spec.id: spec}).issues]
    assert codes == ([] if s["expect"] == "ok" else [s["expect"]])
