import { type GeoJSONSource, Map as MapLibreMap, setWorkerUrl } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
import { useEffect, useRef, useState } from "react";
import type { GeoPoint, Polygon } from "../../contracts.gen";
import { routeGeoJSON } from "../editor/routeGeoJSON";
import { ATTRIBUTION, basemapStyle, tilesExist } from "./basemap";
import { zoneGeoJSON } from "./zoneGeoJSON";

// Same worker fix as MapView: without it Vite moves the worker and the zone layer never draws.
setWorkerUrl(workerUrl);

// The route window's map (decision 0054): the local imagery and the operating zone; each click adds a point
// and the route so far is drawn as a line with dots (the first one larger). Fits the zone; pan and zoom work.
export function RouteMap({ zone, points, onAdd }: { zone: Polygon; points: GeoPoint[]; onAdd: (p: GeoPoint) => void }) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<MapLibreMap | null>(null);
  const add = useRef(onAdd);
  add.current = onAdd;
  const [tiles, setTiles] = useState(false);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    let gone = false;
    tilesExist().then((ok) => {
      if (gone || !el.current) return;
      setTiles(ok);
      const lons = zone.points.map((p) => p.lon);
      const lats = zone.points.map((p) => p.lat);
      const m = new MapLibreMap({
        container: el.current, style: basemapStyle(ok), attributionControl: false,
        bounds: [Math.min(...lons), Math.min(...lats), Math.max(...lons), Math.max(...lats)], fitBoundsOptions: { padding: 20 },
      });
      m.on("load", () => {
        m.addSource("zone", { type: "geojson", data: zoneGeoJSON(zone) });
        // Friendly operating area: theme.css --friend; the route is the system's own green (--live).
        m.addLayer({ id: "zone-line", type: "line", source: "zone",
          paint: { "line-color": "#80e0ff", "line-opacity": 0.8, "line-width": 1.2, "line-dasharray": [4, 3] } });
        m.addSource("route", { type: "geojson", data: routeGeoJSON([]) });
        m.addLayer({ id: "route-line", type: "line", source: "route", filter: ["==", "$type", "LineString"],
          paint: { "line-color": "#4ade80", "line-width": 2 } });
        m.addLayer({ id: "route-dot", type: "circle", source: "route", filter: ["==", "$type", "Point"],
          paint: { "circle-radius": ["case", ["==", ["get", "n"], "1"], 8, 5], "circle-color": "#4ade80",
            "circle-stroke-color": "#000000", "circle-stroke-width": 1 } });
        setReady(true);
      });
      m.on("click", (e) => add.current({ lat: e.lngLat.lat, lon: e.lngLat.lng, alt_m: 0 }));
      map.current = m;
    });
    return () => {
      gone = true;
      map.current?.remove();
      map.current = null;
    };
  }, [zone]);
  useEffect(() => {
    if (ready) (map.current?.getSource("route") as GeoJSONSource | undefined)?.setData(routeGeoJSON(points));
  }, [points, ready]);
  return (
    <figure className="route-map-wrap">
      <div className="route-map" ref={el} />
      {tiles && <figcaption>{ATTRIBUTION}</figcaption>}
    </figure>
  );
}
