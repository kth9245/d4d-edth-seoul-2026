import { lazy, Suspense, useEffect, useState } from "react";
import type { Polygon } from "./contracts.gen";
import { fetchZone } from "./features/live/fetchZone";
import { useFrames } from "./features/live/useFrames";
import { Screen } from "./Screen";

const WS_URL = `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`;
// Dev only: ?scene=s1..s6 shows an example Frame without the gateway. The demo build leaves this out.
const SceneApp = import.meta.env.DEV ? lazy(() => import("./features/live/SceneApp")) : null;
const scene = new URLSearchParams(location.search).get("scene");

function LiveApp() {
  const { frame, connected } = useFrames(WS_URL);
  const [zone, setZone] = useState<Polygon | null>(null);
  // The zone is fixed once the operation exists; read it again only after (re)connecting to the gateway.
  useEffect(() => {
    if (connected) fetchZone().then(setZone);
  }, [connected]);
  return <Screen frame={frame} zone={zone} status={connected ? "LIVE" : "연결 끊김"} ok={connected} />;
}

export default function App() {
  if (SceneApp && scene) {
    return (
      <Suspense fallback={null}>
        <SceneApp scene={scene} />
      </Suspense>
    );
  }
  return <LiveApp />;
}
