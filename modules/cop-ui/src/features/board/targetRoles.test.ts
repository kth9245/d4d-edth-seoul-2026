import { describe, expect, it } from "vitest";
import type { ActionKind, Domain, Role } from "../../contracts.gen";
import { targetRoles } from "./targetRoles";

const role = (id: string, kind: ActionKind, domains: Domain[]): Role =>
  ({ id, name: id, domains, entry: "s", steps: [{ id: "s", name: "s", do: { kind } }] });
const ROLES = [role("watch", "watch_target", ["air"]), role("track_fast", "watch_target", ["air"]),
  role("approach", "approach_target", ["sea"]), role("strike", "strike_target", ["air", "sea"]),
  role("patrol_a", "patrol_route", ["air"])];

describe("targetRoles", () => {
  it("offers the roles whose first step works a target and that the vehicle's domain runs, never strike", () => {
    expect(targetRoles(ROLES, "air").map((p) => p.id)).toEqual(["watch", "track_fast"]);
    expect(targetRoles(ROLES, "sea").map((p) => p.id)).toEqual(["approach"]);
    expect(targetRoles(ROLES, "ground")).toEqual([]);
  });
});
