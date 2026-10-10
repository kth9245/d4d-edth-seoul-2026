import type { FeatureCollection, Polygon as GeoPolygon, Position } from "geojson";
import type { Polygon } from "../../contracts.gen";

// Operation zone (set once when the operation is created) → GeoJSON polygon with a closed [lon, lat] ring.
export function zoneGeoJSON(zone: Polygon | null): FeatureCollection<GeoPolygon> {
  if (!zone || zone.points.length === 0) return { type: "FeatureCollection", features: [] };
  const ring: Position[] = zone.points.map((p) => [p.lon, p.lat]);
  const [first, last] = [ring[0], ring[ring.length - 1]];
  if (first[0] !== last[0] || first[1] !== last[1]) ring.push(first);
  return {
    type: "FeatureCollection",
    features: [{ type: "Feature", properties: {}, geometry: { type: "Polygon", coordinates: [ring] } }],
  };
}
