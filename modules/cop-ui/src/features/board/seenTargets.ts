import type { GeoPoint, Target } from "../../contracts.gen";
import type { Track } from "./trackState";

export interface SeenTarget { id: string; kind: string; threat: number; distM: number }

export const TARGET_KIND_KO: Record<string, string> = {
  boat: "보트", fast_boat: "고속정", person: "사람", unknown: "미상", drone: "자폭 드론", usv: "적 수상정", ugv: "적 지상로봇",
};
const M_PER_DEG = 111_320;

// The enemies a target role can be pointed at from the vehicle menu: the ones our sensors see right now (track
// "seen", decision 0047). Lost, RF-only, never-seen and struck targets are left out: we do not know where they are
// and a strike would fly to the simulator's true position. Most dangerous first, then nearest.
export function seenTargets(targets: Target[], tracks: Record<string, Track>, from: GeoPoint): SeenTarget[] {
  const mLon = M_PER_DEG * Math.cos((from.lat * Math.PI) / 180);
  return targets
    .filter((t) => tracks[t.id]?.k === "seen")
    .map((t) => ({ id: t.id, kind: TARGET_KIND_KO[t.kind] ?? t.kind, threat: t.threat ?? 0,
      distM: Math.round(Math.hypot((t.pos.lat - from.lat) * M_PER_DEG, (t.pos.lon - from.lon) * mLon)) }))
    .sort((a, b) => b.threat - a.threat || a.distM - b.distM);
}
