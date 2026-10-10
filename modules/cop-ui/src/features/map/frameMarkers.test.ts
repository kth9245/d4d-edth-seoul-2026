import { describe, expect, it } from "vitest";
import s1 from "../../../../../contracts/examples/frames/s1_report_wait.json";
import s3 from "../../../../../contracts/examples/frames/s3_takeover.json";
import s8 from "../../../../../contracts/examples/frames/s8_neutralized.json";
import type { Frame } from "../../contracts.gen";
import { frameMarkers } from "./frameMarkers";

describe("frameMarkers", () => {
  it("makes one marker per vehicle with its position and status", () => {
    const { vehicles } = frameMarkers(s1 as Frame);
    expect(vehicles.map((v) => v.id)).toEqual(["d1", "d2", "d3", "usv", "ugv", "d4"]); // d4 waits at base in the example scene
    expect(vehicles[0]).toMatchObject({ id: "d1", lon: 124.695, lat: 37.98, status: "active" });
    expect(vehicles[1].status).toBe("ready");
  });

  it("shows the battery right of each vehicle: a 4-block bar and the percent, coloured by level (user, 10/10)", () => {
    const f = s1 as Frame;
    const at = (pct: number) => frameMarkers({ ...f, vehicles: [{ ...f.vehicles[0], battery_pct: pct }] }).vehicles[0];
    expect([at(78.4).label, at(78.4).battery]).toEqual(["d1 ▮▮▮▮ 78%", "ok"]);
    expect([at(50).label, at(50).battery]).toEqual(["d1 ▮▮▯▯ 50%", "mid"]);
    expect([at(30).label, at(30).battery]).toEqual(["d1 ▮▮▯▯ 30%", "low"]);
    expect([at(0).label, at(100).label]).toEqual(["d1 ▯▯▯▯ 0%", "d1 ▮▮▮▮ 100%"]);
  });

  it("follows the vehicle status between frames", () => {
    expect(frameMarkers(s3 as Frame).vehicles[0].status).toBe("returning");
  });

  it("makes one marker per target, seen when some vehicle sees it", () => {
    const { targets } = frameMarkers(s1 as Frame);
    expect(targets).toEqual([
      { id: "boat1", kind: "boat", lon: 124.7, lat: 37.98437, seen: true, neutralized: false, rf: false, label: "boat1",
        track: "seen", tone: "lo" },
    ]);
  });

  it("draws a target where our side knows it and says its risk, lost time and direction (decision 0047)", () => {
    const f = s1 as Frame;
    const t = { ...f.targets[0], threat: 72, seen_by: [], first_seen_ms: f.t_ms - 60_000, last_seen_ms: f.t_ms - 20_000 };
    const tracks = { boat1: { k: "lost" as const, pos: { lat: 37.98, lon: 124.71 }, agoMs: 20_000, dir: "away" as const, speed: 6.3 } };
    expect(frameMarkers({ ...f, targets: [t] }, tracks).targets[0]).toMatchObject({
      lon: 124.71, lat: 37.98, track: "lost", tone: "hi", label: "boat1 0.72 · 놓침 0:20 · 이탈(도주) 추정",
    });
    const never = { boat1: { k: "never" as const, pos: t.pos } };
    expect(frameMarkers({ ...f, targets: [t] }, never).targets[0]).toMatchObject({ track: "never", label: "boat1 · 미탐" });
    const seen = { boat1: { k: "seen" as const, pos: t.pos } };
    expect(frameMarkers({ ...f, targets: [{ ...t, seen_by: ["d1"], rf_detected: true }] }, seen).targets[0].label).toBe("boat1 0.72 · RF");
  });

  it("marks a target whose emission our vehicles picked up with RF, never by the truth emitting (decision 0040)", () => {
    const f = s1 as Frame;
    const at = (t: object) => frameMarkers({ ...f, targets: [{ ...f.targets[0], ...t }] }).targets[0];
    expect([at({ rf_detected: true }).rf, at({ rf_detected: true }).label]).toEqual([true, "boat1 · RF"]);
    expect([at({ emitting: true }).rf, at({ emitting: true }).label]).toEqual([false, "boat1"]);
    expect(at({ rf_detected: true, neutralized_ms: 1 }).label).toBe("boat1 · 무력화");
  });

  it("marks a target nobody sees as not seen", () => {
    const f = s1 as Frame;
    const unseen = { ...f, targets: [{ ...f.targets[0], seen_by: [] }] };
    expect(frameMarkers(unseen).targets[0].seen).toBe(false);
  });

  it("marks a struck target neutralized and says so in its label", () => {
    const { targets } = frameMarkers(s8 as Frame);
    expect(targets.find((t) => t.id === "fast1")).toMatchObject({ neutralized: true, label: "fast1 · 무력화" });
    expect(targets.find((t) => t.id === "boat1")).toMatchObject({ neutralized: false, label: "boat1" });
  });
});
