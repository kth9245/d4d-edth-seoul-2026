import type { EnemySpec, Operation, Role } from "../../contracts.gen";
import { appearText } from "./enemyRows";
import { choicesOf } from "./vehicleColumns";

export type Usage = { vehicle_id: string; how: string };

// Which vehicles run each role and how they get there: operation start, a report choice, or a switch.
// An enemy's role names the enemy and when it appears (Part1-21).
export function roleUsage(op: Operation, roles: Role[], enemies: EnemySpec[] = []): Record<string, Usage[]> {
  const out: Record<string, Usage[]> = {};
  const push = (roleId: string, u: Usage) => (out[roleId] ??= []).push(u);
  for (const [v, pid] of Object.entries(op.assign ?? {})) push(pid, { vehicle_id: v, how: "작전 시작" });
  for (const p of roles) {
    for (const c of choicesOf(p)) {
      for (const [v, pid] of Object.entries(c.role_by_vehicle ?? {})) {
        push(pid, { vehicle_id: v, how: `${p.name}의 '${c.label}' 뒤` });
      }
    }
  }
  for (const sw of op.switches ?? []) {
    for (const [v, pid] of Object.entries(sw.role_by_vehicle)) push(pid, { vehicle_id: v, how: `전체 전환 '${sw.label}'` });
  }
  for (const e of enemies) push(e.role_id, { vehicle_id: e.id, how: `적 · ${appearText(e, op.started_ms)}` });
  return out;
}
