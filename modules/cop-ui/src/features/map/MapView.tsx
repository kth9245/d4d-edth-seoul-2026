import { type GeoJSONSource, Map as MapLibreMap, setWorkerUrl } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
import { useEffect, useRef } from "react";
import type { Frame, Polygon } from "../../contracts.gen";
import { basemapStyle, TILE_BOUNDS } from "./basemap";
import { frameMarkers } from "./frameMarkers";
import { clearMarkers, type MarkerStore, syncTargets, syncVehicles } from "./markers";
import { zoneGeoJSON } from "./zoneGeoJSON";

// MapLibre 6 loads its worker from next to its own file, but Vite moves that file when bundling (dev and build),
// so GeoJSON layers (the zone) silently never draw. Point it at the real worker file instead.
setWorkerUrl(workerUrl);

const [W, S, E, N] = TILE_BOUNDS;
const PAD = 0.2; // degrees of panning room beyond the fetched tiles (plain background there)

function draw(m: MapLibreMap, vehicles: MarkerStore, targets: MarkerStore, frame: Frame | null): void {
  const { vehicles: vs, targets: ts } = frame ? frameMarkers(frame) : { vehicles: [], targets: [] };
  syncVehicles(m, vehicles, vs);
  syncTargets(m, targets, ts);
}

export function MapView({ frame, zone, tilesAvailable }:
  { frame: Frame | null; zone: Polygon | null; tilesAvailable: boolean }) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<MapLibreMap | null>(null);
  const latest = useRef({ frame, zone });
  const vehicles = useRef<MarkerStore>(new Map());
  const targets = useRef<MarkerStore>(new Map());

  useEffect(() => {
    if (!el.current) return;
    const m = new MapLibreMap({
      container: el.current, style: basemapStyle(tilesAvailable),
      bounds: TILE_BOUNDS, fitBoundsOptions: { padding: 24 },
      maxBounds: [W - PAD, S - PAD, E + PAD, N + PAD],
      // Only the imagery source line (EOX, required); no MapLibre link, never collapsed (theme.css keeps it small).
      attributionControl: { compact: false, customAttribution: [] },
    });
    m.on("load", () => {
      m.addSource("zone", { type: "geojson", data: zoneGeoJSON(latest.current.zone) });
      // Friendly operating area: theme.css --friend (map paint cannot read CSS variables).
      m.addLayer({ id: "zone-fill", type: "fill", source: "zone", paint: { "fill-color": "#80e0ff", "fill-opacity": 0.05 } });
      m.addLayer({ id: "zone-line", type: "line", source: "zone",
        paint: { "line-color": "#80e0ff", "line-opacity": 0.7, "line-width": 1.5, "line-dasharray": [4, 3] } });
    });
    map.current = m;
    draw(m, vehicles.current, targets.current, latest.current.frame);
    const [vs, ts] = [vehicles.current, targets.current];
    return () => {
      clearMarkers(vs);
      clearMarkers(ts);
      m.remove();
      map.current = null;
    };
  }, [tilesAvailable]);

  useEffect(() => {
    latest.current.frame = frame;
    if (map.current) draw(map.current, vehicles.current, targets.current, frame);
  }, [frame]);

  useEffect(() => {
    latest.current.zone = zone;
    (map.current?.getSource("zone") as GeoJSONSource | undefined)?.setData(zoneGeoJSON(zone));
  }, [zone]);

  return <div ref={el} className="map" />;
}
