import { describe, expect, it } from "vitest";
import { choiceGroups } from "./choiceGroups";

// boat1's card in the demo (decision 0046), after decision 0048 keeps watch-together to d1 only
const BOAT1 = [
  { id: "approach", label: "근접 확인", preview: "d1→watch · usv→approach · ugv→landing" },
  { id: "take_d3", label: "d3 → 발생 지역 순찰(해안 순찰 A)", preview: "d3→patrol_a" },
  { id: "take_d4", label: "d4 → 발생 지역 순찰(해안 순찰 A)", preview: "d4→patrol_a" },
  { id: "join_d3_d1", label: "d3 → d1와 함께 감시(boat1)", preview: "d3→watch" },
  { id: "join_d4_d1", label: "d4 → d1와 함께 감시(boat1)", preview: "d4→watch" },
];

describe("choiceGroups", () => {
  it("keeps the card's planned choices first and groups drone requests by what they ask", () => {
    const g = choiceGroups(BOAT1);
    expect(g.planned.map((c) => c.id)).toEqual(["approach"]);
    expect(g.requests).toEqual([
      { what: "해안 순찰 A 이어받기", options: [{ vehicle: "d3", choiceId: "take_d3" }, { vehicle: "d4", choiceId: "take_d4" }] },
      { what: "d1와 함께 boat1 감시", options: [{ vehicle: "d3", choiceId: "join_d3_d1" }, { vehicle: "d4", choiceId: "join_d4_d1" }] },
    ]);
  });

  it("treats choices that move several vehicles or none as planned", () => {
    const g = choiceGroups([
      { id: "keep", label: "감시 유지", preview: "" },
      { id: "both", label: "함께 타격", preview: "d2→strike · usv→strike" },
      { id: "one", label: "이 기체로 타격", preview: "usv→strike" },
    ]);
    expect(g.planned.map((c) => c.id)).toEqual(["keep", "both", "one"]);
    expect(g.requests).toEqual([]);
  });
});
