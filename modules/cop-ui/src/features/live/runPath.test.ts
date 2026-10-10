import { describe, expect, it } from "vitest";
import { runPath } from "./runPath";

describe("runPath", () => {
  it("adds run=ops on 실작전 only (decision 0068)", () => {
    expect(runPath("/decisions", false)).toBe("/decisions");
    expect(runPath("/decisions", true)).toBe("/decisions?run=ops");
    expect(runPath("/graph?focus=boat1", true)).toBe("/graph?focus=boat1&run=ops");
    expect(runPath("ws://h/ws", true)).toBe("ws://h/ws?run=ops");
  });
});
