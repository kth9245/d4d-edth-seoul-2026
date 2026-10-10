import { describe, expect, it } from "vitest";
import type { EnemySpec, Role, VehicleSpec } from "../../contracts.gen";
import { switchRoleOptions } from "./switchRoleOptions";

const role = (id: string, domains: Role["domains"]) => ({ id, name: `이름 ${id}`, domains }) as unknown as Role;
const roles = [role("patrol_a", ["air"]), role("approach", ["sea"]), role("go_home", ["air", "sea"]), role("enemy_boat1", ["sea"])];
const vehicles = [{ id: "d2", domain: "air" }, { id: "usv", domain: "sea" }] as VehicleSpec[];
const enemies = [{ id: "boat1", role_id: "enemy_boat1" }] as EnemySpec[];

describe("live board switch: roles offered for the picked vehicle (QA finding 2)", () => {
  it("a drone gets air roles, a boat sea roles, never an enemy's role", () => {
    expect(switchRoleOptions(roles, vehicles, enemies, "d2").map((o) => o.id)).toEqual(["patrol_a", "go_home"]);
    expect(switchRoleOptions(roles, vehicles, enemies, "usv").map((o) => o.id)).toEqual(["approach", "go_home"]);
  });
  it("no vehicle picked yet (or unknown) offers nothing", () => {
    expect(switchRoleOptions(roles, vehicles, enemies, "")).toEqual([]);
    expect(switchRoleOptions(roles, vehicles, enemies, "nope")).toEqual([]);
  });
});
