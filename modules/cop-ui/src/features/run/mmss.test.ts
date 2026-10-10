import { describe, expect, it } from "vitest";
import { mmss } from "./mmss";

describe("mmss", () => {
  it("formats ms as minutes:seconds", () => {
    expect(mmss(0)).toBe("0:00");
    expect(mmss(198_000)).toBe("3:18");
    expect(mmss(16 * 60_000 + 15_000)).toBe("16:15");
  });
  it("drops the part below one second", () => {
    expect(mmss(59_999)).toBe("0:59");
  });
  it("keeps counting minutes past an hour", () => {
    expect(mmss(61 * 60_000)).toBe("61:00");
  });
  it("shows 0:00 for a negative span", () => {
    expect(mmss(-200)).toBe("0:00");
  });
});
