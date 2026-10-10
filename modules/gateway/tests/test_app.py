from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from contracts.models import Frame
from modules import sim
from modules.gateway import create_app
from modules.gateway.tests.test_live import FakeEngine

ROOT = Path(__file__).resolve().parents[3]
SCENARIO = str(ROOT / "demo/scenarios/baengnyeong_night.json")


def fake_app(**kw) -> tuple[TestClient, FakeEngine]:
    eng = FakeEngine()
    ns = SimpleNamespace(
        load_scenario_json=sim.load_scenario_json,  # capabilities from the ontology (decision 0038)
        init_engine=eng.init,
        tick=lambda state, inputs: eng.tick(state, inputs),  # tests may swap eng.tick
    )
    return TestClient(create_app(SCENARIO, engine=ns, period_s=0.01, **kw)), eng


def test_plays_and_operation_come_from_the_scenario():
    client, _ = fake_app()
    assert "track_fast" in [p["id"] for p in client.get("/plays").json()]
    assert client.get("/operation").json()["id"] == "op1"
    assert client.get("/health").json() == {"ok": True}


def test_vehicles_come_from_the_scenario():
    # Part3-14: the editor's operation panel shows each vehicle's domain and home.
    client, _ = fake_app()
    vehicles = client.get("/vehicles").json()
    assert [v["id"] for v in vehicles] == client.get("/operation").json()["vehicle_ids"]
    assert {"domain", "home", "name"} <= set(vehicles[0])


def test_enemies_come_from_the_scenario():
    # Part1-21: the editor's enemy section shows each enemy and the play it follows.
    client, _ = fake_app()
    enemies = client.get("/enemies").json()
    assert [e["id"] for e in enemies] == ["boat1", "fast1", "boat2", "boat3"]  # decision 0036
    plays = {p["id"] for p in client.get("/plays").json()}
    assert all(e["play_id"] in plays for e in enemies)


def test_watch_points_come_from_the_scenario():
    # decision 0047: the live board tells approaching from fleeing by the expected landing point
    client, _ = fake_app()
    got = client.get("/watch_points").json()
    assert [(w["id"], w["radius_m"]) for w in got] == [("landing", 2000.0)]


def test_scenarios_lists_the_demo_operations_with_the_running_one_active():
    # decision 0042: the editor picks one of the demo operations
    client, _ = fake_app()
    got = client.get("/scenarios").json()
    assert [(s["id"], s["active"]) for s in got] == [
        ("baengnyeong_night", True),
        ("baengnyeong_24h", False),
    ]


def test_activate_switches_what_the_editor_endpoints_answer():
    client, _ = fake_app()
    run = client.post("/scenarios/baengnyeong_24h/activate").json()
    assert run["status"] == "paused"
    day = sim.load_scenario_json(str(ROOT / "demo/scenarios/baengnyeong_24h.json"))
    assert client.get("/operation").json()["name"] == day.operation.name
    assert [v["id"] for v in client.get("/vehicles").json()] == [v.id for v in day.vehicles]
    assert [s["active"] for s in client.get("/scenarios").json()] == [False, True]


def test_activate_an_unknown_scenario_is_404():
    client, _ = fake_app()
    assert client.post("/scenarios/nope/activate").status_code == 404
    assert client.get("/operation").json()["name"] == "백령도 야간 해안 경계"


def test_a_broken_catalog_file_is_skipped_and_the_running_operation_still_starts():
    # the night demo must not depend on another operation's file (decision 0042 review)
    land = str(ROOT / "demo/scenarios/baengnyeong_land.json")  # polygons, not a Scenario
    client, _ = fake_app(scenario_paths=[SCENARIO, land])
    assert [s["id"] for s in client.get("/scenarios").json()] == ["baengnyeong_night"]
    assert client.get("/operation").json()["name"] == "백령도 야간 해안 경계"


def test_scenario_paths_replace_the_demo_list():
    client, _ = fake_app(scenario_paths=[SCENARIO])
    assert [s["id"] for s in client.get("/scenarios").json()] == ["baengnyeong_night"]


