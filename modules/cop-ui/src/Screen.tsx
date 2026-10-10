import { useEffect, useState } from "react";
import type { Frame, Polygon } from "./contracts.gen";
import { CardList } from "./features/cards/CardList";
import { tilesExist } from "./features/map/basemap";
import { MapView } from "./features/map/MapView";

// Map on the left, side column on the right (cards come in Part1-10).
export function Screen({ frame, zone, status, ok }:
  { frame: Frame | null; zone: Polygon | null; status: string; ok: boolean }) {
  const [tiles, setTiles] = useState<boolean | null>(null);
  useEffect(() => {
    tilesExist().then(setTiles);
  }, []);
  return (
    <div className="layout">
      {tiles === null ? <div className="map" /> : <MapView frame={frame} zone={zone} tilesAvailable={tiles} />}
      <aside>
        <div className={ok ? "status ok" : "status down"}>{status}</div>
        <CardList frame={frame} />
      </aside>
    </div>
  );
}
