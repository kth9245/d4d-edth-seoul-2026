import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { Operation, Role } from "../../contracts.gen";
import { reachableRoles, vehicleColumns } from "./vehicleColumns";

const op = scenario.operation as unknown as Operation;
const roles = scenario.roles as unknown as Role[];
const summary = (o: Operation, p: Role[]) =>
  vehicleColumns(o, p).map((c) => [c.vehicle_id, c.reserve_for, c.roles.map((x) => [x.role_id, x.via])]);

describe("vehicleColumns", () => {
  it("lists each vehicle's start role then the roles its report choices lead to", () => {
    expect(summary(op, roles)).toEqual([
      ["d1", [], [["patrol_a", null], ["watch", "근접 확인"]]],
      ["d2", [], [["patrol_b", null]]], // decision 0036: d2 patrols from the start
      ["d3", ["d1"], [["standby", null]]],
      ["d4", [], [["standby", null]]], // coast pair partner of d2
      ["usv", [], [["standby", null], ["approach", "근접 확인"]]],
      ["ugv", [], [["standby", null], ["landing", "근접 확인"]]],
    ]);
  });
  it("keeps switches out of the columns", () => {
    const all = vehicleColumns(op, roles).flatMap((c) => c.roles.map((x) => x.role_id));
    expect(all).not.toContain("go_home");
  });
  it("marks a missing role with role null", () => {
    const o = { ...op, vehicle_ids: ["d1"], assign: { d1: "ghost" } };
    expect(vehicleColumns(o, roles)[0].roles).toEqual([{ role_id: "ghost", role: null, via: null }]);
  });
  it("gives an empty column to a vehicle without assign", () => {
    const o = { ...op, vehicle_ids: ["x9"], assign: {}, reserve: {} };
    expect(vehicleColumns(o, roles)).toEqual([{ vehicle_id: "x9", reserve_for: [], roles: [] }]);
  });
});

describe("reachableRoles", () => {
  it("stops on a choice cycle", () => {
    const step = (to: string) => ({
      id: "s",
      name: "s",
      do: { kind: "hold" as const },
      report: { text: "t", choices: [{ id: "c", label: "c", role_by_vehicle: { v: to } }] },
    });
    const a = { id: "a", name: "A", domains: ["air" as const], entry: "s", steps: [step("b")] };
    const b = { id: "b", name: "B", domains: ["air" as const], entry: "s", steps: [step("a")] };
    const o = { ...op, vehicle_ids: ["v"], assign: { v: "a" } };
    expect(reachableRoles(o, [a, b]).map((p) => p.id)).toEqual(["a", "b"]);
    expect(vehicleColumns(o, [a, b])[0].roles.map((x) => x.role_id)).toEqual(["a", "b"]);
  });
});
