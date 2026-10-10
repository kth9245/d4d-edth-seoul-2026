import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { Operation, Play } from "../../contracts.gen";

export type EditorData = { operation: Operation; plays: Play[]; source: "gateway" | "example" };
type Fetch = (url: string) => Promise<Response>;

// Dev stub until Part1-7 serves GET /operation and GET /plays. Remove before integration 2 (09 §4.5).
const EXAMPLE = scenario as unknown as { operation: Operation; plays: Play[] };

async function getJson<T>(f: Fetch, url: string): Promise<T> {
  const r = await f(url);
  if (!r.ok) throw new Error(`${url} answered ${r.status}`);
  return (await r.json()) as T;
}

export async function loadEditorData(f: Fetch = (url) => fetch(url)): Promise<EditorData> {
  try {
    const [operation, plays] = await Promise.all([getJson<Operation>(f, "/operation"), getJson<Play[]>(f, "/plays")]);
    // A wrong shape would throw later inside groupPlays/vehicleColumns and blank the whole page.
    if (!Array.isArray(plays) || !Array.isArray(operation?.vehicle_ids)) throw new Error("unexpected /operation or /plays shape");
    return { operation, plays, source: "gateway" };
  } catch (e) {
    console.warn("editor: gateway unavailable, showing example data", e);
    return { operation: EXAMPLE.operation, plays: EXAMPLE.plays, source: "example" };
  }
}
