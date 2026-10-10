import { Handle, type Node, type NodeProps, Position } from "@xyflow/react";
import type { Play, Step, ValidationIssue } from "../../contracts.gen";
import { ACTION_LABEL, describeAction } from "./describe";
import { exitText } from "./playGraph";

export type StepNodeData = {
  step: Step;
  play: Play;
  issues: ValidationIssue[];
  fresh: boolean; // just added by "보고 카드 끼워 넣기"
  playName: (id: string) => string | null;
  onOpen: (playId: string) => void;
  onInsertReport?: () => void;
};
export type StepNodeType = Node<StepNodeData, "step">;

// One step as a graph card (Part3-10.1): 행동 / 보고 / 연결 sections; every exit row has its own handle on the
// right edge so its edge leaves from that row. Buttons carry "nodrag" so clicking them never drags the card.
export function StepNode({ data }: NodeProps<StepNodeType>) {
  const { step, play, issues, fresh, playName, onOpen, onInsertReport } = data;
  const stepName = (id: string) => play.steps.find((s) => s.id === id)?.name;
  const unguarded = issues.some((i) => i.code === "missing_report_point");
  const exits = step.on ?? [];
  return (
    <div className={`step-node${issues.length ? " has-issues" : ""}${fresh ? " fresh" : ""}`}>
      <Handle type="target" position={Position.Left} className="sn-in" />
      {fresh && <span className="sn-badge">변경</span>}
      <div className="sn-head">
        <b>{step.name}</b>
        {step.id === play.entry && <span className="sn-tag">시작</span>}
        <code>{step.id}</code>
      </div>
      <div className="sn-sec">
        <div className="sn-label">행동 <span className="chip">{ACTION_LABEL[step.do.kind] ?? step.do.kind}</span></div>
        <div className="sn-text">{describeAction(step.do)}</div>
      </div>
      {step.report && (
        <div className="sn-sec">
          <div className="sn-label">보고</div>
          <div className="sn-text">{step.report.text}</div>
          {(step.report.choices ?? []).map((c) => (
            <div key={c.id} className="sn-choice">
              <span className="chip choice">{c.label}</span>
              {Object.entries(c.play_by_vehicle ?? {}).map(([v, pid]) => (
                <div key={v} className="sn-target">
                  {v} →{" "}
                  {playName(pid) ? (
                    <button className="link nodrag" onClick={() => onOpen(pid)}>{playName(pid)}</button>
                  ) : (
                    <span className="missing">{pid}</span>
                  )}
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
      {exits.length > 0 && (
        <div className="sn-sec">
          <div className="sn-label">연결</div>
          {exits.map((e, i) => (
            <div key={i} className="sn-exit">
              → {exitText(step, e.cond)} <b>{stepName(e.go_step) ?? <span className="missing">{e.go_step}</span>}</b>
              <Handle type="source" position={Position.Right} id={`exit-${i}`} className="sn-out" />
            </div>
          ))}
        </div>
      )}
      {issues.map((i, k) => <div key={k} className="issue">⚠ {i.message}</div>)}
      {unguarded && onInsertReport && (
        <button className="insert-report nodrag" onClick={onInsertReport}>보고 카드 끼워 넣기</button>
      )}
    </div>
  );
}
