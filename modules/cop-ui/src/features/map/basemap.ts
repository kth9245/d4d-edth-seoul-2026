import { layers, namedFlavor } from "@protomaps/basemaps";
import type { LayerSpecification, StyleSpecification } from "maplibre-gl";

const TILES_PATH = "/tiles/seoul.pmtiles";
const BG: LayerSpecification = { id: "bg", type: "background", paint: { "background-color": "#0b1320" } };

export async function tilesExist(): Promise<boolean> {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), 1500);
  try {
    const r = await fetch(TILES_PATH, { method: "HEAD", signal: ctl.signal });
    const type = r.headers.get("content-type") ?? "";
    return r.ok && !type.includes("text/html");
  } catch {
    return false;
  } finally {
    clearTimeout(timer);
  }
}

export function basemapStyle(tilesAvailable: boolean): StyleSpecification {
  if (!tilesAvailable) return { version: 8, sources: {}, layers: [BG] };
  const origin = typeof location === "undefined" ? "http://localhost" : location.origin;
  const base = layers("protomaps", namedFlavor("dark")).filter((l) => l.type !== "symbol");
  return {
    version: 8,
    sources: { protomaps: { type: "vector", url: `pmtiles://${origin}${TILES_PATH}` } },
    layers: [BG, ...(base as LayerSpecification[])],
  };
}
