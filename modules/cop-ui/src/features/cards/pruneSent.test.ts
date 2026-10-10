import { describe, expect, it } from "vitest";
import { pruneSent } from "./pruneSent";

describe("pruneSent", () => {
  const sent = { "rep-a": "dec-1", "rep-b": "dec-2" };

  it("keeps the same object when every sent report is still in the frame", () => {
    expect(pruneSent(sent, ["rep-a", "rep-b", "rep-c"], false)).toBe(sent);
  });
  it("forgets reports that left the frame (run reset before they happened)", () => {
    expect(pruneSent(sent, ["rep-b"], false)).toEqual({ "rep-b": "dec-2" });
  });
  it("forgets everything when time went backwards", () => {
    expect(pruneSent(sent, ["rep-a", "rep-b"], true)).toEqual({});
  });
});
