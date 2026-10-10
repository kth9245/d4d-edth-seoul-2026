import { lazy, Suspense, useEffect, useState } from "react";
import type { Polygon } from "./contracts.gen";
import { EditorScreen } from "./features/editor/EditorScreen";
import { fetchZone } from "./features/live/fetchZone";
import { useFrames } from "./features/live/useFrames";
import { tabFromHash } from "./features/nav/tab";
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
  const [hash, setHash] = useState(location.hash);
  useEffect(() => {
    const onHash = () => setHash(location.hash);
    addEventListener("hashchange", onHash);
    return () => removeEventListener("hashchange", onHash);
  }, []);
  const tab = tabFromHash(hash);
  return (
    <div className="app">
      <header className="tabs">
        <span className="brand"><b>ROLECALL</b><small>BAENGNYEONG SECTOR</small></span>
        <a href="#editor" className={tab === "editor" ? "on" : ""}>편집기</a>
        <a href="#live" className={tab === "live" ? "on" : ""}>상황판</a>
      </header>
      {tab === "editor" ? (
        <EditorScreen />
      ) : SceneApp && scene ? (
        <Suspense fallback={null}>
          <SceneApp scene={scene} />
        </Suspense>
      ) : (
        <LiveApp />
      )}
    </div>
  );
}
