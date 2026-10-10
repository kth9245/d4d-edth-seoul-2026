import type { EnemySpec, Operation, Play } from "../../contracts.gen";
import { appearText } from "./enemyRows";
import { choicesOf } from "./vehicleColumns";

export type Usage = { vehicle_id: string; how: string };

// Which vehicles run each play and how they get there: operation start, a report choice, or a switch.
// An enemy's play names the enemy and when it appears (Part1-21).
export function playUsage(op: Operation, plays: Play[], enemies: EnemySpec[] = []): Record<string, Usage[]> {
  const out: Record<string, Usage[]> = {};
  const push = (playId: string, u: Usage) => (out[playId] ??= []).push(u);
  for (const [v, pid] of Object.entries(op.assign ?? {})) push(pid, { vehicle_id: v, how: "작전 시작" });
  for (const p of plays) {
    for (const c of choicesOf(p)) {
      for (const [v, pid] of Object.entries(c.play_by_vehicle ?? {})) {
        push(pid, { vehicle_id: v, how: `${p.name}의 '${c.label}' 뒤` });
      }
    }
  }
  for (const sw of op.switches ?? []) {
    for (const [v, pid] of Object.entries(sw.play_by_vehicle)) push(pid, { vehicle_id: v, how: `전체 전환 '${sw.label}'` });
  }
  for (const e of enemies) push(e.play_id, { vehicle_id: e.id, how: `적 · ${appearText(e, op.started_ms)}` });
  return out;
}
