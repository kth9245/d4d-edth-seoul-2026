import type { RasterLayerSpecification, RasterSourceSpecification } from "maplibre-gl";
import { afterEach, describe, expect, it, vi } from "vitest";
import { basemapStyle, TILE_BOUNDS, tilesExist } from "./basemap";

describe("basemapStyle", () => {
  it("returns background-only style when tiles missing", () => {
    const s = basemapStyle(false, false);
    expect(Object.keys(s.sources)).toHaveLength(0);
    expect(s.layers.map((l) => l.type)).toEqual(["background"]);
  });

  it("uses the local Baengnyeong raster tiles z8-14 inside the fetched bounds", () => {
    const s = basemapStyle(true, false);
    const src = s.sources.sat as RasterSourceSpecification;
    expect(src.type).toBe("raster");
    expect(src.tiles).toEqual(["http://localhost/tiles/baengnyeong/{z}/{x}/{y}.jpg"]);
    expect([src.minzoom, src.maxzoom, src.tileSize]).toEqual([8, 14, 256]);
    expect(src.bounds).toEqual(TILE_BOUNDS);
    expect(src.attribution).toContain("EOX");
    expect(s.layers.map((l) => l.type)).toEqual(["background", "raster"]);
    expect(s.glyphs).toBeUndefined();
  });

  it("dims the raster for the night scene", () => {
    const sat = basemapStyle(true, false).layers[1] as RasterLayerSpecification;
    expect(sat.paint?.["raster-brightness-max"]).toBeLessThan(1);
  });
});

describe("high-resolution Esri layer (user 10/11)", () => {
  it("streams Esri z8-18 over the local EOX tiles, dimmed the same, inside the same bounds", () => {
    const s = basemapStyle(true, true);
    expect(s.layers.map((l) => l.id)).toEqual(["bg", "sat", "hires"]);
    const src = s.sources.hires as RasterSourceSpecification;
    expect(src.tiles?.[0]).toContain("server.arcgisonline.com/ArcGIS/rest/services/World_Imagery");
    expect([src.minzoom, src.maxzoom, src.bounds]).toEqual([8, 18, TILE_BOUNDS]);
    expect(src.attribution).toContain("Esri");
    const hires = s.layers[2] as RasterLayerSpecification;
    expect(hires.paint?.["raster-brightness-max"]).toBe(0.6);
  });

  it("shows Esri alone when the local tiles are missing, and nothing of it when switched off", () => {
    expect(basemapStyle(false, true).layers.map((l) => l.id)).toEqual(["bg", "hires"]);
    expect(Object.keys(basemapStyle(true, false).sources)).toEqual(["sat"]);
  });
});

describe("tilesExist", () => {
  afterEach(() => vi.unstubAllGlobals());
  const stub = (res: Partial<Response> | Error) => {
    const f = vi.fn(() => (res instanceof Error ? Promise.reject(res) : Promise.resolve(res)));
    vi.stubGlobal("fetch", f);
    return f;
  };
  const resp = (status: number, type: string) =>
    ({ ok: status < 400, status, headers: new Headers({ "content-type": type }) }) as Response;

  it("probes a Baengnyeong z8 tile", async () => {
    const f = stub(resp(200, "image/jpeg"));
    expect(await tilesExist()).toBe(true);
    expect(f.mock.calls[0]).toContain("/tiles/baengnyeong/8/216/98.jpg");
  });
  it("is false for 200 text/html (SPA fallback)", async () => {
    stub(resp(200, "text/html; charset=utf-8"));
    expect(await tilesExist()).toBe(false);
  });
  it("is false for 404", async () => {
    stub(resp(404, "text/plain"));
    expect(await tilesExist()).toBe(false);
  });
  it("is false when fetch rejects", async () => {
    stub(new Error("net"));
    expect(await tilesExist()).toBe(false);
  });
  it("is false when the request hangs", async () => {
    vi.useFakeTimers();
    vi.stubGlobal("fetch", (_u: string, init?: RequestInit) => new Promise((_res, rej) => {
      init?.signal?.addEventListener("abort", () => rej(new Error("abort")));
    }));
    const p = tilesExist();
    await vi.advanceTimersByTimeAsync(2000);
    expect(await p).toBe(false);
    vi.useRealTimers();
  });
});
