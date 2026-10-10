import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { Role } from "../../contracts.gen";
import { groupRoles } from "./groupRoles";

const roles = scenario.roles as unknown as Role[];
const ids = (g: { roles: Role[] }) => g.roles.map((p) => p.id);

describe("groupRoles", () => {
  it("groups the scenario roles by single domain, multi-domain into common", () => {
    const groups = groupRoles(roles);
    expect(groups.map((g) => [g.label, ids(g)])).toEqual([
      ["드론", ["patrol_a", "watch", "patrol_b", "track_fast", "coast_a", "coast_b"]],
      ["수상정", ["approach", "track_fast_sea", "enemy_boat1", "enemy_fast1", "enemy_boat2", "enemy_boat3"]],
      ["지상", ["landing"]],
      ["공통", ["standby", "go_home", "strike"]],
    ]);
  });
  it("moves the roles enemies follow into a last group of their own (Part1-21)", () => {
    const groups = groupRoles(roles, ["enemy_boat1", "enemy_fast1", "enemy_boat2", "enemy_boat3"]);
    expect(groups.map((g) => [g.label, ids(g)])).toEqual([
      ["드론", ["patrol_a", "watch", "patrol_b", "track_fast", "coast_a", "coast_b"]],
      ["수상정", ["approach", "track_fast_sea"]],
      ["지상", ["landing"]],
      ["공통", ["standby", "go_home", "strike"]],
      ["적", ["enemy_boat1", "enemy_fast1", "enemy_boat2", "enemy_boat3"]], // decision 0036
    ]);
  });
  it("puts a role without domains into common and drops empty groups", () => {
    const bare = { ...roles[0], id: "bare", domains: [] } as Role;
    expect(groupRoles([bare]).map((g) => [g.key, ids(g)])).toEqual([["common", ["bare"]]]);
  });
});
