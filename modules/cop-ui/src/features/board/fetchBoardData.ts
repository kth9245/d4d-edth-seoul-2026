import type { Play, VehicleSpec, WatchPoint } from "../../contracts.gen";

export interface BoardData { plays: Play[]; vehicles: VehicleSpec[]; watch: WatchPoint[] }
export const NO_BOARD_DATA: BoardData = { plays: [], vehicles: [], watch: [] };

async function list<T>(url: string): Promise<T[]> {
  try {
    const r = await fetch(url);
    if (!r.ok) return [];
    const d = await r.json();
    return Array.isArray(d) ? (d as T[]) : [];
  } catch {
    return [];
  }
}

// What the live board needs besides the Frame (Part1-32): play names and first steps, vehicle specs, watch points
// (decision 0047). A failed read is an empty list, never a broken screen.
export async function fetchBoardData(): Promise<BoardData> {
  const [plays, vehicles, watch] = await Promise.all([
    list<Play>("/plays"), list<VehicleSpec>("/vehicles"), list<WatchPoint>("/watch_points"),
  ]);
  return { plays, vehicles, watch };
}
