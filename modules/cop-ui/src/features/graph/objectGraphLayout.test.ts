import { describe, expect, it } from "vitest";
import type { ObjectGraph } from "../../contracts.gen";
import { COL_W, layoutObjectGraph, ROW_H } from "./objectGraphLayout";

const g = {
  focus: "fast1",
  nodes: [
    { id: "fast1", type: "target", label: "fast1", t_ms: 9 }, { id: "c2", type: "command", label: "c2", t_ms: 2 },
    { id: "c1", type: "command", label: "c1", t_ms: 1 }, { id: "blk-c3", type: "block", label: "b", t_ms: 0 },
    { id: "d2", type: "vehicle", label: "d2", t_ms: null }, { id: "dec-4", type: "decision", label: "dec", t_ms: 5 },
  ],
  links: [],
} as ObjectGraph;

describe("layoutObjectGraph", () => {
  it("puts each type in its column left to right", () => {
    const p = layoutObjectGraph(g);
    expect([p.d2.x, p["dec-4"].x, p.c1.x, p.fast1.x]).toEqual([0, 2 * COL_W, 3 * COL_W, 4 * COL_W]);
  });
  it("orders a column by time and puts blocks after commands", () => {
    const p = layoutObjectGraph(g);
    expect([p.c1.y, p.c2.y, p["blk-c3"].y]).toEqual([0, ROW_H, 2 * ROW_H]);
  });
});
