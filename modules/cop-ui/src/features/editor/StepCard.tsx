import type { Play, Step, ValidationIssue } from "../../contracts.gen";
import { describeAction, describeCondition } from "./describe";

type Props = {
  step: Step;
  play: Play;
  playName: (id: string) => string | null;
  onOpen: (playId: string) => void;
  issues?: ValidationIssue[];
};

export function StepCard({ step, play, playName, onOpen, issues = [] }: Props) {
  const stepName = (id: string) => play.steps.find((s) => s.id === id)?.name;
  return (
    <div className={issues.length > 0 ? "step-card has-issues" : "step-card"}>
      <div className="step-name">
        {step.id === play.entry ? "▶ " : ""}
        {step.name}
      </div>
      <div className="step-do">{describeAction(step.do)}</div>
      {(step.on ?? []).map((e, i) => (
        <div key={i} className="step-exit">
          {describeCondition(e.cond)} → {stepName(e.go_step) ?? <span className="missing">{e.go_step}</span>}
        </div>
      ))}
      {step.report && (
        <div className="step-report">
          <div>■ {step.report.text}</div>
          {(step.report.choices ?? []).map((c) => (
            <div key={c.id} className="choice">
              <b>[{c.label}]</b>
              {Object.entries(c.play_by_vehicle ?? {}).map(([v, pid]) => {
                const name = playName(pid);
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
    </div>
  );
}
