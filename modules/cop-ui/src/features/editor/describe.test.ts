import { describe, expect, it } from "vitest";
import { describeAction, describeCondition } from "./describe";

describe("describeAction", () => {
  it("names the route, whether it repeats and whether it is relative", () => {
    expect(describeAction({ kind: "patrol_route", params: { route: [], route_name: "해안 A(북)" } })).toBe("경로 비행 · 해안 A(북) · 반복");
    expect(describeAction({ kind: "move_to", params: { offsets: [{ north_m: 1, east_m: 0 }], route_name: "북쪽으로 1km" } }))
      .toBe("경로 비행 · 북쪽으로 1km · 한 번 · 기체 위치 기준");
    expect(describeCondition({ kind: "at_time", params: { offset_ms: 90_000 } })).toBe("T+1:30");
  });
  it("counts route points", () => {
    const route = [{ lat: 37.98, lon: 124.66 }, { lat: 37.98, lon: 124.74 }];
    expect(describeAction({ kind: "patrol_route", params: { route } })).toBe("경로 비행 · 경로 2곳 · 반복");
  });
  it("names the target rule and distance", () => {
    expect(describeAction({ kind: "watch_target", params: { target: "nearest", distance_m: 150 } }))
      .toBe("표적 감시 · 가장 가까운 표적 · 150m 거리");
    expect(describeAction({ kind: "watch_target", params: { target: "operator" } })).toBe("표적 감시 · 운용자가 고름");
    expect(describeAction({ kind: "approach_target", params: { target: "fast1" } })).toBe("표적 접근 · fast1");
  });
  it("prints a GeoPoint destination", () => {
    expect(describeAction({ kind: "move_to", params: { target: { lat: 37.975, lon: 124.7, alt_m: 0 } } }))
      .toBe("경로 비행 · 37.975, 124.700 · 한 번");
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
