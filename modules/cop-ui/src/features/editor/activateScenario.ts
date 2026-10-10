import type { RunState } from "../../contracts.gen";

type Fetch = (url: string, init?: RequestInit) => Promise<Response>;

// POST /scenarios/{id}/activate (decision 0041): the gateway runs that operation from its start, paused.
export async function activateScenario(id: string, f: Fetch = (url, init) => fetch(url, init)): Promise<RunState> {
  const url = `/scenarios/${encodeURIComponent(id)}/activate`;
  const r = await f(url, { method: "POST" });
  if (!r.ok) throw new Error(`${url} answered ${r.status}`);
  return (await r.json()) as RunState;
}
