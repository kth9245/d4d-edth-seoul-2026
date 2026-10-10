"""Decision 0055 (user 10/10, plan A): the 24h raiders cross the coast patrols and are caught. Runs the real tick loop."""

from pathlib import Path

from contracts.models import Decision, TickInputs
from modules.gateway.engine import init_engine, tick
from modules.sim import load_scenario_json

DAY = Path(__file__).resolve().parent.parent / "demo" / "scenarios" / "baengnyeong_24h.json"


def test_24h_patrols_catch_both_raiders_crossing_the_coast():  # user 10/10 A: they cross the patrol at T+17
    day = load_scenario_json(DAY)
    es, seen = init_engine(day), {}
    while es.t_ms < day.operation.started_ms + 18 * 60_000:
        es, f = tick(es, TickInputs())
        for t in f.targets:
            coast = [v for v in t.seen_by if v in day.operation.rotation]
            if coast and t.id not in seen:
                seen[t.id] = (f.t_ms - day.operation.started_ms) / 60_000
    assert set(seen) >= {"e_drone", "e_usv"} and all(16 <= m <= 18 for m in seen.values()), seen


def _answer(
    r,
) -> str:  # observe, pick the first tracker once then skip, skip the patrols, hold when idle
    ids = [c.id for c in r.choices]
    if "-track-" in r.id:
        return ids[0] if r.id.endswith("-track-0") and len(ids) > 2 else "track_skip"
    pref = ("observe_", "focus_skip", "cover_skip", "hold_")
    return next(i for p in pref for i in ids if i.startswith(p))


def test_24h_raid_asks_one_question_at_a_time_in_order():  # user 10/10: step-by-step raid cards
    day = load_scenario_json(DAY)
    es, asked, n, prev = init_engine(day), [], 0, {}
    while es.t_ms < day.operation.started_ms + 30 * 60_000:
        open_q = [
            r for r in es.reports if r.id.startswith("raid-e") and r.choices and not r.resolved_ms
        ]
        assert len(open_q) <= 1, [r.id for r in open_q]
        for r in open_q:  # 5.3 must not rebuild a raid card
            assert prev.setdefault(r.id, [c.id for c in r.choices]) == [c.id for c in r.choices]
        todo = [
            r for r in es.reports if r.id.startswith("raid-") and r.choices and not r.resolved_ms
        ]
        decs = [Decision(id=f"dec-raid-{n + i}", t_ms=es.t_ms, report_id=r.id, choice_id=_answer(r))
                for i, r in enumerate(todo)]  # fmt: skip
        n += len(decs)
        asked += [r.id for r in todo if r.id.startswith("raid-e")]
        es, _ = tick(es, TickInputs(decisions=decs))
    asked += [r.id for r in es.reports if r.id.endswith("-done")]
    first = asked[0].split("-")[
        1
    ]  # whichever raider was seen first is asked first, the other waits
    other = ({"e_drone", "e_usv"} - {first}).pop()
    flow = [a for a in asked if a.startswith(f"raid-{first}-")]
    assert flow[:2] == [f"raid-{first}-act", f"raid-{first}-track-0"], asked
    assert flow[2].startswith(f"raid-{first}-tact-") and flow[3] == f"raid-{first}-track-1", asked
    assert f"raid-{other}-act" in asked and f"raid-{first}-done" in asked, asked
    assert asked.index(f"raid-{first}-track-1") < asked.index(f"raid-{other}-act"), asked
