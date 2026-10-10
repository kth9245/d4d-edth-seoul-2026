import { useEffect, useMemo, useState } from "react";
import type { Role, ScenarioInfo } from "../../contracts.gen";
import { fetchScenarios } from "../live/fetchScenarios";
import { postRun } from "../run/runApi";
import { activateScenario } from "./activateScenario";
import { deleteRole } from "./deleteRole";
import type { SaveResult } from "./checkView";
import { forSave } from "./draftRequests";
import { groupRoles } from "./groupRoles";
import { zoneCentre } from "./editStep";
import { enemyRows } from "./enemyRows";
import { insertReportStep } from "./insertReportStep";
import { type EditorData, loadEditorData } from "./loadEditorData";
import { createOperation } from "./createOperation";
import { NewOperationMenu } from "./NewOperationMenu";
import { NewRoleMenu } from "./NewRoleMenu";
import { postOperation } from "./postOperation";
import { setStartRole } from "./setStartRole";
import { startRoleOptions } from "./startRoleOptions";
import { OntologyPanel } from "./OntologyPanel";
import { OperationOverview } from "./OperationOverview";
import { ONTOLOGY, OVERVIEW, RoleSidebar } from "./RoleSidebar";
import { roleUsage } from "./roleUsage";
import { RoleWorkflow } from "./RoleWorkflow";
import { saveRole } from "./saveRole";
import { vehicleColumns } from "./vehicleColumns";

