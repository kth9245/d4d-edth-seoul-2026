"""PLY-09 draft_play: 문장 → AI 플레이 초안(결정 0028 Grok). 캐시 우선, 미스면 1회 호출·스키마 밖이면 1회 재요청, 실패 시 standby 템플릿
프롬프트는 리드의 build_draft_prompt(PLY-12), 호출 규약은 tasks Part3-9 리드 메모.
SPEC: modules/play/SPEC.md#PLY-09
"""

import hashlib
import json
from pathlib import Path

import httpx
from pydantic import ValidationError

from contracts.models import Operation, Play
from modules.play.actions.build_draft_prompt import build_draft_prompt
from modules.play.actions.load_play import load_play

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "demo" / "plays" / "cache"
ENV = ROOT / ".env"
FALLBACK = ROOT / "demo" / "plays" / "standby.json"
URL = "https://api.x.ai/v1/chat/completions"
MODEL = "grok-4.7"  # reasoning model: 40-280 s per call on 10/10
FIXED = {"origin": "ai_draft", "approved": False, "template": False}


def _key() -> str:
    lines = ENV.read_text(encoding="utf-8").splitlines() if ENV.exists() else []
    return next((ln.split("=", 1)[1].strip() for ln in lines if ln.startswith("GROK_KEY=")), "")


def _ask(prompt: str, key: str) -> Play:
    r = httpx.post(
        URL,
        timeout=360,
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        },
    )
    r.raise_for_status()
    reply = json.loads(r.json()["choices"][0]["message"]["content"])
    return Play.model_validate({**reply["play"], **FIXED})


def draft_play(text: str, op: Operation) -> Play:
    prompt = build_draft_prompt(text, op)
    path = CACHE / f"{hashlib.sha256(prompt.encode('utf-8')).hexdigest()}.json"
    if path.exists():
        return Play.model_validate_json(path.read_text(encoding="utf-8"))
    key = _key()
    for _ in range(2 if key else 0):  # one call, one retry when the reply is outside the schema
        try:
            play = _ask(prompt, key)
        except (ValidationError, KeyError, TypeError, json.JSONDecodeError):
            continue
        except httpx.HTTPError:
            break
        path.parent.mkdir(parents=True, exist_ok=True)
        body = json.dumps(play.model_dump(mode="json"), ensure_ascii=False, indent=1)
        path.write_text(body + "\n", encoding="utf-8")
        return play
    return load_play(FALLBACK)