def test_routes_come_from_the_running_operation():  # decision 0044
    client, _ = fake_app()
    night = {r["id"] for r in client.get("/routes").json()}
    assert {"patrol_a", "square_300"} <= night
    client.post("/scenarios/baengnyeong_24h/activate")
    day = {r["id"] for r in client.get("/routes").json()}
    assert "patrol_a" not in day and "square_300" in day


def test_run_live_then_ws_streams_running_frames():
    client, _ = fake_app()
    with client:
        assert client.post("/run/live?speed=2").json() == {"status": "running", "speed": 2.0}
        with client.websocket_connect("/ws") as ws:
            a = Frame.model_validate(ws.receive_json())
            b = Frame.model_validate(ws.receive_json())
    assert a.run.status == "running"
    assert b.t_ms > a.t_ms


def test_ws_log_lines_have_no_gaps_or_repeats_at_speed():
    client, _ = fake_app()
    start = client.get("/operation").json()["started_ms"]
    with client:
        client.post("/run/live?speed=4")
        with client.websocket_connect("/ws") as ws:
            lines = [x for _ in range(6) for x in ws.receive_json()["log"]]
    ts = [int(x[1:]) for x in lines]
    assert ts == list(range(start + 200, start + 200 * (len(ts) + 1), 200))


def test_decision_reaches_tick_inputs():
    client, eng = fake_app()
    acc = client.post("/decisions", json={"report_id": "rep-d1-1", "choice_id": "watch"}).json()
    assert acc["id"] == "dec-1"
    client.post("/run/jump?offset_ms=1000")
    assert [d.id for d in eng.seen[1].decisions] == ["dec-1"]


def test_switch_request_and_approve():
    client, _ = fake_app()
    inj = client.post("/injections", json={"play_by_vehicle": {"d2": "track_fast"}}).json()
    assert inj["status"] == "pending"
    assert client.post(f"/injections/{inj['id']}/approve").json()["status"] == "approved"


def test_plays_check_and_save():
    from modules.gateway.tests.test_live_plays import PATROL_A, no_report_play

    client, _ = fake_app()
    bad = no_report_play().model_dump(mode="json")
    assert client.post("/plays/check", json=bad).json()["ok"] is False
    assert client.post("/plays", json=bad).json()["ok"] is False
    renamed = PATROL_A.model_copy(update={"name": "해안 순찰 A2"}).model_dump(mode="json")
    names = lambda: [p["name"] for p in client.get("/plays").json()]  # noqa: E731
    assert client.post("/plays/check", json=renamed).json()["ok"] is True
    assert "해안 순찰 A2" not in names()  # check only, nothing saved
    body = client.post("/plays", json=renamed).json()
    assert (body["ok"], body["issues"]) == (True, [])
    assert set(body["est_return_battery"]) == {"d1", "d3"}  # values belong to the play module
    assert "해안 순찰 A2" in names()


def test_draft_returns_the_cached_ai_play_for_a_demo_sentence():
    import json

    sentences = {
        s["id"]: s["text"]
        for s in json.loads((ROOT / "demo/draft_sentences.json").read_text("utf-8"))
    }
    client, _ = fake_app()
    play = client.post("/plays/draft", json={"text": sentences["no_report"]}).json()
    assert (play["origin"], play["approved"]) == ("ai_draft", False)  # cache hit, no network
    assert "approach_target" in [s["do"]["kind"] for s in play["steps"]]


def test_draft_runs_off_the_event_loop(monkeypatch):
    # draft_play may call the LLM for minutes on a cache miss; the WS loop must keep streaming meanwhile.
    import asyncio

    import modules.gateway.app as app_module
    from modules.gateway.tests.test_live_plays import PATROL_A

    seen = {}

    def fake_draft(text, op):
        try:
            asyncio.get_running_loop()
            seen["in_loop"] = True
        except RuntimeError:
            seen["in_loop"] = False
        seen["args"] = (text, op.id)
        return PATROL_A

    monkeypatch.setattr(app_module, "draft_play", fake_draft)
    client, _ = fake_app()
    assert client.post("/plays/draft", json={"text": "순찰"}).json()["id"] == PATROL_A.id
    assert seen == {"in_loop": False, "args": ("순찰", "op1")}


