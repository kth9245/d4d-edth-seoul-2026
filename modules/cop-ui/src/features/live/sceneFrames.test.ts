import { describe, expect, it } from "vitest";
import { SCENE_ZONE, SCENES } from "./sceneFrames";

describe("sceneFrames", () => {
  it("keys the eight example scenes s1..s8", () => {
    expect(Object.keys(SCENES).sort()).toEqual(["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8"]);
  });
  it("holds the example Frame of each scene", () => {
    expect(SCENES.s1.vehicles).toHaveLength(6); // + d4 (coast pairs)
    expect(SCENES.s5.blocks[0].reason).toBe("outside_zone");
  });
  it("puts the blocks of patrolling d2 before the fast boat (strike-phase order)", () => {
    expect(SCENES.s5.vehicles.find((v) => v.id === "d2")!.role_id).toBe("patrol_b");
    expect(SCENES.s6.t_ms).toBeLessThan(SCENES.s4.t_ms);
  });
  it("opens a strike approval card per tracker in s7 and neutralizes fast1 in s8", () => {
    const open = SCENES.s7.reports.filter((r) => r.text.startsWith("타격 승인 요청") && r.resolved_ms == null);
    expect(open.map((r) => r.vehicle_id)).toEqual(["d2", "usv"]);
    expect(SCENES.s8.targets.find((t) => t.id === "fast1")!.neutralized_ms).toBeTypeOf("number");
  });
  it("uses the example operation zone", () => {
    expect(SCENE_ZONE.points).toHaveLength(4);
  });
});
