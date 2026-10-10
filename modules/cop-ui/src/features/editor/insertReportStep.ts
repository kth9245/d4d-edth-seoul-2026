import type { Role, Step } from "../../contracts.gen";

// "보고 카드 끼워 넣기" (Part3-12, decisions 0003 and 0031): put an operator report with one choice right before
// an approach step that the check found unguarded. The report step holds; choosing "approve" continues to the
// approach step through its operator_choice exit, and every exit that went to the approach step now goes to the
// report first. Returns a new role; the input is not changed.
export function insertReportStep(role: Role, approachId: string): Role {
  const at = role.steps.findIndex((s) => s.id === approachId);
  if (at < 0) return role;
  const target = role.steps[at];
  const ids = new Set(role.steps.map((s) => s.id));
  let id = `${approachId}_report`;
  for (let n = 2; ids.has(id); n++) id = `${approachId}_report-${n}`;

  const report: Step = {
    id,
    name: "보고",
    do: { kind: "hold", params: {} },
    on: [{ cond: { kind: "operator_choice", params: { choice: "approve" } }, go_step: approachId }],
    report: { text: `표적 발견 · ${target.name} 전 운용자 확인`, choices: [{ id: "approve", label: `${target.name} 승인`, role_by_vehicle: {} }] },
    ui: {},
  };
  const redirected = role.steps.map((s) => ({
    ...s,
    on: (s.on ?? []).map((e) => (e.go_step === approachId ? { ...e, go_step: id } : e)),
  }));
  return { ...role, steps: [...redirected.slice(0, at), report, ...redirected.slice(at)] };
}
