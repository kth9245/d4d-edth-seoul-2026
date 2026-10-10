import { useEffect, useMemo, useState } from "react";
import type { Play } from "../../contracts.gen";
import type { SaveResult } from "./checkView";
import { forSave } from "./draftRequests";
import { groupPlays } from "./groupPlays";
import { zoneCentre } from "./editStep";
import { enemyRows } from "./enemyRows";
import { insertReportStep } from "./insertReportStep";
import { type EditorData, loadEditorData } from "./loadEditorData";
import { NewPlayMenu } from "./NewPlayMenu";
import { OntologyPanel } from "./OntologyPanel";
import { OperationOverview } from "./OperationOverview";
import { ONTOLOGY, OVERVIEW, PlaySidebar } from "./PlaySidebar";
import { playUsage } from "./playUsage";
import { PlayWorkflow } from "./PlayWorkflow";
import { savePlay } from "./savePlay";
import { vehicleColumns } from "./vehicleColumns";
import { backFrom, openView, type ViewHistory } from "./viewHistory";

export function EditorScreen() {
  const [data, setData] = useState<EditorData | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  // Which view is open and the ones opened before it, so "뒤로" returns along the same path (sidebar, play links).
  const [nav, setNav] = useState<ViewHistory>({ current: OVERVIEW, stack: [] });
  const selected = nav.current;
  const open = (id: string) => setNav((h) => openView(h, id));
  const back = () => setNav((h) => backFrom(h, OVERVIEW));
  const [results, setResults] = useState<Record<string, SaveResult>>({});
  // Part3-12: plays changed on screen but not saved yet, and the step each change added (to highlight it).
  const [edits, setEdits] = useState<Record<string, Play>>({});
  const [fresh, setFresh] = useState<Record<string, string>>({});
  useEffect(() => {
    loadEditorData().then(setData, (e: Error) => setLoadError(e.message));
  }, []);
  const view = useMemo(
    () =>
      data && {
        groups: groupPlays(data.plays, data.enemies.map((e) => e.play_id)),
        usage: playUsage(data.operation, data.plays, data.enemies),
        columns: vehicleColumns(data.operation, data.plays),
        enemies: enemyRows(data.enemies, data.operation.started_ms, data.plays),
        byId: new Map(data.plays.map((p) => [p.id, p])),
      },
    [data],
  );
  if (loadError) return <div className="editor load-error">서버에 연결하지 못했습니다 ({loadError}). scripts/dev.sh로 gateway(8000)를 띄운 뒤 새로고침하세요.</div>;
  if (!data || !view) return <div className="editor">불러오는 중…</div>;
  const playName = (id: string) => view.byId.get(id)?.name ?? null;
  const prev = nav.stack[nav.stack.length - 1] ?? OVERVIEW;
  const backLabel = prev === OVERVIEW ? "작전 개요" : (playName(prev) ?? prev);
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
  // A card edited on the panel (Part3-12.1): the play becomes unsaved, its old check result goes.
  const editPlay = (p: Play, next: Play, added?: string) => {
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
    open(p.id);
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
      <PlaySidebar groups={view.groups} selected={play ? play.id : selected === ONTOLOGY ? ONTOLOGY : OVERVIEW} showOverview onSelect={open}
        top={<NewPlayMenu existingIds={data.plays.map((p) => p.id)} onCreated={created} />} />
      <main className="editor-main">
        {play ? (
          <PlayWorkflow
            key={play.id}
            play={play}
            usage={view.usage[play.id] ?? []}
            playName={playName}
            onOpen={open}
            onBack={back}
            backLabel={backLabel}
            result={results[play.id]}
            onSave={() => save(play)}
            edited={!!edits[play.id]}
            freshStep={fresh[play.id]}
            onInsertReport={(stepId) => insertReport(play, stepId)}
            onEdit={(next, added) => editPlay(play, next, added)}
            vehicleIds={data.operation.vehicle_ids}
            fallbackPoint={zoneCentre(data.operation.zone)}
            plays={data.plays.map((p) => ({ id: p.id, name: p.name }))}
          />
        ) : selected === ONTOLOGY ? (
          <OntologyPanel op={data.operation} plays={data.plays} vehicles={data.vehicles} />
        ) : (
          <OperationOverview op={data.operation} vehicles={data.vehicles} columns={view.columns} enemies={view.enemies} playName={playName} onOpen={open} />
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
