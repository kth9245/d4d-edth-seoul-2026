import type { FeatureCollection, Point } from "geojson";
import type { Frame } from "../../contracts.gen";

export function toGeoJSON(frame: Frame): FeatureCollection<Point> {
  const assess = new Map(frame.assessments.map((a) => [a.track_id, a]));
  const resp = new Map(frame.responses.map((r) => [r.track_id, r]));
  return {
    type: "FeatureCollection",
    features: frame.tracks.map((t) => ({
      type: "Feature",
      geometry: { type: "Point", coordinates: [t.lon, t.lat] },
      properties: {
        id: t.id,
        cls: assess.get(t.id)?.object_class ?? "unknown",
        threat: assess.get(t.id)?.threat ?? 0,
        response: resp.get(t.id)?.kind ?? "observe",
      },
    })),
  };
}
