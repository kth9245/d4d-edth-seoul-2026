import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { Operation, Play } from "../../contracts.gen";
import { playUsage } from "./playUsage";

const op = scenario.operation as unknown as Operation;
const plays = scenario.plays as unknown as Play[];

describe("playUsage", () => {
  const u = playUsage(op, plays);
  it("names the operation start", () => {
    expect(u["patrol_a"]).toEqual([{ vehicle_id: "d1", how: "작전 시작" }]);
    expect(u["standby"].map((x) => x.vehicle_id)).toEqual(["d2", "d3", "usv", "ugv"]);
  });
  it("names the play and choice that lead here", () => {
    expect(u["patrol_b"]).toEqual([{ vehicle_id: "d2", how: "해안 순찰 A의 '근접 확인' 뒤" }]);
  });
  it("names the operation switch", () => {
    expect(u["go_home"]).toHaveLength(5);
    expect(u["go_home"][0]).toEqual({ vehicle_id: "d1", how: "전체 전환 '전 기체 귀환'" });
  });
  it("has no entry for an unused play", () => {
    expect(u["track_fast"]).toBeUndefined();
  });
});
