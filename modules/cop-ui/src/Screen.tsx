import { useEffect, useState } from "react";
import type { Frame, Polygon } from "./contracts.gen";
import { CardList } from "./features/cards/CardList";
import { SwitchPanel } from "./features/cards/SwitchPanel";
import { ObjectGraphView } from "./features/graph/ObjectGraphView";
import { tilesExist } from "./features/map/basemap";
import { MapView } from "./features/map/MapView";
import { useDirectControl } from "./features/map/useDirectControl";
import { MetricsPanel } from "./features/run/MetricsPanel";
import { RunBar } from "./features/run/RunBar";

// Map with the run bar under it on the left; status, metrics, switch requests and cards in the side column.
// A card's "연결 보기" opens its target's object graph over the map column (decision 0038).
export function Screen({ frame, zone, status, ok }:
  { frame: Frame | null; zone: Polygon | null; status: string; ok: boolean }) {
  const [tiles, setTiles] = useState<boolean | null>(null);
  const [graph, setGraph] = useState<string | null>(null);
  const direct = useDirectControl(frame?.t_ms ?? 0);
  useEffect(() => {
    tilesExist().then(setTiles);
  }, []);
  return (
    <div className="layout">
      <div className="map-col">
        {tiles === null ? <div className="map" /> : <MapView frame={frame} zone={zone} tilesAvailable={tiles} direct={direct} />}
        {direct.hint && <div className={direct.selected ? "direct-hint on" : "direct-hint"}>{direct.hint}</div>}
        <RunBar frame={frame} />
        {graph && <ObjectGraphView focus={graph} onClose={() => setGraph(null)} />}
      </div>
      <aside>
        <div className={ok ? "status ok" : "status down"}>{status}</div>
        <MetricsPanel metrics={frame?.metrics ?? null} />
        <SwitchPanel frame={frame} />
        <CardList frame={frame} onGraph={setGraph} />
      </aside>
    </div>
  );
}
