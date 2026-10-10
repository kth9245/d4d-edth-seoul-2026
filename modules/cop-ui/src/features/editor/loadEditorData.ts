import type { EnemySpec, Operation, Play, VehicleSpec } from "../../contracts.gen";

export type EditorData = { operation: Operation; plays: Play[]; vehicles: VehicleSpec[]; enemies: EnemySpec[] };
type Fetch = (url: string) => Promise<Response>;

async function getJson<T>(f: Fetch, url: string): Promise<T> {
  const r = await f(url);
  if (!r.ok) throw new Error(`${url} answered ${r.status}`);
  return (await r.json()) as T;
}

// GET /operation, /plays, /vehicles and /enemies. Without the gateway this fails and the editor says so (no example data).
export async function loadEditorData(f: Fetch = (url) => fetch(url)): Promise<EditorData> {
  const [operation, plays, vehicles, enemies] = await Promise.all([
    getJson<Operation>(f, "/operation"), getJson<Play[]>(f, "/plays"), getJson<VehicleSpec[]>(f, "/vehicles"),
    getJson<EnemySpec[]>(f, "/enemies"),
  ]);
  // A wrong shape would throw later inside groupPlays/vehicleColumns and blank the whole page.
  if (!Array.isArray(plays) || !Array.isArray(vehicles) || !Array.isArray(enemies) || !Array.isArray(operation?.vehicle_ids)) {
    throw new Error("unexpected /operation, /plays, /vehicles or /enemies shape");
  }
  return { operation, plays, vehicles, enemies };
}
