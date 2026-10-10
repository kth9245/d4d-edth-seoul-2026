import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { Operation, VehicleSpec } from "../../contracts.gen";
import { startText, switchRows, vehicleRows } from "./operationPanel";

const op = scenario.operation as unknown as Operation;
const vehicles = scenario.vehicles as unknown as VehicleSpec[];
const names = new Map(scenario.plays.map((p) => [p.id, p.name]));
const playName = (id: string) => names.get(id) ?? null;

describe("vehicleRows", () => {
  it("lists the operation's vehicles in order with kind, first play and reserves", () => {
    const rows = vehicleRows(op, vehicles, playName);
    expect(rows.map((r) => r.id)).toEqual(["d1", "d2", "d3", "d4", "usv", "ugv"]);
    expect(rows[0]).toEqual({ id: "d1", name: "드론1", domain: "드론", playId: "coast_a", playName: "해안 순찰 A · 북", reserves: [] });
    expect(rows[4]).toMatchObject({ id: "usv", domain: "수상정", playName: "대기", reserves: [] });
  });
  it("still shows a vehicle the gateway has no spec for", () => {
    expect(vehicleRows(op, [], playName)[0]).toMatchObject({ id: "d1", name: "d1", domain: "" });
  });
});

describe("switchRows", () => {
  it("spells out which vehicle each switch button sends to which play", () => {
    const [all] = switchRows(op, playName);
    expect(all.label).toBe("전 기체 귀환");
    expect(all.moves[0]).toEqual({ vehicle: "d1", playId: "go_home", playName: "귀환" });
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
