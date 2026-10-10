import type { Play } from "../../contracts.gen";
import { batteryText, issuesByStep, saveErrorText, type SaveResult } from "./checkView";
import { DOMAIN_LABEL } from "./describe";
import type { Usage } from "./playUsage";
import { StepCard } from "./StepCard";

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

export function PlayWorkflow({ play, usage, playName, onOpen, result, onSave, edited, freshStep, onInsertReport }: Props) {
  const view = result?.state === "done" ? issuesByStep(result.check, play) : null;
  return (
    <section className="workflow">
      <h2>
        {play.name} <small>{play.domains.map((d) => DOMAIN_LABEL[d]).join("·") || "영역 없음"}</small>
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
      {play.steps.map((s) => (
        <StepCard key={s.id} step={s} play={play} playName={playName} onOpen={onOpen} issues={view?.byStep[s.id]}
          fresh={s.id === freshStep} onInsertReport={onInsertReport && (() => onInsertReport(s.id))} />
      ))}
    </section>
  );
}
