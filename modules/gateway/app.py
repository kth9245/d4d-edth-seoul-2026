"""FastAPI app: WebSocket frame stream + static UI for the demo."""

import asyncio
import contextlib
import os
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from modules.gateway.pipeline import Engine
from modules.sim import load_scenario
from shared.log import get_logger, setup_logging

log = get_logger("gateway")
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENARIO = str(ROOT / "demo/scenarios/seoul_mixed.yaml")


def create_app(scenario_path: str, realtime: bool = True, ui_dist: str | None = None) -> FastAPI:
    setup_logging("gateway")  # decision 0010: always log (stderr + logs/gateway.log)
    scenario = load_scenario(scenario_path)
    log.info("scenario %s loaded", scenario_path)
    app = FastAPI(title="kdth gateway")

    @app.get("/health")
    def health() -> dict:
        return {"ok": True}

    @app.websocket("/ws")
    async def ws(websocket: WebSocket) -> None:
        await websocket.accept()
        closed = asyncio.Event()

        async def watch() -> None:
            try:
                while True:
                    await websocket.receive_text()
            except (WebSocketDisconnect, RuntimeError):
                closed.set()

        watcher = asyncio.create_task(watch())
        engine = Engine(scenario)
        try:
            while not closed.is_set():
                if engine.done:
                    engine = Engine(scenario)
                try:
                    payload = engine.step().model_dump_json()
                except Exception:
                    log.exception("pipeline error in engine.step(); closing /ws")
                    with contextlib.suppress(RuntimeError):
                        await websocket.close(code=1011, reason="pipeline error: see server log")
                    return
                try:
                    await websocket.send_text(payload)
                except (WebSocketDisconnect, RuntimeError):
                    break  # client went away
                await asyncio.sleep(scenario.step_ms / 1000 if realtime else 0)
        finally:
            watcher.cancel()

    if ui_dist and Path(ui_dist, "index.html").exists():
        app.mount("/", StaticFiles(directory=ui_dist, html=True), name="ui")
    return app


app = create_app(
    os.environ.get("KDTH_SCENARIO", DEFAULT_SCENARIO), ui_dist=os.environ.get("KDTH_UI_DIST")
)
