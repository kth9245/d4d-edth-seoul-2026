import { describe, expect, it } from "vitest";
import { at, mkCard, mkFrame, mkTarget, mkVehicle, T0 } from "./boardFixtures";
import { cameraPoints } from "./cameraPoints";

const EMPTY = { action: [], alerts: [], history: [] };

describe("cameraPoints", () => {
  it("is empty when nothing is on the map", () => {
    expect(cameraPoints(mkFrame(), {}, EMPTY)).toEqual([]);
  });

  it("looks at targets where we show them, a lost one's estimate, and vehicles on a mission with a target", () => {
    const f = mkFrame({
      targets: [mkTarget({ id: "boat1" }), mkTarget({ id: "old", neutralized_ms: T0 - 130_000 })],
      vehicles: [mkVehicle({ id: "d1", status: "active", target_id: "boat1", pos: at(37.98, 124.7) }),
        mkVehicle({ id: "d4", status: "maintenance", target_id: "boat1", pos: at(37.95, 124.7) })],
    });
    const tracks = { boat1: { k: "lost" as const, pos: at(37.99, 124.74), est: at(37.99, 124.75) }, old: { k: "gone" as const, pos: at(1, 1) } };
    expect(cameraPoints(f, tracks, EMPTY)).toEqual([at(37.99, 124.74), at(37.99, 124.75), at(37.98, 124.7)]);
  });

  it("adds every vehicle an open card names and a block's alternative point", () => {
    const f = mkFrame({ vehicles: [mkVehicle({ id: "d3", pos: at(37.94, 124.7) }), mkVehicle({ id: "usv", pos: at(37.98, 124.69) })] });
    const q = { action: [
      { key: "r", cards: [mkCard({ id: "r", choices: [{ id: "t", label: "d3 → 순찰", preview: "d3→patrol_a" }] })] },
      { key: "b", cards: [mkCard({ id: "b", source: "block", vehicle: "usv", alternative: { lat: 38, lon: 124.6 } })] },
    ], alerts: [], history: [] };
    expect(cameraPoints(f, {}, q)).toEqual([at(37.94, 124.7), at(37.98, 124.69), { lat: 38, lon: 124.6 }]);
  });
});
