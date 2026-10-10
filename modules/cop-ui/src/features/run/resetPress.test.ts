import { describe, expect, it } from "vitest";
import { RESET_WINDOW_MS, resetPress } from "./resetPress";

describe("resetPress", () => {
  it("first press only arms", () => {
    expect(resetPress(null, 1000)).toBe("arm");
  });
  it("second press within the window resets", () => {
    expect(resetPress(1000, 1000 + RESET_WINDOW_MS)).toBe("fire");
  });
  it("a press after the window arms again", () => {
    expect(resetPress(1000, 1001 + RESET_WINDOW_MS)).toBe("arm");
  });
});
