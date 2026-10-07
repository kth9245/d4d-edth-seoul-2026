import { useEffect, useState } from "react";
import { AlertList } from "./features/alerts/AlertList";
import { useFrames } from "./features/live/useFrames";
import { tilesExist } from "./features/map/basemap";
import { MapView } from "./features/map/MapView";

const WS_URL = `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`;
const CENTER: [number, number] = [126.978, 37.5665];

export default function App() {
  const { frame, connected } = useFrames(WS_URL);
  const [tiles, setTiles] = useState<boolean | null>(null);
  useEffect(() => {
    tilesExist().then(setTiles);
  }, []);
  return (
    <div className="layout">
      {tiles !== null && <MapView frame={frame} center={CENTER} tilesAvailable={tiles} />}
      <aside>
        <div className={connected ? "status ok" : "status down"}>{connected ? "LIVE" : "연결 끊김"}</div>
        <AlertList frame={frame} />
      </aside>
    </div>
  );
}
