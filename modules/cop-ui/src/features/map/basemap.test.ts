import { describe, expect, it } from "vitest";
import { basemapStyle } from "./basemap";

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
