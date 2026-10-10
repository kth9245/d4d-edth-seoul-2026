"""Part1-5: AI draft cache for the demo sentences (decision 0028). Needs GROK_KEY in .env and internet.

For each sentence in demo/draft_sentences.json: build_draft_prompt with the demo operation, one Grok call,
the reply's "play" saved as demo/plays/cache/<sha256(prompt)>.json (origin=ai_draft, approved=False).
The demo only reads these files (policy 1); this script is not on the demo path.
tests/test_draft_cache.py checks the files and each sentence's expected check result.

Run: uv run python scripts/make_draft_cache.py [sentence id ...]
"""

import hashlib
import json
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT)]

from contracts.models import Play, Scenario  # noqa: E402
from modules.play.actions.build_draft_prompt import build_draft_prompt  # noqa: E402
from shared.log import get_logger, setup_logging  # noqa: E402

URL = "https://api.x.ai/v1/chat/completions"
MODEL = "grok-4.7"  # reasoning model: 40-280 s per call on 10/10
CACHE = ROOT / "demo" / "plays" / "cache"
SCENARIO = ROOT / "demo" / "scenarios" / "baengnyeong_night.json"
SENTENCES = ROOT / "demo" / "draft_sentences.json"


def _key() -> str:
    env = ROOT / ".env"
    lines = env.read_text(encoding="utf-8").splitlines() if env.exists() else []
    key = next((ln.split("=", 1)[1].strip() for ln in lines if ln.startswith("GROK_KEY=")), "")
    if not key:
        raise SystemExit("GROK_KEY가 .env에 없습니다")
    return key


def _ask(prompt: str, key: str) -> dict:
    r = httpx.post(
        URL,
        timeout=600,
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        },
    )
    r.raise_for_status()
    return json.loads(r.json()["choices"][0]["message"]["content"])


def main(ids: list[str]) -> None:
    setup_logging("make_draft_cache")
    log = get_logger("scripts.make_draft_cache")
    op = Scenario.model_validate_json(SCENARIO.read_text(encoding="utf-8")).operation
    key = _key()
    CACHE.mkdir(parents=True, exist_ok=True)
    for s in json.loads(SENTENCES.read_text(encoding="utf-8")):
        if ids and s["id"] not in ids:
            continue
        prompt = build_draft_prompt(s["text"], op)
        t0 = time.monotonic()
        reply = _ask(prompt, key)
        fixed = {"origin": "ai_draft", "approved": False, "template": False}
        play = Play.model_validate({**reply["play"], **fixed})
        path = CACHE / f"{hashlib.sha256(prompt.encode('utf-8')).hexdigest()}.json"
        body = json.dumps(play.model_dump(mode="json"), ensure_ascii=False, indent=1)
        path.write_text(body + "\n", encoding="utf-8")
        secs = time.monotonic() - t0
        log.info(
            "%s %.0fs -> %s, not_in_text=%s", s["id"], secs, path.name, reply.get("not_in_text")
        )


if __name__ == "__main__":
    main(sys.argv[1:])
