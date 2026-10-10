import { useEffect, useMemo, useState } from "react";
import type { Play } from "../../contracts.gen";
import type { SaveResult } from "./checkView";
import { forSave } from "./draftRequests";
import { groupPlays } from "./groupPlays";
import { insertReportStep } from "./insertReportStep";
import { type EditorData, loadEditorData } from "./loadEditorData";
import { NewPlayMenu } from "./NewPlayMenu";
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
  // Part3-12: plays changed on screen but not saved yet, and the step each change added (to highlight it).
  const [edits, setEdits] = useState<Record<string, Play>>({});
  const [fresh, setFresh] = useState<Record<string, string>>({});
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
  const play = edits[selected] ?? view.byId.get(selected);
  // Results are kept per play id so they survive switching plays. An edit drops the old result (its issues
  // no longer match the cards); a save that passes puts the edited play into the list.
  const insertReport = (p: Play, stepId: string) => {
    const next = insertReportStep(p, stepId);
    const added = next.steps.find((s) => !p.steps.some((o) => o.id === s.id))?.id;
    setEdits((all) => ({ ...all, [p.id]: next }));
    if (added) setFresh((all) => ({ ...all, [p.id]: added }));
    setResults((all) => without(all, p.id));
  };
  // A new play (AI draft or written by hand) arrives unsaved in the list (or replaces one with the same id) and opens.
  const created = (p: Play) => {
    setData((d) => d && { ...d, plays: d.plays.some((x) => x.id === p.id) ? d.plays.map((x) => (x.id === p.id ? p : x)) : [...d.plays, p] });
    setEdits((all) => ({ ...all, [p.id]: p }));
    setFresh((all) => without(all, p.id));
    setResults((all) => without(all, p.id));
    setSelected(p.id);
  };
  const save = (edited: Play) => {
    const p = forSave(edited);
    const put = (r: SaveResult) => setResults((all) => ({ ...all, [p.id]: r }));
    put({ state: "saving" });
    savePlay(p).then(
      (check) => {
        put({ state: "done", check });
        if (!check.ok || !edits[p.id]) return;
        setData((d) => d && { ...d, plays: d.plays.map((x) => (x.id === p.id ? p : x)) });
        setEdits((all) => without(all, p.id));
      },
      (e) => {
        console.warn("editor: save failed", e);
        put({ state: "error", message: String(e) });
      },
    );
  };
  return (
    <div className="editor">
      <PlaySidebar groups={view.groups} selected={play ? play.id : OVERVIEW} source={data.source} showOverview onSelect={setSelected}
        top={<NewPlayMenu existingIds={data.plays.map((p) => p.id)} onCreated={created} />} />
      <main className="editor-main">
        {play ? (
          <PlayWorkflow
            play={play}
            usage={view.usage[play.id] ?? []}
            playName={playName}
            onOpen={setSelected}
            result={results[play.id]}
            onSave={() => save(play)}
            edited={!!edits[play.id]}
            freshStep={fresh[play.id]}
            onInsertReport={(stepId) => insertReport(play, stepId)}
          />
        ) : (
          <OperationOverview op={data.operation} columns={view.columns} playName={playName} onOpen={setSelected} />
        )}
      </main>
    </div>
  );
}

function without<T>(all: Record<string, T>, key: string): Record<string, T> {
  const out = { ...all };
  delete out[key];
  return out;
}
