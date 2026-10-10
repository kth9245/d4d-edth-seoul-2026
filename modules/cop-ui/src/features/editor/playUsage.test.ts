import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { EnemySpec, Operation, Play } from "../../contracts.gen";
import { playUsage } from "./playUsage";

const op = scenario.operation as unknown as Operation;
const plays = scenario.plays as unknown as Play[];

describe("playUsage", () => {
  const u = playUsage(op, plays);
  it("names the operation start", () => {
    expect(u["coast_a"]).toContainEqual({ vehicle_id: "d1", how: "작전 시작" }); // coast patrol (user, 10/10)
    expect(u["standby"].map((x) => x.vehicle_id)).toEqual(["d3", "usv", "ugv", "d4"]);
  });
  it("names the play and choice that lead here", () => {
    expect(u["coast_b"]).toContainEqual({ vehicle_id: "d2", how: "작전 시작" });
    expect(u["watch"]).toEqual([{ vehicle_id: "d1", how: "해안 순찰 A의 '근접 확인' 뒤" }]); // patrol_a stays in the library
  });
  it("names the operation switch", () => {
    expect(u["go_home"]).toHaveLength(8); // all home 6 + d3·d4 by '전 기체 순찰' (coast pairs)
    expect(u["go_home"][0]).toEqual({ vehicle_id: "d1", how: "전체 전환 '전 기체 귀환'" });
  });
  it("has no entry for an unused play", () => {
    expect(u["enemy_boat1"]).toBeUndefined(); // enemy plays run on enemies, not on vehicles (decision 0032)
  });
  it("names the enemy that follows an enemy play and when it appears (Part1-21)", () => {
    const e = playUsage(op, plays, scenario.enemies as unknown as EnemySpec[]);
    expect(e["enemy_boat1"]).toEqual([{ vehicle_id: "boat1", how: "적 · 21:11 KST 등장 (+11분)" }]);
    expect(e["enemy_fast1"]).toEqual([{ vehicle_id: "fast1", how: "적 · 21:23 KST 등장 (+23분)" }]);
  });
});
