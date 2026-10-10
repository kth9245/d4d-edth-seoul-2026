import type { LayerSpecification, StyleSpecification } from "maplibre-gl";

// Area fetched by scripts/fetch_tiles_baengnyeong.sh (W,S,E,N). Outside it there are no tiles, so none are requested.
export const TILE_BOUNDS: [number, number, number, number] = [124.55, 37.88, 124.85, 38.02];
const TILES_DIR = "/tiles/baengnyeong";
const PROBE = `${TILES_DIR}/8/216/98.jpg`;
const EOX_ATTRIBUTION = "© EOX IT Services GmbH — Sentinel-2 cloudless 2020 (CC BY-NC-SA 4.0), contains modified Copernicus Sentinel data";
// High-resolution Esri World Imagery (about 0.6 m at z18) streamed over the local EOX tiles (user 10/11). Never
// downloaded or cached: offline or if Esri fails, the EOX layer under it shows through. Rollback: VITE_BASEMAP=eox in
// modules/cop-ui/.env.local (or revert the commit); the EOX tiles are untouched.
export const HIRES = (import.meta as { env?: Record<string, string | undefined> }).env?.VITE_BASEMAP !== "eox";
const ESRI_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
const ESRI_ATTRIBUTION = "Esri World Imagery — Esri, Maxar, Earthstar Geographics, and the GIS User Community";
export const ATTRIBUTION = HIRES ? `${ESRI_ATTRIBUTION} · ${EOX_ATTRIBUTION}` : EOX_ATTRIBUTION;
// The dimmed sea of the imagery, so the edge of the fetched tiles leaves no seam.
const BG: LayerSpecification = { id: "bg", type: "background", paint: { "background-color": "#0b1616" } };

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

export function basemapStyle(tilesAvailable: boolean, hires: boolean = HIRES): StyleSpecification {
  const origin = typeof location === "undefined" ? "http://localhost" : location.origin;
  // Daytime imagery dimmed for the night operation so vehicle and target markers stand out.
  const paint = { "raster-brightness-max": 0.6, "raster-saturation": -0.4 };
  const style: StyleSpecification = { version: 8, sources: {}, layers: [BG] };
  if (tilesAvailable) {
    style.sources.sat = {
      type: "raster", tiles: [`${origin}${TILES_DIR}/{z}/{x}/{y}.jpg`], tileSize: 256,
      minzoom: 8, maxzoom: 14, bounds: TILE_BOUNDS, attribution: EOX_ATTRIBUTION,
    };
    style.layers.push({ id: "sat", type: "raster", source: "sat", paint });
  }
  if (hires) {
    style.sources.hires = {
      type: "raster", tiles: [ESRI_URL], tileSize: 256, minzoom: 8, maxzoom: 18, bounds: TILE_BOUNDS,
      attribution: ESRI_ATTRIBUTION,
    };
    style.layers.push({ id: "hires", type: "raster", source: "hires", paint });
  }
  return style;
}
