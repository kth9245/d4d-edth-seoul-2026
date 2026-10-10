import { describe, expect, it } from "vitest";
import draft from "../../../../../demo/plays/cache/81cd9c681d4e492f8a0f162a02149ac5372516496c757508afb14505d253b793.json";
import type { Play } from "../../contracts.gen";
import { insertReportStep } from "./insertReportStep";

// The cached AI draft "북쪽 해안 순찰 및 고속정 접근": patrol --target_found--> approach_and_follow (no report).
const play = draft as Play;

describe("insertReportStep", () => {
  it("puts a hold step with a one-choice report right before the approach step", () => {
    const out = insertReportStep(play, "approach_and_follow");
    const i = out.steps.findIndex((s) => s.id === "approach_and_follow");
    const r = out.steps[i - 1];
    expect(r.id).toBe("approach_and_follow_report");
    expect(r.do.kind).toBe("hold");
    expect(r.report?.choices).toEqual([{ id: "approve", label: expect.stringContaining("승인"), play_by_vehicle: {} }]);
  });

  it("continues to the approach step through the choice's operator_choice exit (decision 0031)", () => {
    const r = insertReportStep(play, "approach_and_follow").steps.find((s) => s.id === "approach_and_follow_report")!;
    expect(r.on).toEqual([{ cond: { kind: "operator_choice", params: { choice: "approve" } }, go_step: "approach_and_follow" }]);
  });

  it("sends every exit that went to the approach step to the new report step instead", () => {
    const out = insertReportStep(play, "approach_and_follow");
    const patrol = out.steps.find((s) => s.id === "patrol_north_coast")!;
    expect(patrol.on?.map((e) => e.go_step)).toContain("approach_and_follow_report");
    expect(patrol.on?.map((e) => e.go_step)).not.toContain("approach_and_follow");
  });

  it("leaves the original play untouched and picks a free id", () => {
    const before = JSON.stringify(play);
    const twice = insertReportStep(insertReportStep(play, "approach_and_follow"), "approach_and_follow");
    expect(JSON.stringify(play)).toBe(before);
    expect(twice.steps.map((s) => s.id)).toContain("approach_and_follow_report-2");
  });
});
