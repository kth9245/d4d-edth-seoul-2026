import json
from pathlib import Path

import httpx
import pytest

import modules.play.actions.draft_play as dp
from contracts.models import Play, Scenario
from modules.play.actions.draft_play import draft_play

ROOT = Path(__file__).resolve().parents[3]
OP = Scenario.model_validate_json(
    (ROOT / "demo" / "scenarios" / "baengnyeong_night.json").read_text(encoding="utf-8")
).operation
SENTENCES = json.loads((ROOT / "demo" / "draft_sentences.json").read_text(encoding="utf-8"))
WATCH = json.loads((ROOT / "demo" / "plays" / "watch.json").read_text(encoding="utf-8"))


class FakeReply:
    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        pass

    def json(self):
        return {"choices": [{"message": {"content": json.dumps(self.body)}}]}


def fake_grok(monkeypatch, tmp_path, replies, key="GROK_KEY=test-key"):
    """Point the cache and .env at tmp_path and answer Grok calls from `replies` in order."""
    calls = []
    env = tmp_path / ".env"
    env.write_text(key + "\n", encoding="utf-8")
    monkeypatch.setattr(dp, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(dp, "ENV", env)

    def post(url, **kw):
        calls.append(kw["json"])
        r = replies[len(calls) - 1]
        if isinstance(r, Exception):
            raise r
        return FakeReply(r)

    monkeypatch.setattr(httpx, "post", post)
    return calls


@pytest.mark.parametrize("s", SENTENCES, ids=lambda s: s["id"])
def test_demo_sentences_come_from_the_cache_without_a_call(monkeypatch, s):
    def no_call(*a, **k):
        raise AssertionError("Grok must not be called on a cache hit")

    monkeypatch.setattr(httpx, "post", no_call)
    play = draft_play(s["text"], OP)
    assert isinstance(play, Play)
    assert (play.origin, play.approved, play.template) == ("ai_draft", False, False)


def test_cache_miss_calls_grok_once_marks_ai_draft_and_saves_the_cache(monkeypatch, tmp_path):
    calls = fake_grok(monkeypatch, tmp_path, [{"play": WATCH}])
    play = draft_play("드론 한 대로 표적을 감시해", OP)
    assert len(calls) == 1 and calls[0]["model"] == "grok-4.7"
    assert (play.id, play.origin, play.approved, play.template) == (
        "watch",
        "ai_draft",
        False,
        False,
    )
    assert len(list((tmp_path / "cache").glob("*.json"))) == 1
    assert draft_play("드론 한 대로 표적을 감시해", OP) == play and len(calls) == 1


def test_reply_outside_the_schema_is_asked_again_once(monkeypatch, tmp_path):
    calls = fake_grok(monkeypatch, tmp_path, [{"play": {"id": "x"}}, {"play": WATCH}])
    play = draft_play("드론 한 대로 표적을 감시해", OP)
    assert len(calls) == 2 and play.origin == "ai_draft"


def test_two_bad_replies_give_the_standby_template(monkeypatch, tmp_path):
    calls = fake_grok(monkeypatch, tmp_path, [{"oops": 1}, {"play": {"id": "x"}}])
    play = draft_play("드론 한 대로 표적을 감시해", OP)
    assert len(calls) == 2
    assert (play.id, play.origin, play.template) == ("standby", "human", True)
    assert not (tmp_path / "cache").exists()


def test_no_key_gives_the_standby_template_without_a_call(monkeypatch, tmp_path):
    calls = fake_grok(monkeypatch, tmp_path, [], key="")
    assert draft_play("드론 한 대로 표적을 감시해", OP).id == "standby" and calls == []


def test_network_error_gives_the_standby_template(monkeypatch, tmp_path):
    calls = fake_grok(monkeypatch, tmp_path, [httpx.ConnectError("offline")])
    assert draft_play("드론 한 대로 표적을 감시해", OP).id == "standby" and len(calls) == 1
