import type { Frame, GeoPoint } from "../../contracts.gen";
import type { Queue } from "./decisionQueue";
import type { Track } from "./trackState";

const KEEP_GONE_MS = 120_000;
const movedBy = (preview: string) => preview.split(" · ").map((x) => x.split("→")[0]).filter(Boolean);

// Where the map looks (Part1-32): targets where we show them (and where a lost one may be now), vehicles on a
// mission with a target, every vehicle an open card names (reporter and the vehicles its choices move), and a
// block's alternative point.
export function cameraPoints(f: Frame, tracks: Record<string, Track>, queue: Queue): GeoPoint[] {
  const pts: GeoPoint[] = [];
  for (const t of f.targets) {
    const tr = tracks[t.id];
    if (!tr || (t.neutralized_ms != null && f.t_ms - t.neutralized_ms >= KEEP_GONE_MS)) continue;
    pts.push(tr.pos, ...(tr.est ? [tr.est] : []));
  }
  const cards = queue.action.flatMap((i) => i.cards);
  const named = new Set(cards.flatMap((c) => [...(c.vehicle ?? "").split("·"), ...c.choices.flatMap((ch) => movedBy(ch.preview))]));
  for (const v of f.vehicles) if ((v.status === "active" && v.target_id) || named.has(v.id)) pts.push(v.pos);
  for (const c of cards) if (c.source === "block" && c.alternative) pts.push(c.alternative);
  return pts;
}
