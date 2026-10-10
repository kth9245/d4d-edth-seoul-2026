import type { Operation, VehicleSpec } from "../../contracts.gen";
import { MiniMap } from "../map/MiniMap";
import { startText, switchRows, vehicleRows } from "./operationPanel";

type Props = {
  op: Operation;
  vehicles: VehicleSpec[];
  playName: (id: string) => string | null;
  onOpen: (playId: string) => void;
  onSimulate?: () => void; // decision 0042: "▶ 시뮬레이션" next to the operation name
};

// Operation panel (Part3-14, display only): purpose and start, the zone with the vehicles at home, each vehicle's
// first play and reserves, and what each whole-operation switch button does. Editing the operation is not here.
export function OperationPanel({ op, vehicles, playName, onOpen, onSimulate }: Props) {
  const rows = vehicleRows(op, vehicles, playName);
  const switches = switchRows(op, playName);
  const playLink = (id: string, name: string | null) =>
    name ? <button className="link" onClick={() => onOpen(id)}>{name}</button> : <span className="missing">{id}</span>;
  return (
    <section className="op-panel" aria-label="작전 설정">
      <div className="op-head">
        <div className="op-title">
          <h2>{op.name}</h2>
          {onSimulate && <button className="save simulate" onClick={onSimulate}>▶ 시뮬레이션</button>}
        </div>
        <div className="op-meta">
          {op.purpose && <span>{op.purpose}</span>}
          <span>{startText(op.started_ms)}</span>
          <span>기체 {op.vehicle_ids.length}대</span>
        </div>
      </div>
      <div className="op-body">
        <MiniMap zone={op.zone} vehicles={vehicles.filter((v) => op.vehicle_ids.includes(v.id))} />
        <table className="op-vehicles">
          <thead>
            <tr><th>기체</th><th>종류</th><th>처음 플레이</th><th>예비</th></tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td><b>{r.id}</b> <small>{r.name}</small></td>
                <td>{r.domain}</td>
                <td>{r.playId ? playLink(r.playId, r.playName) : <span className="muted">없음</span>}</td>
                <td>{r.reserves.length ? r.reserves.join(" → ") : <span className="muted">-</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {switches.length > 0 && (
        <div className="op-switches">
          {switches.map((s) => (
            <div key={s.id} className="op-switch">
              <span className="switch">{s.label}</span>
              {s.moves.map((m) => (
                <span key={m.vehicle} className="op-move">{m.vehicle} → {playLink(m.playId, m.playName)}</span>
              ))}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
