import { describe, expect, it } from "vitest";
import s1 from "../../../../../contracts/examples/frames/s1_report_wait.json";
import s3 from "../../../../../contracts/examples/frames/s3_takeover.json";
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
    expect(targets).toEqual([{ id: "boat1", kind: "boat", lon: 124.7, lat: 37.98437, seen: true }]);
  });

  it("marks a target nobody sees as not seen", () => {
    const f = s1 as Frame;
    const unseen = { ...f, targets: [{ ...f.targets[0], seen_by: [] }] };
    expect(frameMarkers(unseen).targets[0].seen).toBe(false);
  });
});
