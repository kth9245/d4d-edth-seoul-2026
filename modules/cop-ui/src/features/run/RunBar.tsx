import { useEffect, useState } from "react";
import type { Frame } from "../../contracts.gen";
import { fetchOperation } from "../live/fetchOperation";
import { fetchScenarios } from "../live/fetchScenarios";
import { mmss } from "./mmss";
import { RESET_WINDOW_MS, resetPress } from "./resetPress";
import { jumpPaused, postRun, type RunResult } from "./runApi";
import { nextStop, type RunStop } from "./runStops";
import { playRequest, speedPress } from "./speedPress";
import { stopsFor } from "./stopsFor";
import "./run.css";

const SPEEDS = [1, 5, 10, 30];

// Under the map: run clock, start/pause, speed, "다음 사건" (pause, then jump) and reset (contracts/API.md §5).
// Buttons only send requests; what the bar shows comes from the next WS Frame (Frame.run).
export function RunBar({ frame }: { frame: Frame | null }) {
  const [startedMs, setStartedMs] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [armedAt, setArmedAt] = useState<number | null>(null); // "처음으로" pressed once
  const [remembered, setRemembered] = useState<number | null>(null); // a speed picked while paused (QA finding 3)
  const hasFrame = frame !== null;
  useEffect(() => {
    // offset_ms counts from operation.started_ms. If the gateway was down when the screen opened,
    // try again once the first Frame arrives.
    if (startedMs !== null) return;
    fetchOperation().then((op) => {
      if (typeof op?.started_ms === "number") setStartedMs(op.started_ms);
    });
  }, [hasFrame, startedMs]);
  // "다음 사건" stops of the running operation (decision 0042). Like startedMs, read again once a Frame
  // arrives if the gateway was down when the screen opened.
  const [stops, setStops] = useState<RunStop[] | null>(null);
  useEffect(() => {
    if (stops !== null) return;
    fetchScenarios().then((list) => {
      if (list.length) setStops(stopsFor(list.find((s) => s.active)?.id ?? null));
    });
  }, [hasFrame, stops]);

  const act = async (send: () => Promise<RunResult>) => {
    if (busy) return;
    setBusy(true);
    setError(null);
    const r = await send();
    setBusy(false);
    if (!r.ok) setError(r.error);
  };

  const running = frame?.run.status === "running";
  const speed = frame?.run.speed ?? 1; // kept while paused (decision 0026), so ▶ resumes at it
  const shown = running ? speed : (remembered ?? speed);
  useEffect(() => {
    if (running) setRemembered(null); // the picked speed is now the run's own
  }, [running]);
  const offset = frame && startedMs !== null ? frame.t_ms - startedMs : null;
  const next = offset === null ? null : nextStop(offset, stops ?? []);
  const off = !frame || busy;
  useEffect(() => {
    if (armedAt === null) return;
    const t = setTimeout(() => setArmedAt(null), RESET_WINDOW_MS);
    return () => clearTimeout(t);
  }, [armedAt]);
  const reset = () => {
    const now = Date.now();
    if (resetPress(armedAt, now) === "arm") return setArmedAt(now);
    setArmedAt(null);
    act(() => postRun("/run/reset"));
  };

  return (
    <div className="runbar">
      <span className="clock">T+{offset === null ? "--:--" : mmss(offset)}</span>
      <button className="run-toggle" disabled={off} onClick={() => act(() => postRun(playRequest(running, speed, remembered)))}>
        {running ? "⏸ 일시정지" : "▶ 재생"}
      </button>
      <span className="speeds">
        {SPEEDS.map((s) => (
          <button key={s} disabled={off} className={s === shown ? (running ? "on" : "on dim") : ""}
            onClick={() => {
              const press = speedPress(running, s);
              if ("request" in press) act(() => postRun(press.request));
              else setRemembered(press.remember);
            }}>
            ×{s}
          </button>
        ))}
      </span>
      <button className="next" disabled={off || !next} onClick={() => next && act(() => jumpPaused(next.offsetMs))}>
        {next ? `다음 사건 ▸ ${mmss(next.offsetMs)} ${next.label}` : "다음 사건 없음"}
      </button>
      <button className={armedAt === null ? "reset" : "reset armed"} disabled={off} title="처음으로" onClick={reset}>
        {armedAt === null ? "↺ 처음으로" : "↺ 한 번 더 누르면 처음으로"}
      </button>
      {error && <span className="error">요청 실패: {error}</span>}
    </div>
  );
}
