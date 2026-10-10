import { describe, expect, it } from "vitest";
import { at } from "./boardFixtures";
import { pointRoles } from "./pointRoles";
import type { Track } from "./trackState";

const ROLES = [{ id: "approach", name: "근접 확인", strike: false }, { id: "strike", name: "표적 타격", strike: true }];
const tr = (k: Track["k"]): Track => ({ k, pos: at(37.96, 124.7) });

describe("pointRoles", () => {
  it("keeps strike for a target our sensors see now", () => {
    expect(pointRoles(ROLES, tr("seen")).map((r) => r.id)).toEqual(["approach", "strike"]);
  });

  it("drops strike for a lost, RF-only, never-seen or unknown target; the other target roles stay", () => {
    for (const t of [tr("lost"), tr("rf"), tr("never"), undefined]) {
      expect(pointRoles(ROLES, t).map((r) => r.id)).toEqual(["approach"]);
    }
  });
});
