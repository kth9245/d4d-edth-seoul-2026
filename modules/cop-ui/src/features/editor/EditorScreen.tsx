import { useEffect, useMemo, useState } from "react";
import { groupPlays } from "./groupPlays";
import { type EditorData, loadEditorData } from "./loadEditorData";
import { PlaySidebar } from "./PlaySidebar";
import { playUsage } from "./playUsage";
import { PlayWorkflow } from "./PlayWorkflow";

export function EditorScreen() {
  const [data, setData] = useState<EditorData | null>(null);
  const [selected, setSelected] = useState<string>("");
  useEffect(() => {
    loadEditorData().then(setData);
  }, []);
  const view = useMemo(
    () =>
      data && {
        groups: groupPlays(data.plays),
        usage: playUsage(data.operation, data.plays),
        byId: new Map(data.plays.map((p) => [p.id, p])),
      },
    [data],
  );
  if (!data || !view) return <div className="editor">불러오는 중…</div>;
  const playName = (id: string) => view.byId.get(id)?.name ?? null;
  const play = view.byId.get(selected) ?? view.groups[0]?.plays[0]; // first play in the sidebar, not data.plays[0] (standby)
  return (
    <div className="editor">
      <PlaySidebar groups={view.groups} selected={play?.id ?? ""} source={data.source} showOverview={false} onSelect={setSelected} />
      <main className="editor-main">
        {play ? (
          <PlayWorkflow play={play} usage={view.usage[play.id] ?? []} playName={playName} onOpen={setSelected} />
        ) : (
          "플레이 없음"
        )}
      </main>
    </div>
  );
}
