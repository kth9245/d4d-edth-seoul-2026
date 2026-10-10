import type { Choice, Operation, Play } from "../../contracts.gen";

export type ColumnPlay = { play_id: string; play: Play | null; via: string | null };
export type Column = { vehicle_id: string; reserve_for: string[]; plays: ColumnPlay[] };

export function choicesOf(play: Play): Choice[] {
  return play.steps.flatMap((s) => s.report?.choices ?? []);
}

// Plays the operation can reach: assigned plays, then every play a report choice points to (BFS, each once).
export function reachablePlays(op: Operation, plays: Play[]): Play[] {
  const byId = new Map(plays.map((p) => [p.id, p]));
  const queue = Object.values(op.assign ?? {});
  const seen = new Set<string>();
  const out: Play[] = [];
  while (queue.length > 0) {
    const id = queue.shift()!;
    if (seen.has(id)) continue;
    seen.add(id);
    const play = byId.get(id);
    if (!play) continue;
    out.push(play);
    for (const c of choicesOf(play)) queue.push(...Object.values(c.play_by_vehicle ?? {}));
  }
  return out;
}

// One column per vehicle: its start play, then plays reachable choices send it to. Switches stay out.
export function vehicleColumns(op: Operation, plays: Play[]): Column[] {
  const byId = new Map(plays.map((p) => [p.id, p]));
  const reach = reachablePlays(op, plays);
  return op.vehicle_ids.map((v) => {
    const out: ColumnPlay[] = [];
    const add = (id: string, via: string | null) => {
      if (!out.some((c) => c.play_id === id)) out.push({ play_id: id, play: byId.get(id) ?? null, via });
    };
    const start = op.assign?.[v];
    if (start) add(start, null);
    for (const p of reach) {
      for (const c of choicesOf(p)) {
        const next = c.play_by_vehicle?.[v];
        if (next) add(next, c.label);
      }
    }
    const reserve_for = Object.entries(op.reserve ?? {})
      .filter(([, ids]) => ids.includes(v))
      .map(([id]) => id);
    return { vehicle_id: v, reserve_for, plays: out };
  });
}
