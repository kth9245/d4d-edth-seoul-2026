import { useEffect, useState } from "react";
import type { Frame, Polygon } from "./contracts.gen";
import { CardList } from "./features/cards/CardList";
import { SwitchPanel } from "./features/cards/SwitchPanel";
import { tilesExist } from "./features/map/basemap";
import { MapView } from "./features/map/MapView";
import { useDirectControl } from "./features/map/useDirectControl";
import { MetricsPanel } from "./features/run/MetricsPanel";
import { RunBar } from "./features/run/RunBar";

// Map with the run bar under it on the left; status, metrics, switch requests and cards in the side column.
export function Screen({ frame, zone, status, ok }:
  { frame: Frame | null; zone: Polygon | null; status: string; ok: boolean }) {
  const [tiles, setTiles] = useState<boolean | null>(null);
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
      </div>
      <aside>
        <div className={ok ? "status ok" : "status down"}>{status}</div>
        <MetricsPanel metrics={frame?.metrics ?? null} />
        <SwitchPanel frame={frame} />
        <CardList frame={frame} />
      </aside>
    </div>
  );
}
