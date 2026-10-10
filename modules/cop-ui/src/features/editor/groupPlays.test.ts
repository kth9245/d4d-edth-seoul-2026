import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { Play } from "../../contracts.gen";
import { groupPlays } from "./groupPlays";

const plays = scenario.plays as unknown as Play[];
const ids = (g: { plays: Play[] }) => g.plays.map((p) => p.id);

describe("groupPlays", () => {
  it("groups the scenario plays by single domain, multi-domain into common", () => {
    const groups = groupPlays(plays);
    expect(groups.map((g) => [g.label, ids(g)])).toEqual([
      ["드론", ["patrol_a", "watch", "patrol_b", "track_fast"]],
      ["수상정", ["approach", "track_fast_sea", "enemy_boat1", "enemy_fast1"]],
      ["지상", ["landing"]],
      ["공통", ["standby", "go_home", "strike"]],
    ]);
  });
  it("moves the plays enemies follow into a last group of their own (Part1-21)", () => {
    const groups = groupPlays(plays, ["enemy_boat1", "enemy_fast1"]);
    expect(groups.map((g) => [g.label, ids(g)])).toEqual([
      ["드론", ["patrol_a", "watch", "patrol_b", "track_fast"]],
      ["수상정", ["approach", "track_fast_sea"]],
      ["지상", ["landing"]],
      ["공통", ["standby", "go_home", "strike"]],
      ["적", ["enemy_boat1", "enemy_fast1"]],
    ]);
  });
  it("puts a play without domains into common and drops empty groups", () => {
    const bare = { ...plays[0], id: "bare", domains: [] } as Play;
    expect(groupPlays([bare]).map((g) => [g.key, ids(g)])).toEqual([["common", ["bare"]]]);
  });
});
