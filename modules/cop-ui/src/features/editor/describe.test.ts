import { describe, expect, it } from "vitest";
import { describeAction, describeCondition } from "./describe";

describe("describeAction", () => {
  it("counts route points", () => {
    const route = [{ lat: 37.98, lon: 124.66 }, { lat: 37.98, lon: 124.74 }];
    expect(describeAction({ kind: "patrol_route", params: { route } })).toBe("순찰 경로 2점");
  });
  it("names the target rule and distance", () => {
    expect(describeAction({ kind: "watch_target", params: { target: "nearest", distance_m: 150 } }))
      .toBe("표적 감시 · 가장 가까운 표적 · 150m 거리");
    expect(describeAction({ kind: "watch_target", params: { target: "operator" } })).toBe("표적 감시 · 운용자가 고름");
    expect(describeAction({ kind: "approach_target", params: { target: "fast1" } })).toBe("표적 접근 · fast1");
  });
  it("prints a GeoPoint destination", () => {
    expect(describeAction({ kind: "move_to", params: { target: { lat: 37.975, lon: 124.7, alt_m: 0 } } }))
      .toBe("이동 · 37.975, 124.700");
  });
  it("is just the label without params", () => {
    expect(describeAction({ kind: "hold" })).toBe("대기");
  });
});

describe("describeCondition", () => {
  it("labels target_found", () => {
    expect(describeCondition({ kind: "target_found", params: {} })).toBe("표적 발견");
  });
  it("reads battery_below pct", () => {
    expect(describeCondition({ kind: "battery_below", params: { pct: 30 } })).toBe("배터리 30% 미만");
  });
  it("appends unknown params as key value", () => {
    expect(describeCondition({ kind: "time_elapsed", params: { sec: 60 } })).toBe("시간 경과 sec 60");
  });
});
