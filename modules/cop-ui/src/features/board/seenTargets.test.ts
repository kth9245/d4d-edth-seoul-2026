import { describe, expect, it } from "vitest";
import { at, mkTarget } from "./boardFixtures";
import { seenTargets } from "./seenTargets";
import type { Track } from "./trackState";

const tr = (k: Track["k"]): Track => ({ k, pos: at(37.96, 124.7) });

describe("seenTargets", () => {
  it("lists only what our sensors see now, most dangerous first, with the distance from the vehicle", () => {
    const targets = [
      mkTarget({ id: "boat1", threat: 50, pos: at(37.96, 124.7) }),
      mkTarget({ id: "fast1", kind: "fast_boat", threat: 100, pos: at(37.97, 124.7) }),
      mkTarget({ id: "boat2", threat: 72 }), mkTarget({ id: "boat3", threat: 90 }),
      mkTarget({ id: "gone1", threat: 99 }), mkTarget({ id: "never1", threat: 80 }),
    ];
    const tracks = { boat1: tr("seen"), fast1: tr("seen"), boat2: tr("lost"), boat3: tr("rf"), gone1: tr("gone"), never1: tr("never") };
    expect(seenTargets(targets, tracks, at(37.95, 124.7))).toEqual([
      { id: "fast1", kind: "고속정", threat: 100, distM: 2226 },
      { id: "boat1", kind: "보트", threat: 50, distM: 1113 },
    ]);
  });

  it("is empty when nothing is seen", () => {
    expect(seenTargets([mkTarget({ id: "boat1" })], { boat1: tr("lost") }, at(37.95, 124.7))).toEqual([]);
  });
});
