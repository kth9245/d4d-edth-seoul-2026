import { describe, expect, it } from "vitest";
import { blankPlay } from "./blankPlay";

describe("blankPlay", () => {
  it("makes a human play with one start card that holds", () => {
    const p = blankPlay("야간 정찰", "air", []);
    expect(p).toMatchObject({ id: "new_play", name: "야간 정찰", domains: ["air"], entry: "start", origin: "human",
      approved: true, template: false });
    expect(p.steps).toEqual([{ id: "start", name: "시작", do: { kind: "hold", params: {} }, on: [], report: null, ui: {} }]);
  });

  it("picks an id no other play has", () => {
    expect(blankPlay("a", "sea", ["new_play"]).id).toBe("new_play-2");
    expect(blankPlay("a", "sea", ["new_play", "new_play-2"]).id).toBe("new_play-3");
  });

  it("names it when the name is left empty", () => {
    expect(blankPlay("  ", "ground", []).name).toBe("새 플레이");
  });
});
