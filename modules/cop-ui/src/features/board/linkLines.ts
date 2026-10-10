import type { Feature, FeatureCollection, LineString } from "geojson";
import type { Frame, GeoPoint } from "../../contracts.gen";
import type { Queue } from "./decisionQueue";
import type { Track } from "./trackState";

export type LinkKind = "watch" | "strike" | "est" | "alt";
type Link = Feature<LineString, { k: LinkKind; v: string }>;

const line = (k: LinkKind, v: string, a: GeoPoint, b: GeoPoint): Link =>
  ({ type: "Feature", properties: { k, v }, geometry: { type: "LineString", coordinates: [[a.lon, a.lat], [b.lon, b.lat]] } });

// Map lines (Part1-32): each vehicle on a mission to the target it works (dashed watch, solid strike; none to a
// struck target unless striking), a lost target's estimate from where it was last seen, and a blocked vehicle
// to the alternative point its block offers.
export function linkLines(f: Frame, tracks: Record<string, Track>, queue: Queue): FeatureCollection<LineString, { k: LinkKind; v: string }> {
  const out: Link[] = [];
  for (const v of f.vehicles) {
    const tr = v.status === "active" && v.target_id ? tracks[v.target_id] : undefined;
    const strike = v.active?.command.kind === "strike";
    if (tr && (tr.k !== "gone" || strike)) out.push(line(strike ? "strike" : "watch", v.id, v.pos, tr.pos));
  }
  for (const [id, tr] of Object.entries(tracks)) if (tr.est) out.push(line("est", id, tr.pos, tr.est));
  for (const c of queue.action.flatMap((i) => i.cards)) {
    const v = c.source === "block" && c.alternative ? f.vehicles.find((x) => x.id === c.vehicle) : undefined;
    if (v && c.alternative) out.push(line("alt", v.id, v.pos, c.alternative));
  }
  return { type: "FeatureCollection", features: out };
}
