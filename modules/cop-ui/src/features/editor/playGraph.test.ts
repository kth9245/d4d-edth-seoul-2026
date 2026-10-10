import { describe, expect, it } from "vitest";
import patrol from "../../../../../demo/plays/patrol_a.json";
import type { Play } from "../../contracts.gen";
import { insertReportStep } from "./insertReportStep";
import { CARD_GAP, COL_W, estimateHeight, exitText, layoutSteps, stepEdges } from "./playGraph";

// Same shape as the cached AI draft "북쪽 해안 순찰 및 고속정 접근" (see insertReportStep.test.ts).
const draft: Play = {
  id: "north_coast_patrol_follow", name: "북쪽 해안 순찰 및 고속정 접근", domains: ["air"], entry: "patrol_north_coast",
  steps: [
    { id: "patrol_north_coast", name: "북쪽 해안 순찰", do: { kind: "patrol_route", params: {} },
      on: [{ cond: { kind: "target_found", params: {} }, go_step: "approach_and_follow" }] },
    { id: "approach_and_follow", name: "고속정 접근 추적", do: { kind: "approach_target", params: {} }, on: [] },
  ],
};
const guarded = insertReportStep(draft, "approach_and_follow");

describe("exitText", () => {
  it("reads an operator_choice exit as the choice label on this step's report", () => {
    const report = guarded.steps.find((s) => s.id === "approach_and_follow_report")!;
    expect(exitText(report, report.on![0].cond)).toBe("'고속정 접근 추적 승인' 선택 시");
  });
  it("falls back to the plain condition text", () => {
    expect(exitText(draft.steps[0], draft.steps[0].on![0].cond)).toBe("표적 발견");
  });
});

describe("layoutSteps", () => {
  it("puts the entry in the first column and each next step one column to the right", () => {
    const pos = layoutSteps(guarded);
    expect(pos.patrol_north_coast.x).toBe(0);
    expect(pos.approach_and_follow_report.x).toBe(COL_W);
    expect(pos.approach_and_follow.x).toBe(2 * COL_W);
  });
  it("stacks steps of one column without overlap", () => {
    const two: Play = { ...draft, steps: [
      { ...draft.steps[0], on: [{ cond: { kind: "target_found", params: {} }, go_step: "a" },
        { cond: { kind: "battery_below", params: { pct: 30 } }, go_step: "b" }] },
      { id: "a", name: "a", do: { kind: "hold", params: {} } }, { id: "b", name: "b", do: { kind: "hold", params: {} } }] };
    const pos = layoutSteps(two);
    expect(pos.a.x).toBe(pos.b.x);
    expect(pos.b.y).toBeGreaterThanOrEqual(pos.a.y + estimateHeight(two.steps[1]) + CARD_GAP);
  });
  it("puts steps the entry cannot reach in a column after the others", () => {
    const pos = layoutSteps({ ...draft, steps: [...draft.steps, { id: "orphan", name: "o", do: { kind: "hold", params: {} } }] });
    expect(pos.orphan.x).toBe(2 * COL_W);
  });
});

describe("stepEdges", () => {
  it("makes one edge per exit from that exit's handle, labelled by its condition", () => {
    const edges = stepEdges(patrol as Play, new Set());
    expect(edges).toEqual([{ id: "patrol:0", source: "patrol", sourceHandle: "exit-0", target: "report",
      label: "표적 발견", kind: "normal" }]);
  });
  it("marks operator-choice edges and edges into a step that failed the check", () => {
    const edges = stepEdges(guarded, new Set(["approach_and_follow"]));
    const choice = edges.find((e) => e.source === "approach_and_follow_report")!;
    expect(choice.kind).toBe("choice");
    expect(stepEdges(draft, new Set(["approach_and_follow"]))[0].kind).toBe("issue");
  });
  it("skips exits that point at a step the play does not have", () => {
    const broken: Play = { ...draft, steps: [{ ...draft.steps[0], on: [{ cond: { kind: "arrived", params: {} }, go_step: "nowhere" }] }] };
    expect(stepEdges(broken, new Set())).toEqual([]);
  });
});
