import { useEffect, useMemo, useState } from "react";
import { groupPlays } from "./groupPlays";
import { type EditorData, loadEditorData } from "./loadEditorData";
import { OperationOverview } from "./OperationOverview";
import { OVERVIEW, PlaySidebar } from "./PlaySidebar";
import { playUsage } from "./playUsage";
import { PlayWorkflow } from "./PlayWorkflow";
import { vehicleColumns } from "./vehicleColumns";

export function EditorScreen() {
  const [data, setData] = useState<EditorData | null>(null);
  const [selected, setSelected] = useState<string>(OVERVIEW);
  useEffect(() => {
    loadEditorData().then(setData);
  }, []);
  const view = useMemo(
    () =>
      data && {
        groups: groupPlays(data.plays),
        usage: playUsage(data.operation, data.plays),
        columns: vehicleColumns(data.operation, data.plays),
        byId: new Map(data.plays.map((p) => [p.id, p])),
      },
    [data],
  );
  if (!data || !view) return <div className="editor">불러오는 중…</div>;
  const playName = (id: string) => view.byId.get(id)?.name ?? null;
  const play = view.byId.get(selected);
  return (
    <div className="editor">
      <PlaySidebar groups={view.groups} selected={play ? play.id : OVERVIEW} source={data.source} showOverview onSelect={setSelected} />
      <main className="editor-main">
        {play ? (
          <PlayWorkflow play={play} usage={view.usage[play.id] ?? []} playName={playName} onOpen={setSelected} />
        ) : (
          <OperationOverview op={data.operation} columns={view.columns} playName={playName} onOpen={setSelected} />
        )}
      </main>
    </div>
  );
}
