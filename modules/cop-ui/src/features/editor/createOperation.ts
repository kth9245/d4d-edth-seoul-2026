import type { ScenarioInfo } from "../../contracts.gen";

type Fetch = (url: string, init?: RequestInit) => Promise<Response>;

// POST /scenarios (decision 0053): an empty operation on the running one's map becomes the running one, paused.
// Returns the operation list with the new one active.
export async function createOperation(name: string, purpose: string, f: Fetch = (url, init) => fetch(url, init)): Promise<ScenarioInfo[]> {
  const r = await f("/scenarios", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, purpose }) });
  if (!r.ok) throw new Error(`/scenarios answered ${r.status}`);
  return (await r.json()) as ScenarioInfo[];
}
