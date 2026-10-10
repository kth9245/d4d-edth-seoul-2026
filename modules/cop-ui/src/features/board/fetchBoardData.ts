import type { EnemySpec, Role, Switch, VehicleSpec, WatchPoint } from "../../contracts.gen";
import { fetchOperation } from "../live/fetchOperation";

export interface BoardData { roles: Role[]; vehicles: VehicleSpec[]; watch: WatchPoint[]; enemyRoles: string[]; switches: Switch[] }
export const NO_BOARD_DATA: BoardData = { roles: [], vehicles: [], watch: [], enemyRoles: [], switches: [] };

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

// What the live board needs besides the Frame (Part1-32): role names and first steps, vehicle specs, watch points
// (decision 0047), the roles enemies follow (left out of the vehicle menu) and the operation's switch buttons
// (the roster head, decision 0060). A failed read is an empty list, never a broken screen.
export async function fetchBoardData(): Promise<BoardData> {
  const [roles, vehicles, watch, enemies, op] = await Promise.all([
    list<Role>("/roles"), list<VehicleSpec>("/vehicles"), list<WatchPoint>("/watch_points"), list<EnemySpec>("/enemies"),
    fetchOperation(),
  ]);
  const switches = Array.isArray(op?.switches) ? op.switches : [];
  return { roles, vehicles, watch, enemyRoles: enemies.map((e) => e.role_id), switches };
}
