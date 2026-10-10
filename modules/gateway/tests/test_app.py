from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from contracts.models import Frame, Scenario
from modules.gateway import create_app
from modules.gateway.tests.test_live import FakeEngine

ROOT = Path(__file__).resolve().parents[3]
SCENARIO = str(ROOT / "demo/scenarios/baengnyeong_night.json")


def fake_app(**kw) -> tuple[TestClient, FakeEngine]:
    eng = FakeEngine()
    ns = SimpleNamespace(
        load_scenario_json=lambda p: Scenario.model_validate_json(Path(p).read_text("utf-8")),
        init_engine=eng.init,
        tick=lambda state, inputs: eng.tick(state, inputs),  # tests may swap eng.tick
    )
    return TestClient(create_app(SCENARIO, engine=ns, period_s=0.01, **kw)), eng


def test_plays_and_operation_come_from_the_scenario():
    client, _ = fake_app()
    assert "track_fast" in [p["id"] for p in client.get("/plays").json()]
    assert client.get("/operation").json()["id"] == "op1"
    assert client.get("/health").json() == {"ok": True}


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
    assert client.post("/plays", json=renamed).json() == {
        "ok": True,
        "issues": [],
        "est_return_battery": {"d1": 53.6, "d3": 51.4},
    }
    assert "해안 순찰 A2" in [p["name"] for p in client.get("/plays").json()]


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


def test_serves_ui_dist(tmp_path):
    (tmp_path / "index.html").write_text("<html>ui</html>")
    client, _ = fake_app(ui_dist=str(tmp_path))
    assert "ui" in client.get("/").text
