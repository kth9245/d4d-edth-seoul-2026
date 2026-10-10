import type { Operation, Role, VehicleSpec } from "../../contracts.gen";
import type { EnemyRow } from "./enemyRows";
import { OperationPanel } from "./OperationPanel";
import { StepCard } from "./StepCard";
import type { Column } from "./vehicleColumns";

type Props = {
  op: Operation;
  vehicles: VehicleSpec[];
  columns: Column[];
  enemies: EnemyRow[];
  roleName: (id: string) => string | null;
  onOpen: (roleId: string) => void;
  onSimulate?: () => void; // decision 0042
};

type CardsProps = { roleId: string; role: Role | null; roleName: (id: string) => string | null; onOpen: (roleId: string) => void };

// A role's name (opens it) and its cards, read only; a missing role says so.
function RoleCards({ roleId, role, roleName, onOpen }: CardsProps) {
  if (!role) return <div className="step-card missing">없는 Role: {roleId}</div>;
  return (
    <>
      <button className="link role-title" onClick={() => onOpen(roleId)}>
        {role.name}
      </button>
      {role.steps.map((s) => (
        <StepCard key={s.id} step={s} role={role} roleName={roleName} onOpen={onOpen} />
      ))}
    </>
  );
}

// Friendly vehicle columns, then the enemies under them (Part1-21): what each enemy does comes from the scenario.
export function OperationOverview({ op, vehicles, columns, enemies, roleName, onOpen, onSimulate }: Props) {
  return (
    <section className="overview">
      <OperationPanel op={op} vehicles={vehicles} roleName={roleName} onOpen={onOpen} onSimulate={onSimulate} />
      <h3 className="ov-section">아군</h3>
      <div className="columns friend-columns">
        {columns.map((col) => (
          <div key={col.vehicle_id} className="column">
            <div className="column-head">
              {col.vehicle_id}
              {col.reserve_for.length > 0 && <small> 예비: {col.reserve_for.join(", ")} 대신</small>}
            </div>
            {col.roles.map((cp) => (
              <div key={cp.role_id}>
                {cp.via && <div className="via">↓ '{cp.via}' 선택 시</div>}
                <RoleCards roleId={cp.role_id} role={cp.role} roleName={roleName} onOpen={onOpen} />
              </div>
            ))}
          </div>
        ))}
      </div>
      {enemies.length > 0 && (
        <>
          <h3 className="ov-section enemy">
            적 <small>시나리오 대본 · 운용자 조작 없음</small>
          </h3>
          <div className="columns enemy-columns">
            {enemies.map((e) => (
              <div key={e.id} className="column enemy-column">
                <div className="column-head">
                  {e.id} <small>{e.kind}</small>
                </div>
                <div className="enemy-meta">
                  <div>{e.appear}</div>
                  <div>{e.place}</div>
                  <div>{e.speed}</div>
                </div>
                <RoleCards roleId={e.roleId} role={e.role} roleName={roleName} onOpen={onOpen} />
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
