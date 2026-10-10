import type { ReactNode } from "react";
import type { PlayGroup } from "./groupPlays";

export const OVERVIEW = "__overview__";
export const ONTOLOGY = "__ontology__"; // decision 0038

type Props = {
  groups: PlayGroup[];
  selected: string;
  showOverview: boolean;
  onSelect: (id: string) => void;
  top?: ReactNode; // above the list: the AI draft box (Part3-13)
};

export function PlaySidebar({ groups, selected, showOverview, onSelect, top }: Props) {
  const item = (id: string, label: string) => (
    <button key={id} className={selected === id ? "item on" : "item"} onClick={() => onSelect(id)}>
      {label}
    </button>
  );
  return (
    <nav className="play-sidebar">
      {top}
      {showOverview && item(OVERVIEW, "작전 개요")}
      {showOverview && item(ONTOLOGY, "온톨로지")}
      {groups.map((g) => (
        <div key={g.key}>
          <div className="group">{g.label}</div>
          {g.plays.map((p) => item(p.id, p.name))}
        </div>
      ))}
    </nav>
  );
}
