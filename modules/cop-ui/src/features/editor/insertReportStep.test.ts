import { describe, expect, it } from "vitest";
import type { Role } from "../../contracts.gen";
import { insertReportStep } from "./insertReportStep";

// Same shape as the cached AI draft "북쪽 해안 순찰 및 고속정 접근" (patrol --target_found--> approach, no report).
// Written here, not imported: cache files are named by draft_cache_key (decision 0057) and are renamed when the key changes.
const role: Role = {
  id: "north_coast_patrol_follow", name: "북쪽 해안 순찰 및 고속정 접근", domains: ["air"], entry: "patrol_north_coast",
  steps: [
    { id: "patrol_north_coast", name: "북쪽 해안 순찰",
      do: { kind: "patrol_route", params: { route: [{ lat: 37.985, lon: 124.62 }, { lat: 37.985, lon: 124.78 }] } },
      on: [{ cond: { kind: "target_found", params: {} }, go_step: "approach_and_follow" }] },
    { id: "approach_and_follow", name: "고속정 접근 추적", do: { kind: "approach_target", params: { target: "nearest" } }, on: [] },
  ],
};

describe("insertReportStep", () => {
  it("puts a hold step with a one-choice report right before the approach step", () => {
    const out = insertReportStep(role, "approach_and_follow");
    const i = out.steps.findIndex((s) => s.id === "approach_and_follow");
    const r = out.steps[i - 1];
    expect(r.id).toBe("approach_and_follow_report");
    expect(r.do.kind).toBe("hold");
    expect(r.report?.choices).toEqual([{ id: "approve", label: expect.stringContaining("승인"), role_by_vehicle: {} }]);
  });

  it("continues to the approach step through the choice's operator_choice exit (decision 0031)", () => {
    const r = insertReportStep(role, "approach_and_follow").steps.find((s) => s.id === "approach_and_follow_report")!;
    expect(r.on).toEqual([{ cond: { kind: "operator_choice", params: { choice: "approve" } }, go_step: "approach_and_follow" }]);
  });

  it("sends every exit that went to the approach step to the new report step instead", () => {
    const out = insertReportStep(role, "approach_and_follow");
    const patrol = out.steps.find((s) => s.id === "patrol_north_coast")!;
    expect(patrol.on?.map((e) => e.go_step)).toContain("approach_and_follow_report");
    expect(patrol.on?.map((e) => e.go_step)).not.toContain("approach_and_follow");
  });

  it("leaves the original role untouched and picks a free id", () => {
    const before = JSON.stringify(role);
    const twice = insertReportStep(insertReportStep(role, "approach_and_follow"), "approach_and_follow");
    expect(JSON.stringify(role)).toBe(before);
    expect(twice.steps.map((s) => s.id)).toContain("approach_and_follow_report-2");
  });
});
