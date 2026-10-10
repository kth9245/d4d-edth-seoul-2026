import type { FeatureCollection, LineString, Position } from "geojson";
import type { WatchPoint } from "../../contracts.gen";

const M_PER_DEG = 111_320;
const SEGMENTS = 64;

// Watch point radius as a ring (Part1-32): "inside the expected landing radius +0.30" on a risk line is visible
// on the map. Outline only, so it never outshines the targets.
export function watchCircles(watch: WatchPoint[]): FeatureCollection<LineString> {
  return {
    type: "FeatureCollection",
    features: watch.map((w) => {
      const mLon = M_PER_DEG * Math.cos((w.pos.lat * Math.PI) / 180);
      const ring: Position[] = [];
      for (let i = 0; i <= SEGMENTS; i++) {
        const a = (i / SEGMENTS) * 2 * Math.PI;
        ring.push(i === SEGMENTS ? ring[0]
          : [w.pos.lon + (w.radius_m * Math.cos(a)) / mLon, w.pos.lat + (w.radius_m * Math.sin(a)) / M_PER_DEG]);
      }
      return { type: "Feature", properties: {}, geometry: { type: "LineString", coordinates: ring } };
    }),
  };
}
