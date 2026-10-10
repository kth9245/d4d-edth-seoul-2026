import { type Situation, targetsLabel } from "./situationCounts";

// Header, middle (Part1-32): targets per stage, most urgent first, and the decisions waiting (white = your turn).
export function SituationBar({ situation }: { situation: Situation }) {
  return (
    <div className="situation">
      <span className="lbl">{targetsLabel(situation.targets)}</span>
      {situation.stages.map((s) => (
        <span key={s.key} className={`c ${s.key}`}><b>{s.n}</b>{s.label}</span>
      ))}
      <span className="sep" />
      <span className={`c dec${situation.decisions ? "" : " none"}`}><b>{situation.decisions}</b>결정 대기</span>
    </div>
  );
}
