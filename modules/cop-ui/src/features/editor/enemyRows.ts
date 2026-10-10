import type { EnemySpec, Role } from "../../contracts.gen";
import { kstTime } from "../cards/kstTime";
import { TARGET_KIND_LABEL } from "./describe";

// The enemy section under the vehicle columns (Part1-21, decision 0032): one column per enemy, read only.

export type EnemyRow = { id: string; kind: string; appear: string; place: string; speed: string; roleId: string; role: Role | null };

// When the enemy appears: KST clock time and minutes after the operation start.
export function appearText(e: EnemySpec, started: number | null | undefined): string {
  const after = `+${Math.round(e.appear_offset_ms / 60000)}분`;
  return started == null ? `${after} 등장` : `${kstTime(started + e.appear_offset_ms).slice(0, 5)} KST 등장 (${after})`;
}

export function enemyRows(enemies: EnemySpec[], started: number | null | undefined, roles: Role[]): EnemyRow[] {
  return enemies.map((e) => ({
    id: e.id,
    kind: TARGET_KIND_LABEL[e.kind],
    appear: appearText(e, started),
    place: e.pos ? `${e.pos.lat.toFixed(3)}, ${e.pos.lon.toFixed(3)}` : `${e.from_enemy} 위치에서`,
    speed: `${e.speed_mps.toFixed(1)} m/s`,
    roleId: e.role_id,
    role: roles.find((p) => p.id === e.role_id) ?? null,
  }));
}
