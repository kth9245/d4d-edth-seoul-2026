from pathlib import Path

from fastapi.testclient import TestClient

from contracts.models import LegacyFrame
from modules.gateway import Engine, create_app
from modules.sim import load_scenario

ROOT = Path(__file__).resolve().parents[3]
SCENARIO = str(ROOT / "demo/scenarios/seoul_mixed.yaml")


def test_engine_produces_tracks_and_assessments():
    eng = Engine(load_scenario(SCENARIO), seed=1)
    frames = [eng.step() for _ in range(40)]
    last = frames[-1]
    assert len(last.tracks) >= 3
    assert {a.track_id for a in last.assessments} == {t.id for t in last.tracks}
    assert frames[1].t_ms - frames[0].t_ms == 500


def test_engine_done_at_end():
    eng = Engine(load_scenario(SCENARIO))
    for _ in range(240):
        eng.step()
    assert eng.done


def test_health_and_websocket_frames():
    client = TestClient(create_app(SCENARIO, realtime=False))
    assert client.get("/health").json() == {"ok": True}
    with client.websocket_connect("/ws") as ws:
        LegacyFrame.model_validate(ws.receive_json())
        LegacyFrame.model_validate(ws.receive_json())


def test_websocket_reconnect():
    client = TestClient(create_app(SCENARIO, realtime=False))
    with client.websocket_connect("/ws") as ws:
        first = LegacyFrame.model_validate(ws.receive_json())
    with client.websocket_connect("/ws") as ws2:
        again = LegacyFrame.model_validate(ws2.receive_json())
    assert again.t_ms == first.t_ms
    assert client.get("/health").status_code == 200


def test_serves_ui_dist(tmp_path):
    (tmp_path / "index.html").write_text("<html>ui</html>")
    client = TestClient(create_app(SCENARIO, realtime=False, ui_dist=str(tmp_path)))
    assert "ui" in client.get("/").text


def test_pipeline_error_closes_socket_with_1011_and_server_survives(monkeypatch):
    import pytest
    from starlette.websockets import WebSocketDisconnect

    def boom(self):
        raise NotImplementedError("skeleton action")

    monkeypatch.setattr(Engine, "step", boom)
    client = TestClient(create_app(SCENARIO, realtime=False))
    with client.websocket_connect("/ws") as ws:
        with pytest.raises(WebSocketDisconnect) as exc:
            ws.receive_text()
    assert exc.value.code == 1011
    assert client.get("/health").json() == {"ok": True}
