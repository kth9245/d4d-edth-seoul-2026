import { describe, expect, it } from "vitest";
import { tabFromHash } from "./tab";

describe("tabFromHash", () => {
  it("opens the editor only on #editor", () => {
    expect(tabFromHash("#editor")).toBe("editor");
    expect(tabFromHash("#live")).toBe("live");
    expect(tabFromHash("")).toBe("live");
  });
  it("opens the MAVLink log window on #mavlink (decision 0064)", () => {
    expect(tabFromHash("#mavlink")).toBe("mavlink");
  });
});
