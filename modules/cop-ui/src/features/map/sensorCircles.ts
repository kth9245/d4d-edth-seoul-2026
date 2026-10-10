import type { FeatureCollection, Polygon } from "geojson";
import type { Domain, Frame, VehicleSpec, VehicleStatus } from "../../contracts.gen";
import { watchCircles } from "../board/watchCircles";

// Only vehicles on a mission (Part1-32.5): the engine also detects with vehicles waiting at base (sensing LIVE has
// ready too), but four waiting drones stacked their discs on the base, so those are left out (lead, 10/11).
const SHOWN: VehicleStatus[] = ["active"];

// Each vehicle's detection area (Part1-32.2): a disc of its spec's sensor_range_m around where it is now, so a
// target inside the disc is one the board calls seen.
export function sensorCircles(f: Frame, specs: VehicleSpec[]): FeatureCollection<Polygon, { id: string; domain: Domain }> {
  const byId = Object.fromEntries(specs.map((s) => [s.id, s]));
  const live = f.vehicles.filter((v) => SHOWN.includes(v.status) && byId[v.id]);
  const rings = watchCircles(live.map((v) => ({ id: v.id, name: byId[v.id].name, pos: v.pos, radius_m: byId[v.id].sensor_range_m })));
  return {
    type: "FeatureCollection",
    features: live.map((v, i) => ({ type: "Feature", properties: { id: v.id, domain: byId[v.id].domain },
      geometry: { type: "Polygon", coordinates: [rings.features[i].geometry.coordinates] } })),
  };
}
