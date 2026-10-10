import { describe, expect, it } from "vitest";
import { SCENE_ZONE, SCENES } from "./sceneFrames";

describe("sceneFrames", () => {
  it("keys the six example scenes s1..s6", () => {
    expect(Object.keys(SCENES).sort()).toEqual(["s1", "s2", "s3", "s4", "s5", "s6"]);
  });
  it("holds the example Frame of each scene", () => {
    expect(SCENES.s1.vehicles).toHaveLength(5);
    expect(SCENES.s5.blocks[0].reason).toBe("outside_zone");
  });
  it("uses the example operation zone", () => {
    expect(SCENE_ZONE.points).toHaveLength(4);
  });
});
