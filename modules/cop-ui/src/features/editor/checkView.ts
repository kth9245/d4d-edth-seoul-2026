import type { Play, PlayCheck, ValidationIssue } from "../../contracts.gen";

export type IssueView = { byStep: Record<string, ValidationIssue[]>; general: ValidationIssue[] };

// Issues on a step of this play go next to that card; the rest (no step, unknown step) go on the play.
export function issuesByStep(check: PlayCheck, play: Play): IssueView {
  const ids = new Set(play.steps.map((s) => s.id));
  const out: IssueView = { byStep: {}, general: [] };
  for (const i of check.issues) {
    if (i.step_id && ids.has(i.step_id)) (out.byStep[i.step_id] ??= []).push(i);
    else out.general.push(i);
  }
  return out;
}

export type SaveResult =
  | { state: "saving" }
  | { state: "done"; check: PlayCheck }
  | { state: "error"; message: string };

export function batteryText(est: Record<string, number> | undefined): string {
  return Object.entries(est ?? {})
    .map(([v, b]) => `${v} ${b.toFixed(1)}%`)
    .join(" · ");
}
