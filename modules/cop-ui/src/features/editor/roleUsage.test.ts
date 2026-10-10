import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { EnemySpec, Operation, Role } from "../../contracts.gen";
import { roleUsage } from "./roleUsage";

const op = scenario.operation as unknown as Operation;
const roles = scenario.roles as unknown as Role[];

describe("roleUsage", () => {
  const u = roleUsage(op, roles);
  it("names the operation start", () => {
    expect(u["patrol_a"]).toEqual([{ vehicle_id: "d1", how: "작전 시작" }]);
    expect(u["standby"].map((x) => x.vehicle_id)).toEqual(["d3", "usv", "ugv", "d4"]);
  });
  it("names the role and choice that lead here", () => {
    expect(u["watch"]).toEqual([{ vehicle_id: "d1", how: "해안 순찰 A의 '근접 확인' 뒤" }]);
    expect(u["patrol_b"]).toEqual([{ vehicle_id: "d2", how: "작전 시작" }]); // decision 0036
  });
  it("names the operation switch", () => {
    expect(u["go_home"]).toHaveLength(6); // all home 6 ('전 기체 순찰' left the data, decision 0060)
    expect(u["go_home"][0]).toEqual({ vehicle_id: "d1", how: "전체 전환 '전 기체 귀환'" });
  });
  it("has no entry for an unused role", () => {
    expect(u["enemy_boat1"]).toBeUndefined(); // enemy roles run on enemies, not on vehicles (decision 0032)
  });
  it("names the enemy that follows an enemy role and when it appears (Part1-21)", () => {
    const e = roleUsage(op, roles, scenario.enemies as unknown as EnemySpec[]);
    expect(e["enemy_boat1"]).toEqual([{ vehicle_id: "boat1", how: "적 · 21:11 KST 등장 (+11분)" }]);
    expect(e["enemy_fast1"]).toEqual([{ vehicle_id: "fast1", how: "적 · 21:23 KST 등장 (+23분)" }]);
  });
});
