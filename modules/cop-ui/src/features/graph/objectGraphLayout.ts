import type { ObjectGraph, ObjectNode } from "../../contracts.gen";

export const COL_W = 260;
export const ROW_H = 84;
// Blocks get their own column so the "막음" link to its command never runs inside one column.
const COLUMN: Record<ObjectNode["type"], number> = { vehicle: 0, report: 1, decision: 2, command: 3, block: 4, target: 5 };
export const REL_KO: Record<string, string> = { reported: "보고함", about: "이 표적", answers: "답함",
  from_decision: "이 결정에서 나옴", sent_to: "이 기체에", aims_at: "겨눔", blocked: "막음" };

// Fixed columns by object type (vehicle, card, decision, command, block, target); in a column the earliest first,
// objects without a time last (decision 0038).
export function layoutObjectGraph(g: ObjectGraph): Record<string, { x: number; y: number }> {
  const cols = new Map<number, ObjectNode[]>();
  for (const n of g.nodes) cols.set(COLUMN[n.type], [...(cols.get(COLUMN[n.type]) ?? []), n]);
  const out: Record<string, { x: number; y: number }> = {};
  for (const [c, nodes] of cols) {
    nodes.sort((a, b) => (a.t_ms ?? Number.MAX_SAFE_INTEGER) - (b.t_ms ?? Number.MAX_SAFE_INTEGER) || a.id.localeCompare(b.id));
    nodes.forEach((n, i) => { out[n.id] = { x: c * COL_W, y: i * ROW_H }; });
  }
  return out;
}

export interface DrawnLink { id: string; source: string; target: string; label: string; reversed: boolean }

// Every link is drawn from the left column to the right one (nodes take links on the left and give them on the
// right). A link whose real direction points left is flipped and marked reversed: its arrow goes on the start.
export function orientLinks(g: ObjectGraph): DrawnLink[] {
  const col = new Map(g.nodes.map((n) => [n.id, COLUMN[n.type]]));
  return g.links.map((l) => {
    const reversed = (col.get(l.src) ?? 0) > (col.get(l.dst) ?? 0);
    return { id: `${l.src}-${l.rel}-${l.dst}`, source: reversed ? l.dst : l.src, target: reversed ? l.src : l.dst,
      label: REL_KO[l.rel] ?? l.rel, reversed };
  });
}
