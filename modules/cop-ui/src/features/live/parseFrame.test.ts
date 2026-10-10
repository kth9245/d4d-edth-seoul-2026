import { describe, expect, it } from "vitest";
import frame from "../../../../../contracts/examples/frame.json";
import legacy from "../../../../../contracts/examples/legacy_frame.json";
import { parseFrame } from "./parseFrame";

describe("parseFrame", () => {
  it("reads a Frame message", () => {
    const f = parseFrame(JSON.stringify(frame));
    expect(f?.vehicles).toHaveLength(6); // + d4 (coast pairs)
    expect(f?.t_ms).toBe(frame.t_ms);
  });

  it("drops a LegacyFrame from the old gateway", () => {
    expect(parseFrame(JSON.stringify(legacy))).toBeNull();
  });

  it("drops broken or non-object messages", () => {
    expect(parseFrame("{not json")).toBeNull();
    expect(parseFrame("null")).toBeNull();
    expect(parseFrame("3")).toBeNull();
  });
});
