import { useEffect, useState } from "react";
import type { Frame } from "../../contracts.gen";
import { fetchOperation } from "../live/fetchOperation";
import { mmss } from "./mmss";
import { jumpPaused, postRun, type RunResult } from "./runApi";
import { nextStop } from "./runStops";
import "./run.css";

const SPEEDS = [1, 5, 10, 30];

// Under the map: run clock, play/pause, speed, "다음 사건" (pause, then jump) and reset (contracts/API.md §5).
// Buttons only send requests; what the bar shows comes from the next WS Frame (Frame.run).
export function RunBar({ frame }: { frame: Frame | null }) {
  const [startedMs, setStartedMs] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const hasFrame = frame !== null;
  useEffect(() => {
    // offset_ms counts from operation.started_ms. If the gateway was down when the screen opened,
    // try again once the first Frame arrives.
    if (startedMs !== null) return;
    fetchOperation().then((op) => {
      if (typeof op?.started_ms === "number") setStartedMs(op.started_ms);
    });
  }, [hasFrame, startedMs]);

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
  const offset = frame && startedMs !== null ? frame.t_ms - startedMs : null;
  const next = offset === null ? null : nextStop(offset);
  const off = !frame || busy;
  const reset = () => {
    if (confirm("작전을 처음부터 다시 시작할까요?")) act(() => postRun("/run/reset"));
  };

  return (
    <div className="runbar">
      <span className="clock">T+{offset === null ? "--:--" : mmss(offset)}</span>
      <button className="play" disabled={off} onClick={() => act(() => postRun(`/run/live?speed=${running ? 0 : speed}`))}>
        {running ? "⏸ 일시정지" : "▶ 재생"}
      </button>
      <span className="speeds">
        {SPEEDS.map((s) => (
          <button key={s} disabled={off} className={s === speed ? (running ? "on" : "on dim") : ""}
            onClick={() => act(() => postRun(`/run/live?speed=${s}`))}>
            ×{s}
          </button>
        ))}
      </span>
      <button className="next" disabled={off || !next} onClick={() => next && act(() => jumpPaused(next.offsetMs))}>
        {next ? `다음 사건 ▸ ${mmss(next.offsetMs)} ${next.label}` : "다음 사건 없음"}
      </button>
      <button className="reset" disabled={off} title="처음으로" onClick={reset}>↺ 처음으로</button>
      {error && <span className="error">요청 실패: {error}</span>}
    </div>
  );
}
