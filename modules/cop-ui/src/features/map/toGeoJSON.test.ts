import { describe, expect, it } from "vitest";
import frame from "../../../../../contracts/examples/frame.json";
import type { Frame } from "../../contracts.gen";
import { toGeoJSON } from "./toGeoJSON";

describe("toGeoJSON", () => {
  it("makes one point per track with assessment and response props", () => {
    const fc = toGeoJSON(frame as Frame);
    expect(fc.features).toHaveLength(1);
    const f = fc.features[0];
    expect(f.geometry.coordinates).toEqual([126.978, 37.5665]);
    expect(f.properties).toEqual({ id: "T-D-1", cls: "drone", threat: 0.82, response: "soft_kill" });
  });

  it("defaults when assessment or response is missing", () => {
    const fc = toGeoJSON({ ...(frame as Frame), assessments: [], responses: [] });
    expect(fc.features[0].properties).toMatchObject({ cls: "unknown", threat: 0, response: "observe" });
  });
});
