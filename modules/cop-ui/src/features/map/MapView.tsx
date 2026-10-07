import { addProtocol, Map as MapLibreMap, type ExpressionSpecification, type GeoJSONSource } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { useEffect, useRef } from "react";
import type { Frame } from "../../contracts.gen";
import { basemapStyle } from "./basemap";
import { toGeoJSON } from "./toGeoJSON";

const CLASS_COLOR = ["match", ["get", "cls"], "drone", "#ff4d4f", "balloon", "#faad14",
  "bird", "#52c41a", "#bfbfbf"] as ExpressionSpecification;

// pmtiles:// 주소를 읽으려면 프로토콜 등록이 필요하다(한 번만).
const protocol = new Protocol();
addProtocol("pmtiles", protocol.tile);

export function MapView({ frame, center, tilesAvailable = false }:
  { frame: Frame | null; center: [number, number]; tilesAvailable?: boolean }) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<MapLibreMap | null>(null);
  const latest = useRef<Frame | null>(frame);

  useEffect(() => {
    if (!el.current) return;
    const m = new MapLibreMap({ container: el.current, style: basemapStyle(tilesAvailable), center, zoom: 13 });
    m.on("load", () => {
      m.addSource("tracks", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      m.addLayer({ id: "tracks", type: "circle", source: "tracks", paint: {
        "circle-color": CLASS_COLOR,
        "circle-radius": ["+", 5, ["*", 10, ["get", "threat"]]],
        "circle-stroke-color": "#fff", "circle-stroke-width": 1 } });
      if (latest.current) (m.getSource("tracks") as GeoJSONSource).setData(toGeoJSON(latest.current));
    });
    map.current = m;
    return () => m.remove();
  }, [center, tilesAvailable]);

  useEffect(() => {
    latest.current = frame;
    const src = map.current?.getSource("tracks") as GeoJSONSource | undefined;
    if (src && frame) src.setData(toGeoJSON(frame));
  }, [frame]);

  return <div ref={el} className="map" />;
}
