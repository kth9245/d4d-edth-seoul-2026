import { useEffect, useMemo, useState } from "react";
import type { Play, ScenarioInfo } from "../../contracts.gen";
import { fetchScenarios } from "../live/fetchScenarios";
import { postRun } from "../run/runApi";
import { activateScenario } from "./activateScenario";
import { deletePlay } from "./deletePlay";
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

export function EditorScreen() {
  const [data, setData] = useState<EditorData | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  // The open view: the overview, the ontology or a play. "← 작전 개요" on a play always goes home (Part1-33),
  // not back along the plays opened before it.
  const [selected, setSelected] = useState<string>(OVERVIEW);
  const open = (id: string) => setSelected(id);
  const home = () => setSelected(OVERVIEW);
  const [results, setResults] = useState<Record<string, SaveResult>>({});
  // Part3-12: plays changed on screen but not saved yet, and the step each change added (to highlight it).
  const [edits, setEdits] = useState<Record<string, Play>>({});
  const [fresh, setFresh] = useState<Record<string, string>>({});
  // Decision 0042: the operations to pick, and why a pick or "시뮬레이션" failed.
  const [scenarios, setScenarios] = useState<ScenarioInfo[]>([]);
  const [opError, setOpError] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<{ id: string; message: string } | null>(null);
  // Plays the server has (loaded or saved since): a new play only on screen is deleted without asking it.
  const [onServer, setOnServer] = useState<Set<string>>(new Set());
  const loaded = (d: EditorData) => {
    setData(d);
    setOnServer(new Set(d.plays.map((p) => p.id)));
  };
  useEffect(() => {
    loadEditorData().then(loaded, (e: Error) => setLoadError(e.message));
    fetchScenarios().then(setScenarios);
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
        if (check.ok) setOnServer((ids) => new Set(ids).add(p.id));
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
  // "삭제" (decision 0050): the server drops the play from the running operation and resets the run (a 404 is a
  // new play that was only on screen). The editor drops it the same way, also from the start assignments, and
  // goes home.
  const remove = (id: string) => {
    setDeleteError(null);
    (onServer.has(id) ? deletePlay(id) : Promise.resolve(false)).then(
      () => {
        setData((d) => d && {
          ...d,
          plays: d.plays.filter((x) => x.id !== id),
          operation: { ...d.operation, assign: Object.fromEntries(Object.entries(d.operation.assign ?? {}).filter(([, p]) => p !== id)) },
        });
        setEdits((all) => without(all, id));
        setResults((all) => without(all, id));
        setFresh((all) => without(all, id));
        setSelected(OVERVIEW);
      },
      (e) => {
        console.warn("editor: delete failed", e);
        setDeleteError({ id, message: `삭제하지 못했습니다 (${String(e)})` });
      },
    );
  };
  // Picking another operation makes it the gateway's running one, paused at its start; the editor reads it
  // again and drops what belonged to the old one (unsaved edits, check results, view history).
  const pickScenario = (id: string) => {
    setOpError(null);
    activateScenario(id)
      .then(() => Promise.all([loadEditorData(), fetchScenarios()]))
      .then(
        ([d, list]) => {
          loaded(d);
          setScenarios(list);
          setEdits({});
          setResults({});
          setFresh({});
          setSelected(OVERVIEW);
        },
        (e) => {
          console.warn("editor: operation switch failed", e);
          setOpError(`작전을 바꾸지 못했습니다 (${String(e)})`);
        },
      );
  };
  // "▶ 시뮬레이션": the run goes back to the operation's start, paused, and the live tab opens (no auto play).
  const simulate = () => {
    setOpError(null);
    postRun("/run/reset").then((r) => {
      if (r.ok) location.hash = "#live";
      else setOpError(`시뮬레이션을 열지 못했습니다 (${r.error})`);
    });
  };
  return (
    <div className="editor">
      <PlaySidebar groups={view.groups} selected={play ? play.id : selected === ONTOLOGY ? ONTOLOGY : OVERVIEW} showOverview onSelect={open}
        top={<NewPlayMenu existingIds={data.plays.map((p) => p.id)} onCreated={created} />}
        scenarios={scenarios} onPickScenario={pickScenario} />
      <main className="editor-main">
        {opError && <div className="issue">⚠ {opError}</div>}
        {play ? (
          <PlayWorkflow
            key={play.id}
            play={play}
            usage={view.usage[play.id] ?? []}
            playName={playName}
            onOpen={open}
            onHome={home}
            onDelete={() => remove(play.id)}
            deleteError={deleteError?.id === play.id ? deleteError.message : null}
            result={results[play.id]}
            onSave={() => save(play)}
            edited={!!edits[play.id]}
            freshStep={fresh[play.id]}
            onInsertReport={(stepId) => insertReport(play, stepId)}
            onEdit={(next, added) => editPlay(play, next, added)}
            vehicleIds={data.operation.vehicle_ids}
            fallbackPoint={zoneCentre(data.operation.zone)}
            plays={data.plays.map((p) => ({ id: p.id, name: p.name }))}
            routes={data.routes}
            enemy={data.enemies.some((e) => e.play_id === play.id)}
          />
        ) : selected === ONTOLOGY ? (
          <OntologyPanel op={data.operation} plays={data.plays} vehicles={data.vehicles} />
        ) : (
          <OperationOverview op={data.operation} vehicles={data.vehicles} columns={view.columns} enemies={view.enemies} playName={playName} onOpen={open} onSimulate={simulate} />
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
