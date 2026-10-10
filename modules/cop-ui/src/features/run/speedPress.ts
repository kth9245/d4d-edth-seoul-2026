// The run bar's speed buttons (QA finding 3, lead: "멈춤 유지, 속도만 기억"): while running a speed button
// changes the speed at once; while paused it only remembers the speed and ▶ starts at it.
export function speedPress(running: boolean, pressed: number): { request: string } | { remember: number } {
  return running ? { request: `/run/live?speed=${pressed}` } : { remember: pressed };
}

// ▶ / ⏸: pause sends 0; play sends the speed remembered while paused, else the run's own (decision 0026).
export function playRequest(running: boolean, runSpeed: number, remembered: number | null): string {
  return `/run/live?speed=${running ? 0 : (remembered ?? runSpeed)}`;
}
