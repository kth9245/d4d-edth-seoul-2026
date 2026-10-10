import type { Target } from "../../contracts.gen";
import type { Stage } from "./targetStage";
import type { VehicleRow } from "./vehicleRows";

const KIND_KO: Record<string, string> = { boat: "보트", fast_boat: "고속정", person: "사람", unknown: "미상" };
const tone = (r: number) => (r >= 0.7 ? "hi" : r >= 0.4 ? "mid" : "lo");
const QUIET: Record<string, number> = { gone: 1, never: 2 };

// Left column (Part1-32): our vehicles (what each does, its target, battery) and the targets by risk with their
// own stage. A vehicle row selects it like its map marker; with a vehicle selected a target row points at it.
export function RosterPanel({ rows, targets, stages, selected, onVehicle, onTarget }: {
  rows: VehicleRow[]; targets: Target[]; stages: Record<string, Stage>; selected: string | null;
  onVehicle: (id: string) => void; onTarget: (id: string) => void;
}) {
  const busy = rows.filter((r) => r.status === "active").length;
  const back = rows.filter((r) => r.status === "returning").length;
  const idle = rows.length - busy - back;
  const counts = [busy && `임무 ${busy}`, back && `귀환 ${back}`, idle && `대기 ${idle}`].filter(Boolean).join(" · ");
  const ts = [...targets].sort((a, b) => (QUIET[stages[a.id]?.key] ?? 0) - (QUIET[stages[b.id]?.key] ?? 0)
    || (b.threat ?? 0) - (a.threat ?? 0));
  const gone = targets.filter((t) => t.neutralized_ms != null).length;
  return (
    <aside className="roster">
      <h3>아군 <b>{rows.length}</b><small>{counts}</small></h3>
      {rows.map((r) => (
        <button key={r.id} type="button" className={`ro st-${r.status}${r.id === selected ? " sel" : ""}`} onClick={() => onVehicle(r.id)}>
          <span className="l1"><b>{r.id}</b><span className="doing">{r.doing}</span>{r.waiting && <span className="chip">결정 대기</span>}</span>
          <span className="l2">
            <span className="kind">{r.kind}</span>
            {r.target && <span className={`tgt${r.striking ? " strike" : ""}`}>{r.striking ? "타격 →" : "→"} {r.target}</span>}
            <span className={`bat${r.low ? " low" : ""}`}><i style={{ width: `${r.battery}%` }} /></span>
            <em className={r.low ? "low" : ""}>{r.battery}%</em>
          </span>
        </button>
      ))}
      <h3 className="en">적 <b>{targets.length - gone}</b><small>{gone ? `무력화 ${gone} · ` : ""}위험도 순</small></h3>
      {ts.map((t) => {
        const s = stages[t.id];
        const r = (t.threat ?? 0) / 100;
        const quiet = s?.key === "gone" || s?.key === "never";
        return (
          <button key={t.id} type="button" className={`ro en ${quiet ? s.key : tone(r)}`} onClick={() => onTarget(t.id)}>
            <span className="l1">
              <b>{t.id}</b><span className="doing">{KIND_KO[t.kind] ?? t.kind}</span>
              {t.rf_detected && !quiet && <span className="rf">RF</span>}
              <span className="risk">{quiet ? "—" : r.toFixed(2)}</span>
            </span>
            <span className="l2"><span className={`stg ${s?.key}${s?.away ? " away" : ""}`}>{s?.label}</span><span className="det">{s?.detail}</span></span>
            {!quiet && <span className="rbar"><i style={{ width: `${Math.min(100, r * 100)}%` }} /></span>}
          </button>
        );
      })}
    </aside>
  );
}
