// A span of ms as "m:ss" (run clock T+16:15, stop labels, vehicle gap). Minutes do not wrap at an hour.
export function mmss(ms: number): string {
  const s = Math.max(0, Math.floor(ms / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}
