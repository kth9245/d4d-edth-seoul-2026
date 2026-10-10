import { useEffect, useState } from "react";
import type { OntologyView, Operation, Play, VehicleSpec } from "../../contracts.gen";
import { kindRows, reasonLine, reserveLines } from "./ontologyView";

// Editor "온톨로지" (decision 0038): the kind hierarchy, each vehicle's verdict per action with the path the
// server walked (GET /ontology runs the same inference as the play check) and why each reserve qualifies.
export function OntologyPanel({ op, plays, vehicles }: { op: Operation; plays: Play[]; vehicles: VehicleSpec[] }) {
  const [view, setView] = useState<OntologyView | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pick, setPick] = useState(vehicles[0]?.id ?? "");
  useEffect(() => {
    fetch("/ontology")
      .then(async (r) => {
        if (!r.ok) throw new Error(`/ontology answered ${r.status}`);
        setView((await r.json()) as OntologyView);
      })
      .catch((e: Error) => setError(e.message));
  }, []);
  if (error) return <div className="onto load-error">온톨로지를 불러오지 못했습니다 ({error})</div>;
  if (!view) return <div className="onto">불러오는 중…</div>;
  const onto = view.ontology;
  const chosen = view.vehicles.find((v) => v.vehicle_id === pick);
  return (
    <div className="onto">
      <h2>온톨로지</h2>
      <div className="onto-top">
        <section>
          <h3>종류 계층</h3>
          <ul className="onto-tree">
            {kindRows(onto, vehicles).map((k) => (
              <li key={k.id} style={{ paddingLeft: k.depth * 20 }}>
                <b>{k.label}</b>
                {k.adds && <span className="adds"> [{k.adds}]</span>}
                {k.vehicles.length > 0 && <span className="who"> {k.vehicles.join(" ")}</span>}
              </li>
            ))}
          </ul>
        </section>
        <section>
          <h3>행동 묶음</h3>
          <table className="onto-groups">
            <tbody>
              {onto.groups.map((g) => (
                <tr key={g.id}><th>{g.label}</th><td>{g.actions.join(" · ")}</td></tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>
      <h3>기체별 판정</h3>
      <div className="onto-pick">
        {view.vehicles.map((v) => (
          <button key={v.vehicle_id} className={v.vehicle_id === pick ? "on" : ""} onClick={() => setPick(v.vehicle_id)}>
            {v.vehicle_id}
          </button>
        ))}
      </div>
      <ul className="onto-reasons">
        {chosen?.reasons.map((r) => (
          <li key={r.action} className={r.allowed ? "yes" : "no"}>
            <i>{r.allowed ? "✓" : "✗"}</i> <code>{r.action}</code> {reasonLine(r, onto)}
          </li>
        ))}
      </ul>
      {reserveLines(op, plays, view, vehicles).map((line) => (
        <div key={line} className="onto-reserve">예비 자격: {line}</div>
      ))}
    </div>
  );
}
