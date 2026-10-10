import type { RunState } from "../../contracts.gen";

export type RunResult = { ok: true; run: RunState } | { ok: false; error: string };

// POST /run/live?speed= · /run/reset · /run/jump?offset_ms= (contracts/API.md §5). Never throws: the bar shows the error.
export async function postRun(path: string): Promise<RunResult> {
  let r: Response;
  try {
    r = await fetch(path, { method: "POST" });
  } catch {
    return { ok: false, error: "서버 연결 실패" };
  }
  const data = await r.json().catch(() => null);
  if (r.ok && data) return { ok: true, run: data as RunState };
  const detail = typeof data?.detail === "string" ? ` ${data.detail}` : "";
  return { ok: false, error: `${r.status}${detail}` };
}
