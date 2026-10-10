import { useState } from "react";
import type { SeenTarget } from "./seenTargets";
import type { MenuRole } from "./vehicleMenuRoles";

// The menu under the picked roster row (Part1-32.1, decisions 0058, 0059): move by a map click, target-less roles
// switch at once, a target role opens the enemies seen now under it and a pick points the vehicle at that one.
// Every button shows what changes; the press is the approval.
export function VehicleMenu({ current, plain, target, seen, onRole, onPoint }: {
  current: string; plain: MenuRole[]; target: MenuRole[]; seen: SeenTarget[];
  onRole: (role: string, name: string) => void; onPoint: (role: string, target: string) => void;
}) {
  const [open, setOpen] = useState<string | null>(null);
  return (
    <div className="vmenu">
      <div className="vm-move">이동 · 지도를 누르면 그 지점으로</div>
      {plain.length > 0 && (
        <div className="vm-plain">
          <div className="vm-h">Role 바꾸기 · 누르면 바로</div>
          {plain.map((r) => (
            <button key={r.id} type="button" data-role={r.id} onClick={() => onRole(r.id, r.name)}>
              {r.name}<small>{current} → {r.name}</small>
            </button>
          ))}
        </div>
      )}
      {target.length > 0 && <div className="vm-h">표적에 붙이기 · 포착된 적을 고르세요</div>}
      {target.map((r) => (
        <div key={r.id} className="vm-t">
          <button type="button" data-role={r.id} className={r.strike ? "strike" : ""} aria-expanded={open === r.id}
            onClick={() => setOpen(open === r.id ? null : r.id)}>{r.name}</button>
          {open === r.id && (seen.length > 0 ? seen.map((t) => (
            <button key={t.id} type="button" className="vm-pick" data-target={t.id} onClick={() => onPoint(r.id, t.id)}>
              <b>{t.id}</b><span>{t.kind}</span><em>{(t.threat / 100).toFixed(2)}</em><span>{t.distM} m</span>
            </button>
          )) : <div className="vm-none">지금 포착된 적이 없습니다</div>)}
        </div>
      ))}
    </div>
  );
}
