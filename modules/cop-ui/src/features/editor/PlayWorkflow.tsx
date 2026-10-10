import { useState } from "react";
import type { GeoPoint, Play, RouteDef } from "../../contracts.gen";
import { batteryText, issuesByStep, saveErrorText, type SaveResult } from "./checkView";
import { DOMAIN_LABEL } from "./describe";
import type { Usage } from "./playUsage";
import { addStepAfter, removeStep } from "./editStep";
import { PlayGraph } from "./PlayGraph";
import { StepEditor } from "./StepEditor";

type Props = {
  play: Play;
  usage: Usage[];
  playName: (id: string) => string | null;
  onOpen: (playId: string) => void;
  result?: SaveResult;
  onSave: () => void;
  edited?: boolean;
  freshStep?: string;
  onInsertReport?: (stepId: string) => void;
  onBack?: () => void;
  backLabel?: string;
  // Card editing (Part3-12.1): the changed play goes up unsaved; freshStep marks a card just added.
  onEdit?: (next: Play, freshStep?: string) => void;
  vehicleIds?: string[];
  plays?: { id: string; name: string }[];
  fallbackPoint?: GeoPoint | null;
  routes?: RouteDef[]; // decision 0044: for the card panel's route select
  enemy?: boolean; // the play an enemy follows (no route select, no T+)
};

function SaveStatus({ result }: { result?: SaveResult }) {
  if (!result) return null;
  if (result.state === "saving") return <span>검사 중…</span>;
  if (result.state === "error") return <span className="save-bad" title={result.message}>{saveErrorText(result.message)}</span>;
  const { check } = result;
  const battery = batteryText(check.est_return_battery);
  return (
    <>
      {check.ok ? (
        <span className="save-ok">저장됨 · 작전을 시작 전으로 되돌림</span>
      ) : (
        <span className="save-bad">저장 안 됨 · 오류 {check.issues.length}개</span>
      )}
      {battery && <span className="battery">예상 귀환 배터리 {battery}</span>}
    </>
  );
}

export function PlayWorkflow({ play, usage, playName, onOpen, result, onSave, edited, freshStep, onInsertReport, onBack, backLabel,
  onEdit, vehicleIds = [], plays = [], fallbackPoint = null, routes = [], enemy = false }: Props) {
  const view = result?.state === "done" ? issuesByStep(result.check, play) : null;
  const [picked, setPicked] = useState<string | null>(null);
  const step = onEdit ? play.steps.find((s) => s.id === picked) : undefined;
  return (
    <section className="workflow">
      {onBack && <button className="back" onClick={onBack}>← 뒤로 · {backLabel}</button>}
      <h2>
        {play.name} <small>{play.domains.map((d) => DOMAIN_LABEL[d]).join("·") || "영역 없음"}</small>
        {play.origin === "ai_draft" && !play.approved && <span className="ai-badge">AI 초안 · 승인 전</span>}
      </h2>
      <div className="usage">
        {usage.length === 0
          ? "이 작전에서 쓰는 기체 없음"
          : usage.map((u, i) => (
              <div key={i}>
                {u.vehicle_id} — {u.how}
              </div>
            ))}
      </div>
      <div className="save-bar">
        <button className="save" onClick={onSave} disabled={result?.state === "saving"}>
          저장
        </button>
        <SaveStatus result={result} />
        {edited && !(result?.state === "done" && result.check.ok) && <span className="edited">고친 내용 있음 · 아직 저장 안 됨</span>}
      </div>
      {view?.general.map((i, k) => (
        <div key={k} className="issue">
          ⚠ {i.message}
        </div>
      ))}
      <div className="workflow-body">
        <PlayGraph play={play} issues={view?.byStep ?? {}} freshStep={freshStep} playName={playName} onOpen={onOpen}
          onInsertReport={onInsertReport} selectedStep={step?.id ?? null} onSelectStep={setPicked} />
        {step && onEdit && (
          <StepEditor play={play} step={step} vehicleIds={vehicleIds} plays={plays} fallbackPoint={fallbackPoint} routes={routes} enemy={enemy} onChange={(next) => onEdit(next)}
            onAddAfter={() => {
              const { play: next, id } = addStepAfter(play, step.id);
              onEdit(next, id);
              setPicked(id);
            }}
            onRemove={() => {
              onEdit(removeStep(play, step.id));
              setPicked(null);
            }}
            onClose={() => setPicked(null)} />
        )}
      </div>
    </section>
  );
}
