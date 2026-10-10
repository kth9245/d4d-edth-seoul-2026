import { describe, expect, it } from "vitest";
import op from "../../../../../contracts/examples/operation.json";
import type { Operation } from "../../contracts.gen";
import { zoneGeoJSON } from "./zoneGeoJSON";

describe("zoneGeoJSON", () => {
  it("makes one closed [lon, lat] ring from the operation zone", () => {
    const fc = zoneGeoJSON((op as Operation).zone);
    expect(fc.features).toHaveLength(1);
    const ring = fc.features[0].geometry.coordinates[0];
    expect(ring).toHaveLength(5);
    expect(ring[0]).toEqual([124.56, 37.9]);
    expect(ring[4]).toEqual(ring[0]);
  });

  it("does not add a point when the ring is already closed", () => {
    const p = { lat: 37.9, lon: 124.6 };
    const fc = zoneGeoJSON({ points: [p, { lat: 37.95, lon: 124.7 }, { lat: 37.9, lon: 124.7 }, p] });
    expect(fc.features[0].geometry.coordinates[0]).toHaveLength(4);
  });

  it("is empty without a zone", () => {
    expect(zoneGeoJSON(null).features).toEqual([]);
  });
});
