import { useEffect, useState } from "react";
import type { Frame, Role, Switch, SwitchIn } from "../../contracts.gen";
import { fetchOperation } from "../live/fetchOperation";
import { fetchRoles } from "../live/fetchRoles";
import { postSwitch } from "./injectionRequests";
import type { Sent } from "./postJson";

// Side column, above the cards: ask for a role switch (contracts/API.md §4). Whole-operation buttons come from
// Operation.switches; a partial switch picks one vehicle and one role (event 4: d2 → fast boat tracking).
// A request only makes a pending injection; its card below carries approve / reject.
export function SwitchPanel({ frame }: { frame: Frame | null }) {
  const [switches, setSwitches] = useState<Switch[] | null>(null);
  const [roles, setRoles] = useState<Role[]>([]);
  const [vehicle, setVehicle] = useState("");
  const [role, setRole] = useState("");
  const [busy, setBusy] = useState(false);
  const [last, setLast] = useState<Sent | null>(null);
  const hasFrame = frame !== null;
  useEffect(() => {
    // Read once the gateway answers (the screen may open before it is up).
    if (!hasFrame || switches !== null) return;
    fetchOperation().then((op) => setSwitches(op?.switches ?? []));
    fetchRoles().then(setRoles);
  }, [hasFrame, switches]);
  if (!frame) return null;

  const request = async (body: SwitchIn) => {
    if (busy) return;
    setBusy(true);
    setLast(await postSwitch(body));
    setBusy(false);
  };

  return (
    <section className="switchpanel">
      {(switches ?? []).length > 0 && (
        <div className="whole">
          {switches!.map((s) => (
            <button key={s.id} disabled={busy} onClick={() => request({ switch_id: s.id })}>{s.label}</button>
          ))}
        </div>
      )}
      <div className="partial">
        <select aria-label="전환할 기체" value={vehicle} onChange={(e) => setVehicle(e.target.value)}>
          <option value="">기체</option>
          {frame.vehicles.map((v) => <option key={v.id} value={v.id}>{v.id}</option>)}
        </select>
        <select aria-label="새 Role" value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="">Role</option>
          {roles.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
        <button disabled={busy || !vehicle || !role} onClick={() => request({ role_by_vehicle: { [vehicle]: role } })}>
          전환 요청
        </button>
      </div>
      {last?.ok && <div className="note">요청됨 {last.id} · 위 결정 대기에서 승인</div>}
      {last && !last.ok && <div className="note error">요청 실패: {last.error}</div>}
    </section>
  );
}
