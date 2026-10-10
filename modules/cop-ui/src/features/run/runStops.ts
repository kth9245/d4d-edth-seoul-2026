export type RunStop = { offsetMs: number; label: string };

const MIN = 60_000;

// Where "다음 사건" pauses the run: a few seconds after each scene so its card is already up
// (Part1-13 decision: right after the event, paused). Offsets are ms after operation.started_ms.
// Times come from the spike engine on demo/scenarios/baengnyeong_night.json
// (knowledge/spikes/rolecall_engine_proto/run_script.py): boat seen → report card at 16:13,
// drone 1 battery 19:00, boat split 23:00, direct-control scene 31:00.
// Checked on the real engine.py 10/10 (Part1-14, scripts/qa/live.json): card at 16:13, gap card 19:00,
// split 23:05, 31:00. Check again after scenario tuning (Part2-19).
export const RUN_STOPS: RunStop[] = [
  { offsetMs: 16 * MIN + 20_000, label: "보고 카드" },
  { offsetMs: 19 * MIN + 5_000, label: "드론1 배터리" },
  { offsetMs: 23 * MIN + 5_000, label: "보트 분리" },
  { offsetMs: 31 * MIN, label: "직접 조종" },
];

// The first stop strictly after the current offset, so sitting on a stop (just jumped) moves on.
export function nextStop(offsetMs: number, stops: RunStop[] = RUN_STOPS): RunStop | null {
  return stops.find((s) => s.offsetMs > offsetMs) ?? null;
}
