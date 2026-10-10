import { describe, expect, it } from "vitest";
import { tabFromHash } from "./tab";

describe("tabFromHash", () => {
  it("opens the editor on #editor, 실작전 on #ops, the simulation otherwise", () => {
    expect(tabFromHash("#editor")).toBe("editor");
    expect(tabFromHash("#ops")).toBe("ops");
    expect(tabFromHash("#live")).toBe("live");
    expect(tabFromHash("")).toBe("live");
  });
});
