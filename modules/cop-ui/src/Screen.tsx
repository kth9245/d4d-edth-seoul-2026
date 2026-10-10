import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import type { Frame, Polygon } from "./contracts.gen";
import { boardView } from "./features/board/boardView";
import { DecisionQueue } from "./features/board/DecisionQueue";
import { LoadBar } from "./features/board/LoadBar";
import { PointMenu } from "./features/board/PointMenu";
import { pointRoles } from "./features/board/pointRoles";
import { RosterPanel } from "./features/board/RosterPanel";
import { seenTargets } from "./features/board/seenTargets";
import { SituationBar } from "./features/board/SituationBar";
import { useBoardData } from "./features/board/useBoardData";
import { VehicleMenu } from "./features/board/VehicleMenu";
import { vehicleMenuRoles } from "./features/board/vehicleMenuRoles";
import "./features/board/board.css";
import "./features/cards/cards.css";
import { postSwitch } from "./features/cards/injectionRequests";
import { ObjectGraphView } from "./features/graph/ObjectGraphView";
import { tilesExist } from "./features/map/basemap";
import { MapView } from "./features/map/MapView";
import { MavlinkButton, MavlinkPanel } from "./features/mavlink/MavlinkLog";
import { useDirectControl } from "./features/map/useDirectControl";
import { RunBar } from "./features/run/RunBar";

// Live board (Part1-32): header line (stage counts, operator load, link status) in the app header, our vehicles
// (a picked one opens its menu under its row, Part1-32.1) and the targets on the left with the operation's switch
// buttons in its head, the map with the run bar in the middle, the decision queue on the right with the history
// folded under it. A card's "연결 보기" opens its target's graph over the map.
export function Screen({ frame, zone, status, ok }:
  { frame: Frame | null; zone: Polygon | null; status: string; ok: boolean }) {
  const [tiles, setTiles] = useState<boolean | null>(null);
  const [graph, setGraph] = useState<string | null>(null);
  const [slot, setSlot] = useState<HTMLElement | null>(null);
  const [mavlink, setMavlink] = useState(false); // decision 0065: the MAVLink log panel
  const data = useBoardData(frame !== null);
  const direct = useDirectControl(frame?.t_ms ?? 0);
  const board = useMemo(() => (frame ? boardView(frame, data) : null), [frame, data]);
  const [switchNote, setSwitchNote] = useState<string | null>(null);
  const live = frame?.vehicles.find((x) => x.id === direct.selected) ?? null;
  const spec = data.vehicles.find((x) => x.id === direct.selected);
  const current = data.roles.find((r) => r.id === live?.role_id)?.name ?? "대기";
  const menuRoles = spec ? vehicleMenuRoles(data.roles, spec, data.enemyRoles, live?.role_id ?? null) : { plain: [], target: [] };
  const menu = frame && board && live ? (
    <VehicleMenu key={live.id} current={current} plain={menuRoles.plain} target={menuRoles.target}
      seen={seenTargets(frame.targets, board.tracks, live.pos)} onRole={direct.onRole} onPoint={direct.onPointTarget} />
  ) : null;
  const onSwitch = async (id: string) => {
    const r = await postSwitch({ switch_id: id });
    setSwitchNote(r.ok ? `요청됨 ${r.id} · 결정 대기에서 승인` : `요청 실패: ${r.error}`);
  };
  useEffect(() => {
    tilesExist().then(setTiles);
    setSlot(document.getElementById("header-slot"));
  }, []);
  return (
    <div className="layout board">
      {slot && createPortal(
        <>
          {board && <SituationBar situation={board.situation} />}
          <LoadBar metrics={frame?.metrics ?? null} />
          <MavlinkButton onClick={() => setMavlink((v) => !v)} />
          <div className={ok ? "status ok" : "status down"}>{status}</div>
        </>, slot)}
      {frame && board ? (
        <RosterPanel rows={board.rows} targets={frame.targets} stages={board.stages} selected={direct.selected}
          onVehicle={direct.onVehicleClick} onTarget={(id) => direct.selected && direct.onTargetClick(id, 220, 120)}
          menu={menu} switches={data.switches} onSwitch={onSwitch} switchNote={switchNote} />
      ) : <aside className="roster" />}
      <div className="map-col">
        {tiles === null ? <div className="map" /> : <MapView frame={frame} zone={zone} tilesAvailable={tiles} direct={direct} board={board} watch={data.watch} specs={data.vehicles} />}
        {direct.hint && <div className={direct.selected ? "direct-hint on" : "direct-hint"}>{direct.hint}</div>}
        {frame && direct.selected && direct.pick && (
          // Pointing (decisions 0048, 0049, 0058): the selected vehicle's target roles beside the pointed target.
          <PointMenu vehicle={direct.selected} target={direct.pick.target} x={direct.pick.x} y={direct.pick.y}
            roles={pointRoles(menuRoles.target, board?.tracks[direct.pick.target])} current={current}
            onPick={direct.onPoint} onCancel={direct.cancelPick} />
        )}
        <RunBar frame={frame} />
        {graph && <ObjectGraphView focus={graph} onClose={() => setGraph(null)} />}
        {mavlink && <MavlinkPanel onClose={() => setMavlink(false)} />}
      </div>
      <aside className="ops">
        <div className="ops-scroll">
          {frame && board ? <DecisionQueue frame={frame} queue={board.queue} onGraph={setGraph} />
            : <div className="next-act"><div className="t">게이트웨이 연결 대기</div></div>}
        </div>
        <div className="folds">
          <details className="fold hist"><summary>지난 기록 <b>{board?.queue.history.length ?? 0}</b></summary>
            {board?.queue.history.map((c) => (
              <div key={`${c.source}-${c.id}`} className="hist-row"><time>{c.time}</time><span>{c.text}{c.done ? ` · ${c.done}` : ""}</span>
                {c.target && (c.kind === "target_detected" || c.kind === "target_neutralized") &&
                  <button className="graph-open" onClick={() => setGraph(c.target!)}>연결 보기</button>}</div>
            ))}
          </details>
        </div>
      </aside>
    </div>
  );
}
