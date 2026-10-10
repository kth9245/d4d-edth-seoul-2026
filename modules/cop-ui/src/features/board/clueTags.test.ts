import { describe, expect, it } from "vitest";
import { clueTags } from "./clueTags";

describe("clueTags", () => {
  it("names each clue our sensors picked up, RF first (decision 0071)", () => {
    expect(clueTags({})).toEqual([]);
    expect(clueTags({ rf_detected: true })).toEqual(["RF"]);
    expect(clueTags({ sound_detected: true })).toEqual(["소음"]);
    expect(clueTags({ rf_detected: true, ir_detected: true, sound_detected: true })).toEqual(["RF", "열", "소음"]);
  });
});