def test_reset_pauses():
    client, _ = fake_app()
    client.post("/run/live?speed=5")
    assert client.post("/run/reset").json() == {"status": "paused", "speed": 1.0}
    assert client.post("/run/live?speed=0").json() == {"status": "paused", "speed": 1.0}


def test_tick_error_pauses_and_server_survives():
    client, eng = fake_app()

    def boom(state, inputs):
        raise RuntimeError("engine bug")

    with client:
        eng.tick = boom
        client.post("/run/live?speed=1")
        with client.websocket_connect("/ws") as ws:
            statuses = [ws.receive_json()["run"]["status"] for _ in range(20)]
        assert statuses[-1] == "paused"
        assert client.get("/health").json() == {"ok": True}


def test_default_engine_streams_contract_frames():
    with TestClient(create_app(SCENARIO, period_s=0.01)) as client:
        client.post("/run/live?speed=1")
        with client.websocket_connect("/ws") as ws:
            Frame.model_validate(ws.receive_json())


def test_default_engine_is_the_real_engine_and_no_stub_is_left():
    # 09 §4.5: stubs go before integration 2, so the example-frame fallback must not exist any more.
    import importlib.util

    from modules.gateway import engine
    from modules.gateway.app import default_engine

    assert default_engine().tick is engine.tick
    assert importlib.util.find_spec("modules.gateway.stub_engine") is None


def test_serves_ui_dist(tmp_path):
    (tmp_path / "index.html").write_text("<html>ui</html>")
    client, _ = fake_app(ui_dist=str(tmp_path))
    assert "ui" in client.get("/").text


def test_ontology_view_from_the_scenario():  # decision 0038
    client, _ = fake_app()
    view = client.get("/ontology").json()
    assert [v["vehicle_id"] for v in view["vehicles"]] == ["d1", "d2", "d3", "d4", "usv", "ugv"]
    d1 = {r["action"]: r for r in view["vehicles"][0]["reasons"]}
    assert d1["strike_target"]["allowed"] is False
    assert d1["strike_target"]["path"] == ["recon_drone", "air_vehicle", "vehicle"]


def test_check_shows_the_kind_path_when_d1_gets_a_strike_step():  # editor demo beat (0038)
    client, _ = fake_app()
    patrol = next(p for p in client.get("/plays").json() if p["id"] == "patrol_a")
    strike = {"kind": "strike_target", "params": {"target": "nearest"}}
    patrol["steps"].append({"id": "hit", "name": "타격", "do": strike})
    chk = client.post("/plays/check", json=patrol).json()
    msgs = [i["message"] for i in chk["issues"] if i["code"] == "missing_capability"]
    assert "d1는 strike_target를 못 함: 정찰 드론 → 공중 기체 → 기체 어디에도 이 능력 없음" in msgs


def test_graph_from_a_vehicle_on_the_real_engine():  # decision 0038
    client = TestClient(create_app(SCENARIO, period_s=0.01))
    g = client.get("/graph?focus=d1").json()
    assert g["focus"] == "d1" and {"vehicle", "command"} <= {n["type"] for n in g["nodes"]}


def test_graph_unknown_focus_is_404():
    client = TestClient(create_app(SCENARIO, period_s=0.01))
    assert client.get("/graph?focus=nope").status_code == 404


def test_delete_play_with_the_real_engine():  # decision 0050
    with TestClient(create_app(SCENARIO, period_s=0.01)) as client:
        pid = client.get("/operation").json()["assign"]["d1"]
        left = client.delete(f"/plays/{pid}")
        assert left.status_code == 200 and pid not in [p["id"] for p in left.json()]
        assert pid not in [p["id"] for p in client.get("/plays").json()]
        assert "d1" not in client.get("/operation").json()["assign"]
        assert client.post("/run/jump?offset_ms=60000").json()["status"] == "paused"
        assert client.delete("/plays/nope").status_code == 404
