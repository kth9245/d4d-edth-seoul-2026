import type { Choice, Operation, Role } from "../../contracts.gen";

export type ColumnRole = { role_id: string; role: Role | null; via: string | null };
export type Column = { vehicle_id: string; reserve_for: string[]; roles: ColumnRole[] };

export function choicesOf(role: Role): Choice[] {
  return role.steps.flatMap((s) => s.report?.choices ?? []);
}

// Roles the operation can reach: assigned roles, then every role a report choice points to (BFS, each once).
export function reachableRoles(op: Operation, roles: Role[]): Role[] {
  const byId = new Map(roles.map((p) => [p.id, p]));
  const queue = Object.values(op.assign ?? {});
  const seen = new Set<string>();
  const out: Role[] = [];
  while (queue.length > 0) {
    const id = queue.shift()!;
    if (seen.has(id)) continue;
    seen.add(id);
    const role = byId.get(id);
    if (!role) continue;
    out.push(role);
    for (const c of choicesOf(role)) queue.push(...Object.values(c.role_by_vehicle ?? {}));
  }
  return out;
}

// One column per vehicle: its start role, then roles reachable choices send it to. Switches stay out.
export function vehicleColumns(op: Operation, roles: Role[]): Column[] {
  const byId = new Map(roles.map((p) => [p.id, p]));
  const reach = reachableRoles(op, roles);
  return op.vehicle_ids.map((v) => {
    const out: ColumnRole[] = [];
    const add = (id: string, via: string | null) => {
      if (!out.some((c) => c.role_id === id)) out.push({ role_id: id, role: byId.get(id) ?? null, via });
    };
    const start = op.assign?.[v];
    if (start) add(start, null);
    for (const p of reach) {
      for (const c of choicesOf(p)) {
        const next = c.role_by_vehicle?.[v];
        if (next) add(next, c.label);
      }
    }
    const reserve_for = Object.entries(op.reserve ?? {})
      .filter(([, ids]) => ids.includes(v))
      .map(([id]) => id);
    return { vehicle_id: v, reserve_for, roles: out };
  });
}
