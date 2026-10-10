import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { Operation, VehicleSpec } from "../../contracts.gen";
import { startText, switchRows, vehicleRows } from "./operationPanel";

const op = scenario.operation as unknown as Operation;
const vehicles = scenario.vehicles as unknown as VehicleSpec[];
const names = new Map(scenario.roles.map((p) => [p.id, p.name]));
const roleName = (id: string) => names.get(id) ?? null;

describe("vehicleRows", () => {
  it("lists the operation's vehicles in order with kind, first role and reserves", () => {
    const rows = vehicleRows(op, vehicles, roleName);
    expect(rows.map((r) => r.id)).toEqual(["d1", "d2", "d3", "d4", "usv", "ugv"]);
    expect(rows[0]).toEqual({ id: "d1", name: "드론1", domain: "드론", roleId: "patrol_a", roleName: "해안 순찰 A", reserves: ["d3"] });
    expect(rows[4]).toMatchObject({ id: "usv", domain: "수상정", roleName: "대기", reserves: [] });
  });
  it("still shows a vehicle the gateway has no spec for", () => {
    expect(vehicleRows(op, [], roleName)[0]).toMatchObject({ id: "d1", name: "d1", domain: "" });
  });
});

describe("switchRows", () => {
  it("spells out which vehicle each switch button sends to which role", () => {
    const [all] = switchRows(op, roleName);
    expect(all.label).toBe("전 기체 귀환");
    expect(all.moves[0]).toEqual({ vehicle: "d1", roleId: "go_home", roleName: "귀환" });
    expect(all.moves).toHaveLength(6); // + d4 (coast pairs)
  });
});

describe("startText", () => {
  it("shows the start in KST", () => {
    expect(startText(op.started_ms)).toBe("21:00 KST");
  });
  it("says when there is no start time", () => {
    expect(startText(null)).toBe("시작 시각 없음");
  });
});
