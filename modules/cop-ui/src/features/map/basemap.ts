import type { LayerSpecification, StyleSpecification } from "maplibre-gl";

// Area fetched by scripts/fetch_tiles_baengnyeong.sh (W,S,E,N). Outside it there are no tiles, so none are requested.
export const TILE_BOUNDS: [number, number, number, number] = [124.55, 37.88, 124.85, 38.02];
const TILES_DIR = "/tiles/baengnyeong";
const PROBE = `${TILES_DIR}/8/216/98.jpg`;
const ATTRIBUTION = "© EOX IT Services GmbH — Sentinel-2 cloudless 2020 (CC BY-NC-SA 4.0), contains modified Copernicus Sentinel data";
const BG: LayerSpecification = { id: "bg", type: "background", paint: { "background-color": "#0b1320" } };

export async function tilesExist(): Promise<boolean> {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), 1500);
  try {
    const r = await fetch(PROBE, { method: "HEAD", signal: ctl.signal });
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
  return {
    version: 8,
    sources: {
      sat: {
        type: "raster", tiles: [`${origin}${TILES_DIR}/{z}/{x}/{y}.jpg`], tileSize: 256,
        minzoom: 8, maxzoom: 14, bounds: TILE_BOUNDS, attribution: ATTRIBUTION,
      },
    },
    // Daytime imagery dimmed for the night operation so vehicle and target markers stand out.
    layers: [BG, { id: "sat", type: "raster", source: "sat", paint: { "raster-brightness-max": 0.65 } }],
  };
}
