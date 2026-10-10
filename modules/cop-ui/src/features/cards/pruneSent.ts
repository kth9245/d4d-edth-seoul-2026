// What the screen remembers having sent per report id. After /run/reset the same seed brings back the same report
// ids, and the server has forgotten the old decisions, so a kept entry would lock the replayed card for good.
// Returns the same object when nothing is dropped, so React skips the re-render.
export function pruneSent<T>(sent: Record<string, T>, reportIds: string[], timeWentBack: boolean): Record<string, T> {
  if (timeWentBack) return Object.keys(sent).length ? {} : sent;
  const ids = new Set(reportIds);
  const keep = Object.entries(sent).filter(([id]) => ids.has(id));
  return keep.length === Object.keys(sent).length ? sent : Object.fromEntries(keep);
}
