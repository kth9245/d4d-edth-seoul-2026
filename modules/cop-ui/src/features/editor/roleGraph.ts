import type { Condition, Role, Step } from "../../contracts.gen";
import { describeCondition } from "./describe";

// Graph view of one role (Part3-10.1): positions for the step cards and one edge per exit.

export const COL_W = 440; // card width (300) + room for the edge label between columns
export const CARD_GAP = 48;

// An operator_choice exit reads as the choice the operator presses on this step's report (decision 0031).
export function exitText(step: Step, cond: Condition): string {
  const choice = cond.kind === "operator_choice" ? step.report?.choices?.find((c) => c.id === cond.params?.choice) : undefined;
  return choice ? `'${choice.label}' 선택 시` : describeCondition(cond);
}

// Rough card height, on the high side so cards in one column never overlap.
export function estimateHeight(s: Step): number {
  const exits = s.on ?? [];
  const choices = s.report?.choices ?? [];
  const targets = choices.reduce((n, c) => n + Object.keys(c.role_by_vehicle ?? {}).length, 0);
  const report = s.report ? 52 + 26 * choices.length + 20 * targets : 0;
  return 46 + 70 + report + (exits.length ? 36 + 26 * exits.length : 0) + 40;
}

// Entry in column 0, each step one column after the first step that leads to it (breadth first, so the
// shortest path wins); steps the entry cannot reach go in one more column. Columns are centred vertically.
export function layoutSteps(role: Role): Record<string, { x: number; y: number }> {
  const byId = new Map(role.steps.map((s) => [s.id, s]));
  const depth = new Map<string, number>();
  const queue = byId.has(role.entry) ? [role.entry] : [];
  if (queue.length) depth.set(role.entry, 0);
  while (queue.length) {
    const id = queue.shift()!;
    for (const e of byId.get(id)!.on ?? []) {
      if (byId.has(e.go_step) && !depth.has(e.go_step)) {
        depth.set(e.go_step, depth.get(id)! + 1);
        queue.push(e.go_step);
      }
    }
  }
  const last = Math.max(-1, ...depth.values()) + 1;
  const columns: Step[][] = [];
  const order = [...[...depth.keys()].map((id) => byId.get(id)!), ...role.steps.filter((s) => !depth.has(s.id))];
  for (const s of order) (columns[depth.get(s.id) ?? last] ??= []).push(s);
  const height = (col: Step[]) => col.reduce((h, s) => h + estimateHeight(s), 0) + CARD_GAP * (col.length - 1);
  const tallest = Math.max(0, ...columns.map((c) => (c ? height(c) : 0)));
  const pos: Record<string, { x: number; y: number }> = {};
  columns.forEach((col, i) => {
    let y = (tallest - height(col)) / 2;
    for (const s of col) {
      pos[s.id] = { x: i * COL_W, y };
      y += estimateHeight(s) + CARD_GAP;
    }
  });
  return pos;
}

export type EdgeKind = "normal" | "choice" | "issue";
export interface StepEdge { id: string; source: string; sourceHandle: string; target: string; label: string; kind: EdgeKind }

// One edge per exit, leaving from that exit's handle. Choice edges (operator approval) and edges into a step
// that failed the check are told apart; an exit to a step the role lacks has no edge (its card shows it red).
export function stepEdges(role: Role, issueSteps: Set<string>): StepEdge[] {
  const ids = new Set(role.steps.map((s) => s.id));
  return role.steps.flatMap((s) =>
    (s.on ?? []).flatMap((e, i): StepEdge[] => ids.has(e.go_step)
      ? [{ id: `${s.id}:${i}`, source: s.id, sourceHandle: `exit-${i}`, target: e.go_step, label: exitText(s, e.cond),
        kind: e.cond.kind === "operator_choice" ? "choice" : issueSteps.has(e.go_step) ? "issue" : "normal" }]
      : []),
  );
}
