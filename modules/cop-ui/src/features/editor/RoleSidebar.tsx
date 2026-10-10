import type { ReactNode } from "react";
import type { ScenarioInfo } from "../../contracts.gen";
import type { RoleGroup } from "./groupRoles";

export const OVERVIEW = "__overview__";
export const ONTOLOGY = "__ontology__"; // decision 0038

type Props = {
  groups: RoleGroup[];
  selected: string;
  showOverview: boolean;
  onSelect: (id: string) => void;
  top?: ReactNode; // above the list: the AI draft box (Part3-13)
  // Decision 0042: the operations the gateway can run; picking another makes it the running one.
  scenarios?: ScenarioInfo[];
  onPickScenario?: (id: string) => void;
};

export function RoleSidebar({ groups, selected, showOverview, onSelect, top, scenarios = [], onPickScenario }: Props) {
  const item = (id: string, label: string) => (
    <button key={id} className={selected === id ? "item on" : "item"} onClick={() => onSelect(id)}>
      {label}
    </button>
  );
  return (
    <nav className="role-sidebar">
      {top}
      {scenarios.length > 0 && (
        <div className="ops">
          <div className="group">작전</div>
          {scenarios.map((s) => (
            <button key={s.id} className={s.active ? "item op active" : "item op"} title={s.purpose}
              onClick={() => !s.active && onPickScenario?.(s.id)}>
              {s.name}
            </button>
          ))}
        </div>
      )}
      {showOverview && item(OVERVIEW, "작전 개요")}
      {showOverview && item(ONTOLOGY, "온톨로지")}
      {groups.map((g) => (
        <div key={g.key}>
          <div className="group">{g.label}</div>
          {g.roles.map((p) => item(p.id, p.name))}
        </div>
      ))}
    </nav>
  );
}
