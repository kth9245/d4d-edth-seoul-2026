import type { ObjectGraph, ObjectNode } from "../../contracts.gen";

export const COL_W = 260;
export const ROW_H = 84;
const COLUMN: Record<ObjectNode["type"], number> = { vehicle: 0, report: 1, decision: 2, command: 3, block: 3, target: 4 };
export const REL_KO: Record<string, string> = { reported: "보고함", about: "이 표적", answers: "답함",
  from_decision: "이 결정에서 나옴", sent_to: "이 기체에", aims_at: "겨눔", blocked: "막음" };

// Fixed columns by object type (vehicle, card, decision, command, target); in a column the earliest first,
// blocks after commands, objects without a time last (decision 0038).
export function layoutObjectGraph(g: ObjectGraph): Record<string, { x: number; y: number }> {
  const cols = new Map<number, ObjectNode[]>();
  for (const n of g.nodes) cols.set(COLUMN[n.type], [...(cols.get(COLUMN[n.type]) ?? []), n]);
  const out: Record<string, { x: number; y: number }> = {};
  for (const [c, nodes] of cols) {
    nodes.sort((a, b) => Number(a.type === "block") - Number(b.type === "block")
      || (a.t_ms ?? Number.MAX_SAFE_INTEGER) - (b.t_ms ?? Number.MAX_SAFE_INTEGER) || a.id.localeCompare(b.id));
    nodes.forEach((n, i) => { out[n.id] = { x: c * COL_W, y: i * ROW_H }; });
  }
  return out;
}
