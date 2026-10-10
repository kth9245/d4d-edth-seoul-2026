import { type GeoJSONSource, LngLatBounds, Map as MapLibreMap, setWorkerUrl } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
import { useEffect, useRef } from "react";
import type { Frame, GeoPoint, Polygon, WatchPoint } from "../../contracts.gen";
import type { BoardView } from "../board/boardView";
import { cameraPoints } from "../board/cameraPoints";
import { linkLines } from "../board/linkLines";
import { watchCircles } from "../board/watchCircles";
import { basemapStyle, TILE_BOUNDS } from "./basemap";
import { directAims, type PendingAim } from "./directAims";
import { frameMarkers } from "./frameMarkers";
import { clearMarkers, type MarkerStore, syncAim, syncTargets, syncVehicles } from "./markers";
import { zoneGeoJSON } from "./zoneGeoJSON";

// MapLibre 6 loads its worker from next to its own file, but Vite moves that file when bundling (dev and build),
// so GeoJSON layers (the zone) silently never draw. Point it at the real worker file instead.
setWorkerUrl(workerUrl);

const [W, S, E, N] = TILE_BOUNDS;
const PAD = 0.2; // degrees of panning room beyond the fetched tiles (plain background there)
const EMPTY = { type: "FeatureCollection" as const, features: [] };
const USER_HOLD_MS = 10_000;

// A target pointed at with a vehicle selected (decision 0048) and where it sits in the map box, for the role menu.
export interface Pick { target: string; x: number; y: number }

export interface DirectProps {
  selected: string | null;
  pending: PendingAim | null; // the order just sent; the crosses come from the frame (directAims)
  pick: Pick | null;
  onVehicleClick: (id: string) => void;
  onMapClick: (p: GeoPoint) => void;
  onTargetClick: (id: string, x: number, y: number) => void;
  onPoint: (role: string) => void;
  cancelPick: () => void;
}
const NO_DIRECT: DirectProps = { selected: null, pending: null, pick: null, onVehicleClick: () => {}, onMapClick: () => {},
  onTargetClick: () => {}, onPoint: () => {}, cancelPick: () => {} };

