import { describe, expect, it } from "vitest";
import { at, mkTarget, T0 } from "./boardFixtures";
import { trackState } from "./trackState";

const LANDING = at(37.978, 124.7);
const lostAt = (p: object) => mkTarget({ id: "fast1", first_seen_ms: T0 - 60_000, last_seen_ms: T0 - 20_000,
  pos: at(37.99, 124.76), last_seen_pos: at(37.987, 124.745), ...p });

describe("trackState", () => {
  it("says seen, RF only, never detected or struck from what our side knows", () => {
    expect(trackState(mkTarget({ id: "a", seen_by: ["d1"], first_seen_ms: T0 }), T0, LANDING).k).toBe("seen");
    expect(trackState(mkTarget({ id: "b", rf_detected: true }), T0, LANDING).k).toBe("rf");
    expect(trackState(mkTarget({ id: "c" }), T0, LANDING)).toEqual({ k: "never", pos: at(37.99, 124.72) });
    expect(trackState(mkTarget({ id: "d", neutralized_ms: T0, seen_by: ["usv"] }), T0, LANDING).k).toBe("gone");
  });

  it("draws a lost target where it was last seen, still when it was not moving", () => {
    expect(trackState(lostAt({}), T0, LANDING)).toEqual({ k: "lost", pos: at(37.987, 124.745), agoMs: 20_000, dir: "still", speed: 0 });
  });

  it("estimates where a moving lost target is now and whether it heads to the landing point", () => {
    const away = trackState(lostAt({ last_seen_vel_east_mps: 6.3 }), T0, LANDING); // landing is west
    expect([away.k, away.dir, away.agoMs]).toEqual(["lost", "away", 20_000]);
    expect(away.est!.lat).toBeCloseTo(37.987, 6);
    expect(away.est!.lon).toBeCloseTo(124.745 + (6.3 * 20) / (111_320 * Math.cos((37.987 * Math.PI) / 180)), 6);
    expect(trackState(lostAt({ last_seen_vel_east_mps: -6.3 }), T0, LANDING).dir).toBe("approach");
  });

  it("assumes a moving lost target approaches when there is no landing point", () => {
    expect(trackState(lostAt({ last_seen_vel_east_mps: 6.3 }), T0, null).dir).toBe("approach");
  });

  it("falls back to the true position while the gateway does not send the last seen spot yet", () => {
    expect(trackState(lostAt({ last_seen_pos: null }), T0, LANDING).pos).toEqual(at(37.99, 124.76));
  });
});
