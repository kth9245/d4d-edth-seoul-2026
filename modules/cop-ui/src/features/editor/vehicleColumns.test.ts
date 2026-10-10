import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { Operation, Play } from "../../contracts.gen";
import { reachablePlays, vehicleColumns } from "./vehicleColumns";

const op = scenario.operation as unknown as Operation;
const plays = scenario.plays as unknown as Play[];
const summary = (o: Operation, p: Play[]) =>
  vehicleColumns(o, p).map((c) => [c.vehicle_id, c.reserve_for, c.plays.map((x) => [x.play_id, x.via])]);

describe("vehicleColumns", () => {
  it("lists each vehicle's start play then the plays its report choices lead to", () => {
    expect(summary(op, plays)).toEqual([
      // demo starts on the coast patrol (user, 10/10); coast cards build their choices at run time
      ["d1", [], [["coast_a", null]]],
      ["d2", [], [["coast_b", null]]],
      ["d3", [], [["standby", null]]],
      ["d4", [], [["standby", null]]],
      ["usv", [], [["standby", null]]],
      ["ugv", [], [["standby", null]]],
    ]);
  });
  it("keeps switches out of the columns", () => {
    const all = vehicleColumns(op, plays).flatMap((c) => c.plays.map((x) => x.play_id));
    expect(all).not.toContain("go_home");
  });
  it("marks a missing play with play null", () => {
    const o = { ...op, vehicle_ids: ["d1"], assign: { d1: "ghost" } };
    expect(vehicleColumns(o, plays)[0].plays).toEqual([{ play_id: "ghost", play: null, via: null }]);
  });
  it("gives an empty column to a vehicle without assign", () => {
    const o = { ...op, vehicle_ids: ["x9"], assign: {}, reserve: {} };
    expect(vehicleColumns(o, plays)).toEqual([{ vehicle_id: "x9", reserve_for: [], plays: [] }]);
  });
});

describe("reachablePlays", () => {
  it("stops on a choice cycle", () => {
    const step = (to: string) => ({
      id: "s",
      name: "s",
      do: { kind: "hold" as const },
      report: { text: "t", choices: [{ id: "c", label: "c", play_by_vehicle: { v: to } }] },
    });
    const a = { id: "a", name: "A", domains: ["air" as const], entry: "s", steps: [step("b")] };
    const b = { id: "b", name: "B", domains: ["air" as const], entry: "s", steps: [step("a")] };
    const o = { ...op, vehicle_ids: ["v"], assign: { v: "a" } };
    expect(reachablePlays(o, [a, b]).map((p) => p.id)).toEqual(["a", "b"]);
    expect(vehicleColumns(o, [a, b])[0].plays.map((x) => x.play_id)).toEqual(["a", "b"]);
  });
});
