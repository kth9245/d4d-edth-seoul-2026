import type { ScenarioInfo } from "../../contracts.gen";

type Fetch = (url: string) => Promise<Response>;

// GET /scenarios (decision 0041): the operations the gateway can run, the running one active.
// Any failure (old gateway, network, not a list) is [], so the list just does not show.
export async function fetchScenarios(f: Fetch = (url) => fetch(url)): Promise<ScenarioInfo[]> {
  try {
    const r = await f("/scenarios");
    if (!r.ok) return [];
    const list: unknown = await r.json();
    return Array.isArray(list) ? (list as ScenarioInfo[]) : [];
  } catch {
    return [];
  }
}
