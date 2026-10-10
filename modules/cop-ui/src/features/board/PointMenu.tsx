import type { MenuRole } from "./vehicleMenuRoles";

// Role menu beside a pointed target (decisions 0048, 0049, 0058): each button says what changes (current role → new
// role · target) and pressing it is the approval. An armed vehicle also gets its strike role (red).
export function PointMenu({ vehicle, target, x, y, roles, current, onPick, onCancel }: {
  vehicle: string; target: string; x: number; y: number; roles: MenuRole[]; current: string;
  onPick: (role: string) => void; onCancel: () => void;
}) {
  return (
    <div className="pickpop" style={{ left: x + 16, top: Math.max(8, y - 20) }}>
      <div className="ph">{vehicle} → {target}</div>
      {roles.length ? roles.map((r) => (
        <button key={r.id} type="button" className={r.strike ? "strike" : ""} onClick={() => onPick(r.id)}>
          {r.name}<small>{current} → {r.name} · 표적 {target}</small></button>
      )) : <div className="pn">{vehicle}가 표적에 쓸 수 있는 Role이 없습니다.</div>}
      <button type="button" className="x" onClick={onCancel}>취소</button>
      <div className="pn">누르면 바로 바뀝니다.</div>
    </div>
  );
}
