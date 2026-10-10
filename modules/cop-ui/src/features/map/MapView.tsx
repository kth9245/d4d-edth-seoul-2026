import { type GeoJSONSource, Map as MapLibreMap, setWorkerUrl } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
import { useEffect, useRef } from "react";
import type { Frame, GeoPoint, Polygon } from "../../contracts.gen";
import { basemapStyle, TILE_BOUNDS } from "./basemap";
import { frameMarkers } from "./frameMarkers";
import { clearMarkers, type MarkerStore, syncAim, syncTargets, syncVehicles } from "./markers";
import { zoneGeoJSON } from "./zoneGeoJSON";

// MapLibre 6 loads its worker from next to its own file, but Vite moves that file when bundling (dev and build),
// so GeoJSON layers (the zone) silently never draw. Point it at the real worker file instead.
setWorkerUrl(workerUrl);

const [W, S, E, N] = TILE_BOUNDS;
const PAD = 0.2; // degrees of panning room beyond the fetched tiles (plain background there)

export type Aim = GeoPoint & { label: string };
export interface DirectProps {
  selected: string | null;
  aim: Aim | null;
  onVehicleClick: (id: string) => void;
  onMapClick: (p: GeoPoint) => void;
}
const NO_DIRECT: DirectProps = { selected: null, aim: null, onVehicleClick: () => {}, onMapClick: () => {} };

export function MapView({ frame, zone, tilesAvailable, direct = NO_DIRECT }:
  { frame: Frame | null; zone: Polygon | null; tilesAvailable: boolean; direct?: DirectProps }) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<MapLibreMap | null>(null);
  const latest = useRef({ frame, zone, direct });
  useEffect(() => {
    // First effect of each commit, so the drawing effects below and marker clicks see this render's callbacks.
    latest.current.direct = direct;
  });
  const vehicles = useRef<MarkerStore>(new Map());
  const targets = useRef<MarkerStore>(new Map());
  const aims = useRef<MarkerStore>(new Map());
  // Marker click handlers are made once per marker, so they read the latest callback through the ref.
  const onVehicleClick = (id: string) => latest.current.direct.onVehicleClick(id);
  const draw = (m: MapLibreMap) => {
    const { frame: f, direct: d } = latest.current;
    const { vehicles: vs, targets: ts } = f ? frameMarkers(f) : { vehicles: [], targets: [] };
    syncVehicles(m, vehicles.current, vs, d.selected, onVehicleClick);
    syncTargets(m, targets.current, ts);
    syncAim(m, aims.current, d.aim);
    m.getCanvas().style.cursor = d.selected ? "crosshair" : "";
  };

  useEffect(() => {
    if (!el.current) return;
    const m = new MapLibreMap({
      container: el.current, style: basemapStyle(tilesAvailable),
      bounds: TILE_BOUNDS, fitBoundsOptions: { padding: 24 },
      maxBounds: [W - PAD, S - PAD, E + PAD, N + PAD],
      // Only the imagery source line (EOX, required); no MapLibre link, never collapsed (theme.css keeps it small).
      attributionControl: { compact: false, customAttribution: [] },
    });
    m.on("click", (e) => latest.current.direct.onMapClick({ lat: e.lngLat.lat, lon: e.lngLat.lng }));
    m.on("load", () => {
      m.addSource("zone", { type: "geojson", data: zoneGeoJSON(latest.current.zone) });
      // Friendly operating area: theme.css --friend (map paint cannot read CSS variables).
      m.addLayer({ id: "zone-fill", type: "fill", source: "zone", paint: { "fill-color": "#80e0ff", "fill-opacity": 0.05 } });
      m.addLayer({ id: "zone-line", type: "line", source: "zone",
        paint: { "line-color": "#80e0ff", "line-opacity": 0.7, "line-width": 1.5, "line-dasharray": [4, 3] } });
    });
    map.current = m;
    draw(m);
    const stores = [vehicles.current, targets.current, aims.current];
    return () => {
      stores.forEach(clearMarkers);
      m.remove();
      map.current = null;
    };
  }, [tilesAvailable]);

  useEffect(() => {
    latest.current.frame = frame;
    if (map.current) draw(map.current);
  }, [frame, direct.selected, direct.aim]);

  useEffect(() => {
    latest.current.zone = zone;
    (map.current?.getSource("zone") as GeoJSONSource | undefined)?.setData(zoneGeoJSON(zone));
  }, [zone]);

  return <div ref={el} className="map" />;
}
