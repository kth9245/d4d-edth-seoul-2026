export type RunStop = { offsetMs: number; label: string };

const MIN = 60_000;

// Where "다음 사건" pauses the run: a few seconds after each scene so its card is already up
// (Part1-13 decision: right after the event, paused). Offsets are ms after operation.started_ms.
// Times are the real engine's scenes (modules/gateway/tests/test_demo_timeline.py, scripts/qa/script.json):
// boat cards from the coast patrol s1 17:00, d1 goes home 19:00 (reserve d3 takes its job), d2 sent past the NLL
// s5 20:00 (the battery block at 20:30 was checked at that battery), fast1 appears 23:00 and d3, still watching
// boat1, raises its card at 23:04 (decision 0056). No stop in the strike (s4 fast1 card answered, s7 approval
// cards, s8 neutralized): they follow the operator's clicks, and a jump runs with no operator input (Part1-13.1).
export const RUN_STOPS: RunStop[] = [
  { offsetMs: 17 * MIN + 5_000, label: "보고 카드" },
  { offsetMs: 19 * MIN + 5_000, label: "드론1 귀환" },
  { offsetMs: 20 * MIN, label: "드론2 직접 조종" },
  { offsetMs: 23 * MIN + 5_000, label: "고속정 등장" },
];

// The first stop strictly after the current offset, so sitting on a stop (just jumped) moves on.
export function nextStop(offsetMs: number, stops: RunStop[] = RUN_STOPS): RunStop | null {
  return stops.find((s) => s.offsetMs > offsetMs) ?? null;
}
