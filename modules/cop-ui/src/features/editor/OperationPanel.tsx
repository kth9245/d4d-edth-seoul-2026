import type { Operation, VehicleSpec } from "../../contracts.gen";
import { MiniMap } from "../map/MiniMap";
import { startText, switchRows, vehicleRows } from "./operationPanel";

type Option = { id: string; name: string };

// A start role that does not fit the list (another domain) still shows as picked.
const withCurrent = (options: Option[], id: string | null, name: string | null): Option[] =>
  id && !options.some((o) => o.id === id) ? [...options, { id, name: name ?? id }] : options;

type Props = {
  op: Operation;
  vehicles: VehicleSpec[];
  roleName: (id: string) => string | null;
  onOpen: (roleId: string) => void;
  onSimulate?: () => void; // decision 0042: "▶ 시뮬레이션" next to the operation name
  startOptions?: (vehicleId: string) => { id: string; name: string }[]; // decision 0053
  onStartRole?: (vehicleId: string, roleId: string | null) => void;
};

// Operation panel (Part3-14): purpose and start, the zone with the vehicles at home, each vehicle's first role
// (picked here, decision 0053) and reserves, and what each whole-operation switch button does.
export function OperationPanel({ op, vehicles, roleName, onOpen, onSimulate, startOptions, onStartRole }: Props) {
  const rows = vehicleRows(op, vehicles, roleName);
  const switches = switchRows(op, roleName);
  const roleLink = (id: string, name: string | null) =>
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
            <tr><th>기체</th><th>종류</th><th>처음 Role</th><th>예비</th></tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td><b>{r.id}</b> <small>{r.name}</small></td>
                <td>{r.domain}</td>
                <td>
                  {startOptions && onStartRole ? (
                    <select className="start-role" aria-label={`${r.id} 처음 Role`} value={r.roleId ?? ""}
                      onChange={(e) => onStartRole(r.id, e.target.value || null)}>
                      <option value="">없음</option>
                      {withCurrent(startOptions(r.id), r.roleId, r.roleName).map((o) => <option key={o.id} value={o.id}>{o.name}</option>)}
                    </select>
                  ) : r.roleId ? roleLink(r.roleId, r.roleName) : <span className="muted">없음</span>}
                </td>
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
                <span key={m.vehicle} className="op-move">{m.vehicle} → {roleLink(m.roleId, m.roleName)}</span>
              ))}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
