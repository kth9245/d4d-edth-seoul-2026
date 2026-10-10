import { describe, expect, it } from "vitest";
import { mkCard } from "./boardFixtures";
import { situationCounts, targetsLabel } from "./situationCounts";
import type { Stage } from "./targetStage";

const s = (key: Stage["key"]): Stage => ({ key, label: key, detail: "", away: false });

describe("situationCounts", () => {
  it("counts targets per stage, most urgent first, leaving out empty stages", () => {
    const got = situationCounts([s("found"), s("never"), s("ask"), s("found"), s("lost")], { action: [], alerts: [], history: [] });
    expect(got.targets).toBe(5);
    expect(got.stages).toEqual([
      { key: "ask", label: "허락 대기", n: 1 }, { key: "lost", label: "놓침", n: 1 },
      { key: "found", label: "발견", n: 2 }, { key: "never", label: "미탐", n: 1 },
    ]);
  });

  it("counts decisions, one per vehicle in a merged target pick", () => {
    const q = { action: [{ key: "a", cards: [mkCard({ id: "a" })] }, { key: "p", cards: [mkCard({ id: "p1" }), mkCard({ id: "p2" })] }],
      alerts: [], history: [] };
    expect(situationCounts([], q).decisions).toBe(3);
  });
});

describe("targetsLabel", () => {
  it("counts enemies without the ship counter, since they can be sites, robots or drones (decision 0080)", () => {
    expect(targetsLabel(3)).toBe("적 3");
    expect(targetsLabel(0)).toBe("적 0");
  });
});
