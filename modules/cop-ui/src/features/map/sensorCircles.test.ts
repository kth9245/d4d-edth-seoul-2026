import { describe, expect, it } from "vitest";
import type { Domain, VehicleSpec } from "../../contracts.gen";
import { at, mkFrame, mkVehicle } from "../board/boardFixtures";
import { sensorCircles } from "./sensorCircles";

const spec = (id: string, domain: Domain, sensor_range_m: number) =>
  ({ id, name: id, domain, speed_mps: 10, endurance_min: 60, sensor_range_m, home: at(37.95, 124.7) }) as VehicleSpec;
const SPECS = [spec("d1", "air", 800), spec("usv", "sea", 500), spec("ugv", "ground", 300)];

describe("sensorCircles", () => {
  it("rings each live vehicle (drone, boat, robot) at its sensor range around where it is now", () => {
    const f = mkFrame({ vehicles: [
      mkVehicle({ id: "d1", pos: at(37.98, 124.69), status: "active" }),
      mkVehicle({ id: "usv", pos: at(37.96, 124.72), status: "ready" }),
    ] });
    const fc = sensorCircles(f, SPECS);
    expect(fc.features.map((ft) => ft.properties)).toEqual([{ id: "d1", domain: "air" }, { id: "usv", domain: "sea" }]);
    const ring = fc.features[1].geometry.coordinates[0];
    expect(ring).toHaveLength(65);
    expect(ring[64]).toEqual(ring[0]);
    expect(ring[16][1]).toBeCloseTo(37.96 + 500 / 111_320, 6);
  });

  it("draws no ring where the engine does not detect: returning, lost or in maintenance (sensing LIVE)", () => {
    const f = mkFrame({ vehicles: [
      mkVehicle({ id: "d1", status: "returning" }),
      mkVehicle({ id: "usv", status: "lost" }),
      mkVehicle({ id: "ugv", status: "maintenance" }),
    ] });
    expect(sensorCircles(f, SPECS).features).toEqual([]);
  });

  it("draws nothing before the specs arrive", () => {
    expect(sensorCircles(mkFrame({ vehicles: [mkVehicle({ id: "d1", status: "active" })] }), []).features).toEqual([]);
  });
});
