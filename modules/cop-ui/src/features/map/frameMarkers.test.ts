import { describe, expect, it } from "vitest";
import s1 from "../../../../../contracts/examples/frames/s1_report_wait.json";
import s3 from "../../../../../contracts/examples/frames/s3_takeover.json";
import s8 from "../../../../../contracts/examples/frames/s8_neutralized.json";
import type { Frame } from "../../contracts.gen";
import { frameMarkers } from "./frameMarkers";

describe("frameMarkers", () => {
  it("makes one marker per vehicle with its position and status", () => {
    const { vehicles } = frameMarkers(s1 as Frame);
    expect(vehicles.map((v) => v.id)).toEqual(["d1", "d2", "d3", "usv", "ugv"]);
    expect(vehicles[0]).toEqual({ id: "d1", lon: 124.695, lat: 37.98, status: "active" });
    expect(vehicles[1].status).toBe("ready");
  });

  it("follows the vehicle status between frames", () => {
    expect(frameMarkers(s3 as Frame).vehicles[0].status).toBe("returning");
  });

  it("makes one marker per target, seen when some vehicle sees it", () => {
    const { targets } = frameMarkers(s1 as Frame);
    expect(targets).toEqual([
      { id: "boat1", kind: "boat", lon: 124.7, lat: 37.98437, seen: true, neutralized: false, rf: false, label: "boat1" },
    ]);
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
