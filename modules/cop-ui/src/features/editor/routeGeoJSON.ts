import type { GeoPoint } from "../../contracts.gen";

type Feature =
  | { type: "Feature"; properties: Record<string, string>; geometry: { type: "LineString"; coordinates: number[][] } }
  | { type: "Feature"; properties: { n: string }; geometry: { type: "Point"; coordinates: number[] } };

// The route being drawn in the route window (decision 0054): a line through the clicked points (from two on)
// and each point as a dot carrying its click order (the map has no glyphs, so the first dot is drawn larger).
export function routeGeoJSON(points: GeoPoint[]): { type: "FeatureCollection"; features: Feature[] } {
  const coords = points.map((p) => [p.lon, p.lat]);
  const line: Feature[] = coords.length >= 2 ? [{ type: "Feature", properties: {}, geometry: { type: "LineString", coordinates: coords } }] : [];
  const dots: Feature[] = coords.map((c, i) => ({ type: "Feature", properties: { n: String(i + 1) }, geometry: { type: "Point", coordinates: c } }));
  return { type: "FeatureCollection", features: [...line, ...dots] };
}
