import { Map as MapLibreMap, setWorkerUrl } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
import { useEffect, useRef, useState } from "react";
import type { Polygon, VehicleSpec } from "../../contracts.gen";
import { ATTRIBUTION, basemapStyle, tilesExist } from "./basemap";
import { clearMarkers, type MarkerStore, syncVehicles } from "./markers";
import { zoneGeoJSON } from "./zoneGeoJSON";

// Same worker fix as MapView: without it Vite moves the worker and the zone layer never draws.
setWorkerUrl(workerUrl);

// A still map of the operation for the editor's operation panel (Part3-14): the local imagery, the operating
// zone and each vehicle at its home (dots only; the table beside it names them). No panning or clicks; it fits
// the zone. The imagery credit goes under the map, since MapLibre's control wraps over a map this small.
export function MiniMap({ zone, vehicles }: { zone: Polygon; vehicles: VehicleSpec[] }) {
  const el = useRef<HTMLDivElement>(null);
  const [tiles, setTiles] = useState(false);
  useEffect(() => {
    let map: MapLibreMap | null = null;
    const store: MarkerStore = new Map();
    let gone = false;
    tilesExist().then((ok) => {
      if (gone || !el.current) return;
      setTiles(ok);
      const lons = zone.points.map((p) => p.lon);
      const lats = zone.points.map((p) => p.lat);
      const m = new MapLibreMap({
        container: el.current, style: basemapStyle(ok), interactive: false, attributionControl: false,
        bounds: [Math.min(...lons), Math.min(...lats), Math.max(...lons), Math.max(...lats)], fitBoundsOptions: { padding: 14 },
      });
      m.on("load", () => {
        m.addSource("zone", { type: "geojson", data: zoneGeoJSON(zone) });
        // Friendly operating area: theme.css --friend (map paint cannot read CSS variables).
        m.addLayer({ id: "zone-fill", type: "fill", source: "zone", paint: { "fill-color": "#80e0ff", "fill-opacity": 0.06 } });
        m.addLayer({ id: "zone-line", type: "line", source: "zone",
          paint: { "line-color": "#80e0ff", "line-opacity": 0.8, "line-width": 1.2, "line-dasharray": [4, 3] } });
      });
      const homes = vehicles.map((v) => ({ id: v.id, lat: v.home.lat, lon: v.home.lon, status: "ready" as const,
        battery: "ok" as const, label: v.id })); // labels are hidden on the mini map
      syncVehicles(m, store, homes, null, () => {});
      map = m;
    });
    return () => {
      gone = true;
      clearMarkers(store);
      map?.remove();
    };
  }, [zone, vehicles]);
  return (
    <figure className="mini-map-wrap">
      <div className="mini-map" ref={el} />
      {tiles && <figcaption>{ATTRIBUTION}</figcaption>}
    </figure>
  );
}
