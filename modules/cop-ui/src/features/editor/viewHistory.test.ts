import { describe, expect, it } from "vitest";
import { backFrom, openView } from "./viewHistory";

describe("viewHistory", () => {
  it("remembers where you came from when you open another view", () => {
    expect(openView({ current: "overview", stack: [] }, "patrol_a")).toEqual({ current: "patrol_a", stack: ["overview"] });
  });
  it("does not record opening the view you are already on", () => {
    const h = { current: "patrol_a", stack: ["overview"] };
    expect(openView(h, "patrol_a")).toBe(h);
  });
  it("goes back to the last view, then to the one before", () => {
    const h = openView(openView({ current: "overview", stack: [] }, "patrol_a"), "patrol_b");
    const once = backFrom(h, "overview");
    expect(once).toEqual({ current: "patrol_a", stack: ["overview"] });
    expect(backFrom(once, "overview")).toEqual({ current: "overview", stack: [] });
  });
  it("goes to the fallback view when there is nothing to go back to", () => {
    expect(backFrom({ current: "patrol_a", stack: [] }, "overview")).toEqual({ current: "overview", stack: [] });
  });
});
