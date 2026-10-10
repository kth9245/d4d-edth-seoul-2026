import { describe, expect, it } from "vitest";
import { at } from "./boardFixtures";
import { watchCircles } from "./watchCircles";

describe("watchCircles", () => {
  it("draws each watch point's radius as a closed ring of 64 segments", () => {
    const fc = watchCircles([{ id: "landing", name: "상륙 예상 지점", pos: at(37.978, 124.7), radius_m: 2000 }]);
    const ring = fc.features[0].geometry.coordinates;
    expect(ring).toHaveLength(65);
    expect(ring[64]).toEqual(ring[0]);
    expect(ring[0][1]).toBeCloseTo(37.978, 6);
    expect(ring[16][1]).toBeCloseTo(37.978 + 2000 / 111_320, 6);
  });

  it("is empty without watch points", () => {
    expect(watchCircles([]).features).toEqual([]);
  });
});
