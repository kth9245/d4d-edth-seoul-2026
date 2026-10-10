import { describe, expect, it } from "vitest";
import { at, mkCard, mkFrame, mkVehicle } from "./boardFixtures";
import { linkLines } from "./linkLines";

const strikeCmd = { command: { id: "c", vehicle_id: "d2", kind: "strike" as const, params: {} }, checks: [], passed_ms: 0 };

describe("linkLines", () => {
  it("joins vehicles on a mission to the target they work, solid for a strike, none for a struck target", () => {
    const f = mkFrame({ vehicles: [
      mkVehicle({ id: "d1", status: "active", target_id: "boat1", pos: at(1, 1) }),
      mkVehicle({ id: "d2", status: "active", target_id: "fast1", pos: at(2, 2), active: strikeCmd }),
      mkVehicle({ id: "d3", status: "active", target_id: "gone1", pos: at(3, 3) }),
      mkVehicle({ id: "d4", status: "maintenance", target_id: "boat1", pos: at(4, 4) }),
    ] });
    const tracks = { boat1: { k: "seen" as const, pos: at(5, 5) }, fast1: { k: "seen" as const, pos: at(6, 6) },
      gone1: { k: "gone" as const, pos: at(7, 7) } };
    const fc = linkLines(f, tracks, { action: [], alerts: [], history: [] });
    expect(fc.features.map((x) => [x.properties.k, x.properties.v, x.geometry.coordinates])).toEqual([
      ["watch", "d1", [[1, 1], [5, 5]]], ["strike", "d2", [[2, 2], [6, 6]]],
    ]);
  });

  it("draws a lost target's estimate and a blocked vehicle's way to the alternative", () => {
    const f = mkFrame({ vehicles: [mkVehicle({ id: "d2", pos: at(1, 1) })] });
    const tracks = { fast1: { k: "lost" as const, pos: at(2, 2), est: at(3, 3) } };
    const q = { action: [{ key: "b", cards: [mkCard({ id: "b", source: "block", vehicle: "d2", alternative: { lat: 4, lon: 4 } })] }],
      alerts: [], history: [] };
    expect(linkLines(f, tracks, q).features.map((x) => [x.properties.k, x.properties.v, x.geometry.coordinates])).toEqual([
      ["est", "fast1", [[2, 2], [3, 3]]], ["alt", "d2", [[1, 1], [4, 4]]],
    ]);
  });
});
