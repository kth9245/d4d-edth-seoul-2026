import { afterEach, describe, expect, it, vi } from "vitest";
import { basemapStyle, tilesExist } from "./basemap";

describe("basemapStyle", () => {
  it("returns background-only style when tiles missing", () => {
    const s = basemapStyle(false);
    expect(Object.keys(s.sources)).toHaveLength(0);
    expect(s.layers.map((l) => l.type)).toEqual(["background"]);
  });

  it("uses local pmtiles without any symbol layers when tiles exist", () => {
    const s = basemapStyle(true);
    const src = s.sources.protomaps as { type: string; url: string };
    expect(src.type).toBe("vector");
    expect(src.url).toMatch(/^pmtiles:\/\/.*\/tiles\/seoul\.pmtiles$/);
    expect(s.layers.some((l) => l.type === "symbol")).toBe(false);
    expect(s.glyphs).toBeUndefined();
    expect(s.layers.length).toBeGreaterThan(5);
  });
});

describe("tilesExist", () => {
  afterEach(() => vi.unstubAllGlobals());
  const stub = (res: Partial<Response> | Error) =>
    vi.stubGlobal("fetch", vi.fn(() => (res instanceof Error ? Promise.reject(res) : Promise.resolve(res))));
  const resp = (status: number, type: string) =>
    ({ ok: status < 400, status, headers: new Headers({ "content-type": type }) }) as Response;

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
  it("is true for 200 application/octet-stream", async () => {
    stub(resp(200, "application/octet-stream"));
    expect(await tilesExist()).toBe(true);
  });
});
