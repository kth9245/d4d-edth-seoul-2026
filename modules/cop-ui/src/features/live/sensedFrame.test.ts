import { describe, expect, it } from "vitest";
import { at, mkFrame, mkTarget, mkVehicle } from "../board/boardFixtures";
import { sensedFrame } from "./sensedFrame";

describe("sensedFrame", () => {
  it("drops only the enemies no sensor has ever detected (decision 0067)", () => {
    const f = mkFrame({ targets: [
      mkTarget({ id: "seen1", first_seen_ms: 1, seen_by: ["d1"] }),
      mkTarget({ id: "rf1", rf_detected: true }),
      mkTarget({ id: "lost1", first_seen_ms: 1, last_seen_ms: 1, last_seen_pos: at(37.99, 124.72) }),
      mkTarget({ id: "gone1", first_seen_ms: 1, neutralized_ms: 5 }),
      mkTarget({ id: "never1" }),
    ] });
    expect(sensedFrame(f).targets.map((t) => t.id)).toEqual(["seen1", "rf1", "lost1", "gone1"]);
  });

  it("keeps the rest of the Frame and leaves the input alone", () => {
    const f = mkFrame({ targets: [mkTarget({ id: "never1" })], vehicles: [mkVehicle({ id: "d1" })] });
    const out = sensedFrame(f);
    expect(out.vehicles).toBe(f.vehicles);
    expect(out.t_ms).toBe(f.t_ms);
    expect(out.targets).toEqual([]);
    expect(f.targets).toHaveLength(1);
  });
});
