import { describe, expect, it } from "vitest";
import type { ObjectGraph } from "../../contracts.gen";
import { COL_W, layoutObjectGraph, orientLinks, ROW_H } from "./objectGraphLayout";

const g = {
  focus: "fast1",
  nodes: [
    { id: "fast1", type: "target", label: "fast1", t_ms: 9 }, { id: "c2", type: "command", label: "c2", t_ms: 2 },
    { id: "c1", type: "command", label: "c1", t_ms: 1 }, { id: "blk-c3", type: "block", label: "b", t_ms: 0 },
    { id: "d2", type: "vehicle", label: "d2", t_ms: null }, { id: "dec-4", type: "decision", label: "dec", t_ms: 5 },
    { id: "r1", type: "report", label: "r", t_ms: 3 },
  ],
  links: [
    { src: "c1", dst: "d2", rel: "sent_to" }, { src: "c1", dst: "fast1", rel: "aims_at" },
    { src: "dec-4", dst: "r1", rel: "answers" }, { src: "blk-c3", dst: "c2", rel: "blocked" },
  ],
} as ObjectGraph;

describe("layoutObjectGraph", () => {
  it("puts each type in its column left to right, blocks between commands and targets", () => {
    const p = layoutObjectGraph(g);
    expect([p.d2.x, p.r1.x, p["dec-4"].x, p.c1.x, p["blk-c3"].x, p.fast1.x])
      .toEqual([0, COL_W, 2 * COL_W, 3 * COL_W, 4 * COL_W, 5 * COL_W]);
  });
  it("orders a column by time", () => {
    const p = layoutObjectGraph(g);
    expect([p.c1.y, p.c2.y]).toEqual([0, ROW_H]);
  });
});

describe("orientLinks", () => {
  it("draws every link left to right and marks the ones whose arrow points back at the left node", () => {
    expect(orientLinks(g)).toEqual([
      { id: "c1-sent_to-d2", source: "d2", target: "c1", label: "이 기체에", reversed: true },
      { id: "c1-aims_at-fast1", source: "c1", target: "fast1", label: "겨눔", reversed: false },
      { id: "dec-4-answers-r1", source: "r1", target: "dec-4", label: "답함", reversed: true },
      { id: "blk-c3-blocked-c2", source: "c2", target: "blk-c3", label: "막음", reversed: true },
    ]);
  });
});
