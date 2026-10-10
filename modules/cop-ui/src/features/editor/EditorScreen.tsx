import { useEffect, useMemo, useState } from "react";
import type { Play } from "../../contracts.gen";
import type { SaveResult } from "./checkView";
import { groupPlays } from "./groupPlays";
import { type EditorData, loadEditorData } from "./loadEditorData";
import { OperationOverview } from "./OperationOverview";
import { OVERVIEW, PlaySidebar } from "./PlaySidebar";
import { playUsage } from "./playUsage";
import { PlayWorkflow } from "./PlayWorkflow";
import { savePlay } from "./savePlay";
import { vehicleColumns } from "./vehicleColumns";

export function EditorScreen() {
  const [data, setData] = useState<EditorData | null>(null);
  const [selected, setSelected] = useState<string>(OVERVIEW);
  const [results, setResults] = useState<Record<string, SaveResult>>({});
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
  // Results are kept per play id so they survive switching plays. Cards are read-only until Part3-12,
  // so the saved play is the one already in `data.plays`.
  const save = (p: Play) => {
    const put = (r: SaveResult) => setResults((all) => ({ ...all, [p.id]: r }));
    put({ state: "saving" });
    savePlay(p).then(
      (check) => put({ state: "done", check }),
      (e) => {
        console.warn("editor: save failed", e);
        put({ state: "error", message: String(e) });
      },
    );
  };
  return (
    <div className="editor">
      <PlaySidebar groups={view.groups} selected={play ? play.id : OVERVIEW} source={data.source} showOverview onSelect={setSelected} />
      <main className="editor-main">
        {play ? (
          <PlayWorkflow
            play={play}
            usage={view.usage[play.id] ?? []}
            playName={playName}
            onOpen={setSelected}
            result={results[play.id]}
            onSave={() => save(play)}
          />
        ) : (
          <OperationOverview op={data.operation} columns={view.columns} playName={playName} onOpen={setSelected} />
        )}
      </main>
    </div>
  );
}