// The live board's map (Part1-32): targets where our side knows them (decision 0047), lines from each vehicle on
// a mission to its target, lost targets' estimates and a block's alternative, the landing ring, and a camera that
// fits the open decisions whenever they change (never per frame).
export function MapView({ frame, zone, tilesAvailable, direct = NO_DIRECT, board = null, watch = [] }: {
  frame: Frame | null; zone: Polygon | null; tilesAvailable: boolean; direct?: DirectProps;
  board?: BoardView | null; watch?: WatchPoint[];
}) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<MapLibreMap | null>(null);
  const latest = useRef({ frame, zone, direct, board, watch });
  const lastKey = useRef("");
  const userMoved = useRef(0);
  useEffect(() => {
    // First effect of each commit, so the drawing effects below and marker clicks see this render's callbacks.
    latest.current.direct = direct;
    latest.current.board = board;
    latest.current.watch = watch;
  });
  const vehicles = useRef<MarkerStore>(new Map());
  const targets = useRef<MarkerStore>(new Map());
  const aims = useRef<MarkerStore>(new Map());
  // Marker click handlers are made once per marker, so they read the latest callback through the ref.
  const onVehicleClick = (id: string) => latest.current.direct.onVehicleClick(id);
  // A target click reports where the target sits in the map box, so the role menu opens beside it.
  const onTargetClick = (id: string) => {
    const box = el.current?.getBoundingClientRect();
    const at = targets.current.get(id)?.getElement().getBoundingClientRect();
    if (box && at) latest.current.direct.onTargetClick(id, at.left - box.left + at.width / 2, at.top - box.top + at.height / 2);
  };
  const draw = (m: MapLibreMap) => {
    const { frame: f, direct: d, board: b } = latest.current;
    const { vehicles: vs, targets: ts } = f ? frameMarkers(f, b?.tracks) : { vehicles: [], targets: [] };
    syncVehicles(m, vehicles.current, vs, d.selected, onVehicleClick);
    syncTargets(m, targets.current, ts, onTargetClick);
    syncAim(m, aims.current, directAims(f, d.pending));
    m.getCanvas().style.cursor = d.selected ? "crosshair" : "";
    (m.getSource("links") as GeoJSONSource | undefined)?.setData(f && b ? linkLines(f, b.tracks, b.queue) : EMPTY);
    (m.getSource("watch") as GeoJSONSource | undefined)?.setData(watchCircles(latest.current.watch));
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
    m.on("movestart", (e) => { if (e.originalEvent) userMoved.current = Date.now(); });
    m.on("load", () => {
      m.addSource("zone", { type: "geojson", data: zoneGeoJSON(latest.current.zone) });
      // Friendly operating area: theme.css --friend (map paint cannot read CSS variables).
      m.addLayer({ id: "zone-fill", type: "fill", source: "zone", paint: { "fill-color": "#80e0ff", "fill-opacity": 0.05 } });
      m.addLayer({ id: "zone-line", type: "line", source: "zone",
        paint: { "line-color": "#80e0ff", "line-opacity": 0.7, "line-width": 1.5, "line-dasharray": [4, 3] } });
      // Expected landing radius: --warn, outline only so it never outshines the targets.
      m.addSource("watch", { type: "geojson", data: watchCircles(latest.current.watch) });
      m.addLayer({ id: "watch-line", type: "line", source: "watch",
        paint: { "line-color": "#f59e0b", "line-opacity": 0.4, "line-width": 1, "line-dasharray": [2, 2] } });
      // Vehicle → target (--friend dashed), strike (--hostile solid), lost estimate (--warn dotted), alternative (--live dashed).
      m.addSource("links", { type: "geojson", data: EMPTY });
      m.addLayer({ id: "link-watch", type: "line", source: "links", filter: ["==", ["get", "k"], "watch"],
        paint: { "line-color": "#80e0ff", "line-width": 1.6, "line-opacity": 0.85, "line-dasharray": [2, 2] } });
      m.addLayer({ id: "link-strike", type: "line", source: "links", filter: ["==", ["get", "k"], "strike"],
        paint: { "line-color": "#ef4444", "line-width": 2.5 } });
      m.addLayer({ id: "link-est", type: "line", source: "links", filter: ["==", ["get", "k"], "est"],
        paint: { "line-color": "#f59e0b", "line-width": 1.5, "line-dasharray": [1, 2] } });
      m.addLayer({ id: "link-alt", type: "line", source: "links", filter: ["==", ["get", "k"], "alt"],
        paint: { "line-color": "#4ade80", "line-width": 1.8, "line-dasharray": [3, 2] } });
      draw(m);
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
  }, [frame, board, direct.selected, direct.pending]);

  useEffect(() => {
    // Camera follows the open decisions (Part1-32): refit when the set of open items changes, or when one of its
    // points left the view (a chasing drone flies off), but not for 10 s after the operator moved the map.
    const m = map.current;
    if (!m || !frame || !board) return;
    const key = board.queue.action.map((i) => i.key).join("|");
    const pts = cameraPoints(frame, board.tracks, board.queue);
    const view = m.getBounds();
    const out = !m.isMoving() && Date.now() - userMoved.current > USER_HOLD_MS
      && pts.some((p) => !view.contains([p.lon, p.lat]));
    if (key === lastKey.current && !out) return;
    lastKey.current = key;
    if (pts.length === 0) return;
    const bounds = new LngLatBounds();
    pts.forEach((p) => bounds.extend([p.lon, p.lat]));
    m.fitBounds(bounds, { padding: { top: 60, bottom: 40, left: 60, right: 110 }, maxZoom: 13.4, duration: 700 });
  }, [frame, board]);

  useEffect(() => {
    latest.current.zone = zone;
    (map.current?.getSource("zone") as GeoJSONSource | undefined)?.setData(zoneGeoJSON(zone));
  }, [zone]);

  // While a vehicle is selected the map is picking: targets take clicks (theme.css) for pointing.
  return <div ref={el} className={direct.selected ? "map picking" : "map"} />;
}
