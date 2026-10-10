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

// savePlay throws "/plays answered <status>: ..." when the gateway answered with an error, anything else when it
// did not answer at all; the operator needs to tell those apart (422 = malformed play, 500 = server bug).
export function saveErrorText(message: string): string {
  const m = message.match(/\/plays answered (\d{3})/);
  return m ? `저장 실패: 응답 ${m[1]}` : "저장 실패: 서버 응답 없음";
}

export function batteryText(est: Record<string, number> | undefined): string {
  return Object.entries(est ?? {})
    .map(([v, b]) => `${v} ${b.toFixed(1)}%`)
    .join(" · ");
}
