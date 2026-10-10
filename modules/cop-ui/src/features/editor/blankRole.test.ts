import { describe, expect, it } from "vitest";
import { blankRole } from "./blankRole";

describe("blankRole", () => {
  it("makes a human role with one start card that holds", () => {
    const p = blankRole("야간 정찰", "air", []);
    expect(p).toMatchObject({ id: "new_role", name: "야간 정찰", domains: ["air"], entry: "start", origin: "human",
      approved: true, template: false });
    expect(p.steps).toEqual([{ id: "start", name: "시작", do: { kind: "hold", params: {} }, on: [], report: null, ui: {} }]);
  });

  it("picks an id no other role has", () => {
    expect(blankRole("a", "sea", ["new_role"]).id).toBe("new_role-2");
    expect(blankRole("a", "sea", ["new_role", "new_role-2"]).id).toBe("new_role-3");
  });

  it("names it when the name is left empty", () => {
    expect(blankRole("  ", "ground", []).name).toBe("새 Role");
  });
});