export function EditorScreen() {
  const [data, setData] = useState<EditorData | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  // The open view: the overview, the ontology or a role. "← 작전 개요" on a role always goes home (Part1-33),
  // not back along the roles opened before it.
  const [selected, setSelected] = useState<string>(OVERVIEW);
  const open = (id: string) => setSelected(id);
  const home = () => setSelected(OVERVIEW);
  const [results, setResults] = useState<Record<string, SaveResult>>({});
  // Part3-12: roles changed on screen but not saved yet, and the step each change added (to highlight it).
  const [edits, setEdits] = useState<Record<string, Role>>({});
  const [fresh, setFresh] = useState<Record<string, string>>({});
  // Decision 0042: the operations to pick, and why a pick or "시뮬레이션" failed.
  const [scenarios, setScenarios] = useState<ScenarioInfo[]>([]);
  const [opError, setOpError] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<{ id: string; message: string } | null>(null);
  // Roles the server has (loaded or saved since): a new role only on screen is deleted without asking it.
  const [onServer, setOnServer] = useState<Set<string>>(new Set());
  const loaded = (d: EditorData) => {
    setData(d);
    setOnServer(new Set(d.roles.map((p) => p.id)));
  };
  useEffect(() => {
    loadEditorData().then(loaded, (e: Error) => setLoadError(e.message));
    fetchScenarios().then(setScenarios);
  }, []);
  const view = useMemo(
    () =>
      data && {
        groups: groupRoles(data.roles, data.enemies.map((e) => e.role_id)),
        usage: roleUsage(data.operation, data.roles, data.enemies),
        columns: vehicleColumns(data.operation, data.roles),
        enemies: enemyRows(data.enemies, data.operation.started_ms, data.roles),
        byId: new Map(data.roles.map((p) => [p.id, p])),
      },
    [data],
  );
  if (loadError) return <div className="editor load-error">서버에 연결하지 못했습니다 ({loadError}). scripts/dev.sh로 gateway(8000)를 띄운 뒤 새로고침하세요.</div>;
  if (!data || !view) return <div className="editor">불러오는 중…</div>;
  const roleName = (id: string) => view.byId.get(id)?.name ?? null;
  const role = edits[selected] ?? view.byId.get(selected);
  // Results are kept per role id so they survive switching roles. An edit drops the old result (its issues
  // no longer match the cards); a save that passes puts the edited role into the list.
  const insertReport = (p: Role, stepId: string) => {
    const next = insertReportStep(p, stepId);
    const added = next.steps.find((s) => !p.steps.some((o) => o.id === s.id))?.id;
    setEdits((all) => ({ ...all, [p.id]: next }));
    if (added) setFresh((all) => ({ ...all, [p.id]: added }));
    setResults((all) => without(all, p.id));
  };
  // A card edited on the panel (Part3-12.1): the role becomes unsaved, its old check result goes.
  const editRole = (p: Role, next: Role, added?: string) => {
    setEdits((all) => ({ ...all, [p.id]: next }));
    if (added) setFresh((all) => ({ ...all, [p.id]: added }));
    setResults((all) => without(all, p.id));
  };
  // A new role (AI draft or written by hand) arrives unsaved in the list (or replaces one with the same id) and opens.
  const created = (p: Role) => {
    setData((d) => d && { ...d, roles: d.roles.some((x) => x.id === p.id) ? d.roles.map((x) => (x.id === p.id ? p : x)) : [...d.roles, p] });
    setEdits((all) => ({ ...all, [p.id]: p }));
    setFresh((all) => without(all, p.id));
    setResults((all) => without(all, p.id));
    open(p.id);
  };
  const save = (edited: Role) => {
    const p = forSave(edited);
    const put = (r: SaveResult) => setResults((all) => ({ ...all, [p.id]: r }));
    put({ state: "saving" });
    saveRole(p).then(
      (check) => {
        put({ state: "done", check });
        if (check.ok) setOnServer((ids) => new Set(ids).add(p.id));
        if (!check.ok || !edits[p.id]) return;
        setData((d) => d && { ...d, roles: d.roles.map((x) => (x.id === p.id ? p : x)) });
        setEdits((all) => without(all, p.id));
      },
      (e) => {
        console.warn("editor: save failed", e);
        put({ state: "error", message: String(e) });
      },
    );
  };
  // "삭제" (decision 0050): the server drops the role from the running operation and resets the run (a 404 is a
  // new role that was only on screen). The editor drops it the same way, also from the start assignments, and
  // goes home.
  const remove = (id: string) => {
    setDeleteError(null);
    (onServer.has(id) ? deleteRole(id) : Promise.resolve(false)).then(
      () => {
        setData((d) => d && {
          ...d,
          roles: d.roles.filter((x) => x.id !== id),
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
  const pickScenario = (id: string) => switchTo(activateScenario(id));
  // "＋ 작전 새로 만들기" (decision 0053): the new empty operation runs and its overview opens like a picked one.
  const newOperation = (name: string, purpose: string) => switchTo(createOperation(name, purpose));
  const switchTo = (started: Promise<unknown>) => {
    setOpError(null);
    started
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
  // The overview's start role per vehicle (decision 0053): the server's operation changes and the run resets.
  const startOptions = (vehicleId: string) => {
    const v = data?.vehicles.find((x) => x.id === vehicleId);
    return v && data ? startRoleOptions(data.roles, v, data.enemies.map((e) => e.role_id)) : [];
  };
  const startRole = (vehicleId: string, roleId: string | null) => {
    if (!data) return;
    setOpError(null);
    postOperation(setStartRole(data.operation, vehicleId, roleId)).then(
      (op) => setData((d) => d && { ...d, operation: op }),
      (e) => {
        console.warn("editor: start role failed", e);
        setOpError(`시작 Role을 바꾸지 못했습니다 (${String(e)})`);
      },
    );
  };
  // "▶ 시뮬레이션": the run goes back to the operation's start, paused, and the live tab opens (no auto start).
  const simulate = () => {
    setOpError(null);
    postRun("/run/reset").then((r) => {
      if (r.ok) location.hash = "#live";
      else setOpError(`시뮬레이션을 열지 못했습니다 (${r.error})`);
    });
  };
  return (
    <div className="editor">
      <RoleSidebar groups={view.groups} selected={role ? role.id : selected === ONTOLOGY ? ONTOLOGY : OVERVIEW} showOverview onSelect={open}
        top={<><NewOperationMenu onCreate={newOperation} /><NewRoleMenu existingIds={data.roles.map((p) => p.id)} onCreated={created} /></>}
        scenarios={scenarios} onPickScenario={pickScenario} />
      <main className="editor-main">
        {opError && <div className="issue">⚠ {opError}</div>}
        {role ? (
          <RoleWorkflow
            key={role.id}
            role={role}
            usage={view.usage[role.id] ?? []}
            roleName={roleName}
            onOpen={open}
            onHome={home}
            onDelete={() => remove(role.id)}
            deleteError={deleteError?.id === role.id ? deleteError.message : null}
            result={results[role.id]}
            onSave={() => save(role)}
            edited={!!edits[role.id]}
            freshStep={fresh[role.id]}
            onInsertReport={(stepId) => insertReport(role, stepId)}
            onEdit={(next, added) => editRole(role, next, added)}
            vehicleIds={data.operation.vehicle_ids}
            fallbackPoint={zoneCentre(data.operation.zone)}
            roles={data.roles.map((p) => ({ id: p.id, name: p.name }))}
            routes={data.routes}
            enemy={data.enemies.some((e) => e.role_id === role.id)}
          />
        ) : selected === ONTOLOGY ? (
          <OntologyPanel op={data.operation} roles={data.roles} vehicles={data.vehicles} />
        ) : (
          <OperationOverview op={data.operation} vehicles={data.vehicles} columns={view.columns} enemies={view.enemies} roleName={roleName} onOpen={open} onSimulate={simulate}
            startOptions={startOptions} onStartRole={startRole} />
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
