import { opsRun } from "../live/opsRun";
import { runPath } from "../live/runPath";

export type Sent = { ok: true; id: string } | { ok: false; error: string };

// POST to the gateway (contracts/API.md §5) and keep the returned id (Accepted.id or Injection.id).
// Never throws: the card shows the error. On 실작전 it goes to that run (decision 0068).
export async function postJson(url: string, body?: unknown): Promise<Sent> {
  let r: Response;
  try {
    r = await fetch(runPath(url, opsRun.get()), body === undefined ? { method: "POST" }
      : { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  } catch {
    return { ok: false, error: "서버 연결 실패" };
  }
  const data = await r.json().catch(() => null);
  if (r.ok && typeof data?.id === "string") return { ok: true, id: data.id };
  const detail = typeof data?.detail === "string" ? ` ${data.detail}` : "";
  return { ok: false, error: `${r.status}${detail}` };
}
