import type { EditorData } from "./loadEditorData";
import type { PlayGroup } from "./groupPlays";

export const OVERVIEW = "__overview__";

type Props = {
  groups: PlayGroup[];
  selected: string;
  source: EditorData["source"];
  showOverview: boolean;
  onSelect: (id: string) => void;
};

export function PlaySidebar({ groups, selected, source, showOverview, onSelect }: Props) {
  const item = (id: string, label: string) => (
    <button key={id} className={selected === id ? "item on" : "item"} onClick={() => onSelect(id)}>
      {label}
    </button>
  );
  return (
    <nav className="play-sidebar">
      {source === "example" && <div className="example-badge">예시 데이터(서버 없음)</div>}
      {showOverview && item(OVERVIEW, "작전 개요")}
      {groups.map((g) => (
        <div key={g.key}>
          <div className="group">{g.label}</div>
          {g.plays.map((p) => item(p.id, p.name))}
        </div>
      ))}
    </nav>
  );
}
