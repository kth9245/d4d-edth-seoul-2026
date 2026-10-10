import type { Role, Step, ValidationIssue } from "../../contracts.gen";
import { describeAction } from "./describe";
import { exitText } from "./roleGraph";

type Props = {
  step: Step;
  role: Role;
  roleName: (id: string) => string | null;
  onOpen: (roleId: string) => void;
  issues?: ValidationIssue[];
  fresh?: boolean; // just added by "보고 카드 끼워 넣기"
  onInsertReport?: () => void;
};

export function StepCard({ step, role, roleName, onOpen, issues = [], fresh, onInsertReport }: Props) {
  const stepName = (id: string) => role.steps.find((s) => s.id === id)?.name;
  const unguarded = issues.some((i) => i.code === "missing_report_point");
  return (
    <div className={`step-card${issues.length > 0 ? " has-issues" : ""}${fresh ? " fresh" : ""}`}>
      <div className="step-name">
        {step.id === role.entry ? "▶ " : ""}
        {step.name}
      </div>
      <div className="step-do">{describeAction(step.do)}</div>
      {(step.on ?? []).map((e, i) => (
        <div key={i} className="step-exit">
          {exitText(step, e.cond)} → {stepName(e.go_step) ?? <span className="missing">{e.go_step}</span>}
        </div>
      ))}
      {step.report && (
        <div className="step-report">
          <div>■ {step.report.text}</div>
          {(step.report.choices ?? []).map((c) => (
            <div key={c.id} className="choice">
              <b>[{c.label}]</b>
              {Object.entries(c.role_by_vehicle ?? {}).map(([v, pid]) => {
                const name = roleName(pid);
                return (
                  <div key={v} className="choice-target">
                    {v} →{" "}
                    {name ? (
                      <button className="link" onClick={() => onOpen(pid)}>
                        {name}
                      </button>
                    ) : (
                      <span className="missing">{pid}</span>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      )}
      {issues.map((i, k) => (
        <div key={k} className="issue">
          ⚠ {i.message}
        </div>
      ))}
      {unguarded && onInsertReport && (
        <button className="insert-report" onClick={onInsertReport}>보고 카드 끼워 넣기</button>
      )}
    </div>
  );
}
