import type { Play } from "../../contracts.gen";
import { batteryText, issuesByStep, type SaveResult } from "./checkView";
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
};

function SaveStatus({ result }: { result?: SaveResult }) {
  if (!result) return null;
  if (result.state === "saving") return <span>검사 중…</span>;
  if (result.state === "error") return <span className="save-bad" title={result.message}>저장 실패: 서버 응답 없음</span>;
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

export function PlayWorkflow({ play, usage, playName, onOpen, result, onSave }: Props) {
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
      </div>
      {view?.general.map((i, k) => (
        <div key={k} className="issue">
          ⚠ {i.message}
        </div>
      ))}
      {play.steps.map((s) => (
        <StepCard key={s.id} step={s} play={play} playName={playName} onOpen={onOpen} issues={view?.byStep[s.id]} />
      ))}
    </section>
  );
}
