import { Screen } from "../../Screen";
import { SCENE_ZONE, SCENES } from "./sceneFrames";

// Dev only (?scene=s1..s6): one example Frame, no gateway.
export default function SceneApp({ scene }: { scene: string }) {
  const frame = SCENES[scene] ?? null;
  const status = frame ? `장면 ${scene} (예시 Frame)` : `없는 장면 ${scene} (${Object.keys(SCENES).sort().join("·")})`;
  return <Screen frame={frame} zone={SCENE_ZONE} status={status} ok={frame !== null} />;
}
