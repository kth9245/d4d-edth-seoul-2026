import { describe, expect, it } from "vitest";
import type { ActionKind, Domain, Role, VehicleSpec } from "../../contracts.gen";
import { vehicleMenuRoles } from "./vehicleMenuRoles";

const step = (id: string, kind: ActionKind, target?: string) => ({ id, name: id, do: { kind, params: target ? { target } : {} } });
const role = (id: string, domains: Domain[], ...steps: ReturnType<typeof step>[]): Role =>
  ({ id, name: `${id}名`, domains, entry: steps[0].id, steps });
// The night operation's roles in small (demo/scenarios/baengnyeong_night.json)
const ROLES = [
  role("standby", ["air", "sea", "ground"], step("w", "hold")),
  role("go_home", ["air", "sea", "ground"], step("r", "return_home")),
  role("patrol_a", ["air"], step("p", "patrol_route"), step("rep", "watch_target", "nearest")),
  role("watch", ["air"], step("w", "watch_target", "operator")),
  role("track_fast", ["air"], step("t", "watch_target", "operator")),
  role("approach", ["sea"], step("a", "approach_target", "operator")),
  role("strike", ["air", "sea"], step("s", "strike_target", "operator")),
  role("landing", ["ground"], step("m", "move_to")),
  role("enemy_boat1", ["sea"], step("m", "move_to")),
];
const AIR: ActionKind[] = ["approach_target", "hold", "move_to", "patrol_route", "return_home", "watch_target"];
const spec = (id: string, domain: Domain, capabilities?: ActionKind[]) => ({ id, domain, capabilities }) as VehicleSpec;
const ids = (xs: { id: string }[]) => xs.map((x) => x.id);

describe("vehicleMenuRoles", () => {
  it("gives the armed drone its air roles, target roles last, strike marked", () => {
    const m = vehicleMenuRoles(ROLES, spec("d2", "air", [...AIR, "strike_target"]), ["enemy_boat1"], null);
    expect(ids(m.plain)).toEqual(["standby", "go_home", "patrol_a"]);
    expect(m.target).toEqual([{ id: "watch", name: "watch名", strike: false },
      { id: "track_fast", name: "track_fast名", strike: false }, { id: "strike", name: "strike名", strike: true }]);
  });

  it("gives a recon drone d1 no strike: it cannot do strike_target", () => {
    expect(ids(vehicleMenuRoles(ROLES, spec("d1", "air", AIR), ["enemy_boat1"], null).target)).toEqual(["watch", "track_fast"]);
  });

  it("gives the usv sea roles only and never an enemy's role", () => {
    const m = vehicleMenuRoles(ROLES, spec("usv", "sea", [...AIR, "strike_target"]), ["enemy_boat1"], null);
    expect(ids(m.plain)).toEqual(["standby", "go_home"]);
    expect(ids(m.target)).toEqual(["approach", "strike"]);
  });

  it("leaves out the role it runs now from the target-less list, keeps it among target roles", () => {
    const m = vehicleMenuRoles(ROLES, spec("d2", "air", [...AIR, "strike_target"]), [], "patrol_a");
    expect(ids(m.plain)).toEqual(["standby", "go_home"]);
    expect(ids(vehicleMenuRoles(ROLES, spec("d2", "air", [...AIR, "strike_target"]), [], "watch").target))
      .toEqual(["watch", "track_fast", "strike"]);
  });

  it("drops a role with a step the vehicle cannot do (ground robot cannot watch a target)", () => {
    const m = vehicleMenuRoles(ROLES, spec("ugv", "ground", ["hold", "move_to", "patrol_route", "return_home", "watch_point"]), [], null);
    expect(ids(m.plain)).toEqual(["standby", "go_home", "landing"]);
    expect(m.target).toEqual([]);
  });

  it("treats a patrol around the target's spot (anchor target, 24h focus_orbit) as a target role", () => {
    // a target-less switch would clear target_id and the drone would circle its own position (decision 0055)
    const orbit: Role = { id: "focus_orbit", name: "발견 지점 집중 순찰", domains: ["air"], entry: "s",
      steps: [{ id: "s", name: "s", do: { kind: "patrol_route", params: { offsets: [], anchor: "target" } } }] };
    const m = vehicleMenuRoles([...ROLES, orbit], spec("d1", "air", AIR), [], null);
    expect(ids(m.target)).toEqual(["watch", "track_fast", "focus_orbit"]);
    expect(ids(m.plain)).not.toContain("focus_orbit");
  });

  it("skips the capability rule when the operation has no ontology (no capabilities)", () => {
    expect(ids(vehicleMenuRoles(ROLES, spec("x", "air"), [], null).target)).toEqual(["watch", "track_fast", "strike"]);
  });
});
