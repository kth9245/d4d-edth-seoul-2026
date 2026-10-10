"""FastAPI app: REST inputs, WS Frame stream and the static UI (contracts/API.md §5).

Run: uvicorn modules.gateway.app:create_app --factory (env KDTH_SCENARIO, KDTH_UI_DIST).
The demo operations live in process memory (`Live`, one of them running, decision 0042);
a background task calls `Live.period()` every `period_s`. Handlers are async so all state
changes happen on the event loop thread.
"""

import asyncio
import contextlib
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from contracts.models import DecisionIn, DirectIn, DraftIn, Operation, Play, SwitchIn
from modules import sim
from modules.gateway.actions.build_object_graph import build_object_graph
from modules.gateway.live import Live
from modules.ontology import ontology_view
from modules.play import draft_play
from shared.log import get_logger, setup_logging

log = get_logger("gateway")
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENARIO = str(ROOT / "demo/scenarios/baengnyeong_night.json")
# Operations the editor can pick (decision 0042). The backup baengnyeong_night_before_0036.json
# shares the night scenario id, so it is left out.
DEMO_SCENARIOS = [
    DEFAULT_SCENARIO,
    str(ROOT / "demo/scenarios/baengnyeong_24h.json"),
]


def default_engine():
    """The real tick loop (engine.py, Part2-17) on the sim scenario loader."""
    from modules.gateway.engine import init_engine, tick

    return SimpleNamespace(
        load_scenario_json=sim.load_scenario_json, init_engine=init_engine, tick=tick
    )


def create_app(
    scenario_path: str | None = None,
    ui_dist: str | None = None,
    engine=None,
    period_s: float = 0.2,
    scenario_paths: list[str] | None = None,
) -> FastAPI:
    setup_logging("gateway")  # decision 0010: always log (stderr + logs/gateway.log)
    eng = engine or default_engine()
    path = scenario_path or os.environ.get("KDTH_SCENARIO", DEFAULT_SCENARIO)
    catalog = []
    for p in DEMO_SCENARIOS if scenario_paths is None else scenario_paths:
        try:
            catalog.append(eng.load_scenario_json(p))
        except Exception:  # another operation's broken file must not stop this one (decision 0042)
            log.exception("scenario %s skipped from the operation list: it does not load", p)
    live = Live(eng.load_scenario_json(path), eng.init_engine, eng.tick, catalog)
    log.info("scenario %s loaded; %d operations to pick", path, len(live.scenarios))

    async def run_loop() -> None:
        while True:
            try:
                live.period()
            except Exception:
                log.exception("tick failed at t=%d; run paused", live.frame.t_ms)
                live.set_speed(0)
            await asyncio.sleep(period_s)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        task = asyncio.create_task(run_loop())
        yield
        task.cancel()

    app = FastAPI(title="kdth gateway", lifespan=lifespan)

    @app.middleware("http")
    async def log_errors(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception:
            log.exception("%s %s failed", request.method, request.url.path)
            raise

    @app.get("/health")
    async def health() -> dict:
        return {"ok": True}

    @app.get("/plays")
    async def plays():
        return live.scenario.plays

    @app.post("/plays")
    async def save_play(play: Play):
        chk = live.save_play(play)  # saved and reset only when the check passes
        log.info("POST /plays %s ok=%s issues=%d", play.id, chk.ok, len(chk.issues))
        return chk

    @app.post("/plays/draft")
    async def draft(body: DraftIn):
        # Cache first; a miss may call the LLM for minutes, so run it off the loop that streams /ws.
        t0 = time.monotonic()
        play = await asyncio.to_thread(draft_play, body.text, live.scenario.operation)
        log.info(
            "POST /plays/draft %r -> %s origin=%s %.1fs",
            body.text[:40],
            play.id,
            play.origin,
            time.monotonic() - t0,
        )
        return play

    @app.post("/plays/check")
    async def check_play(play: Play):
        chk = live.check_play(play)
        log.info("POST /plays/check %s ok=%s issues=%d", play.id, chk.ok, len(chk.issues))
        return chk

    @app.get("/operation")
    async def get_operation():
        return live.scenario.operation

    @app.get("/vehicles")
    async def vehicles():
        return live.scenario.vehicles

    @app.get("/enemies")
    async def enemies():
        return live.scenario.enemies

    @app.get("/ontology")
    async def ontology():  # decision 0038: the same inference the play check uses
        if live.scenario.ontology is None:
            raise HTTPException(404, "이 시나리오에는 온톨로지가 없습니다")
        return ontology_view(live.scenario)

    @app.get("/graph")
    async def graph(focus: str):  # decision 0038: objects linked to one object in this run
        try:
            return build_object_graph(live.state, focus)
        except ValueError as e:
            raise HTTPException(404, str(e)) from e

    @app.get("/scenarios")
    async def scenarios():
        return live.scenario_infos()

    @app.post("/scenarios/{scenario_id}/activate")
    async def activate(scenario_id: str):
        if scenario_id not in live.scenarios:
            raise HTTPException(404, f"no scenario {scenario_id}")
        log.info("POST /scenarios/%s/activate", scenario_id)
        return live.activate(scenario_id)

    @app.post("/operation")
    async def post_operation(op: Operation):
        log.info("POST /operation %s", op.id)
        return live.set_operation(op)

    @app.post("/run/live")
    async def run_live(speed: float):
        log.info("POST /run/live speed=%s", speed)
        return live.set_speed(speed)

    @app.post("/run/reset")
    async def run_reset():
        log.info("POST /run/reset")
        return live.reset()

    @app.post("/run/jump")
    async def run_jump(offset_ms: int):
        log.info("POST /run/jump offset_ms=%d", offset_ms)
        return live.jump(offset_ms)

    @app.post("/decisions")
    async def decisions(body: DecisionIn):
        acc = live.decide(body)
        log.info("POST /decisions %s/%s -> %s", body.report_id, body.choice_id, acc.id)
        return acc

    @app.post("/direct")
    async def direct(body: DirectIn):
        acc = live.direct(body)
        log.info("POST /direct %s -> %s %s", body.vehicle_id, body.target, acc.id)
        return acc

    @app.post("/injections")
    async def injections(body: SwitchIn):
        inj = live.request_switch(body)
        log.info("POST /injections %s -> %s %s", body.model_dump(), inj.id, inj.label)
        return inj

    @app.post("/injections/{inj_id}/{verdict}")
    async def settle(inj_id: str, verdict: str):
        log.info("POST /injections/%s/%s", inj_id, verdict)
        return live.settle_injection(inj_id, approve=verdict == "approve")

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
        cursor = None  # log lines already sent on this connection (Live.frame_for)
        try:
            while not closed.is_set():
                frame, cursor = live.frame_for(cursor)
                with contextlib.suppress(WebSocketDisconnect, RuntimeError):
                    await websocket.send_text(frame.model_dump_json())
                await asyncio.sleep(period_s)
        finally:
            watcher.cancel()

    if ui_dist := ui_dist or os.environ.get("KDTH_UI_DIST"):
        if Path(ui_dist, "index.html").exists():
            app.mount("/", StaticFiles(directory=ui_dist, html=True), name="ui")
    return app
