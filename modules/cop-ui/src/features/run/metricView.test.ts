import { describe, expect, it } from "vitest";
import metrics from "../../../../../contracts/examples/metrics.json";
import { metricView } from "./metricView";

describe("metricView", () => {
  it("puts operator actions next to the manual baseline and lists the rest", () => {
    expect(metricView(metrics)).toEqual({
      operator: 1,
      manual: 7,
      rows: [
        ["결정", "1"],
        ["보낸 명령", "6"],
        ["차단된 명령", "0"],
        ["기체 공백", "0:00"],
        ["동시 미결 카드 최대", "1"],
      ],
    });
  });
  it("shows the vehicle gap as minutes:seconds", () => {
    expect(metricView({ vehicle_gap_ms: 198_000 }).rows).toContainEqual(["기체 공백", "3:18"]);
  });
  it("reads missing fields as zero", () => {
    const v = metricView({});
    expect([v.operator, v.manual]).toEqual([0, 0]);
    expect(v.rows[0]).toEqual(["결정", "0"]);
  });
  it("does not judge the mission: the strike result is on its card (Part1-20)", () => {
    expect(metricView({ mission_success: true }).rows.map(([k]) => k)).not.toContain("임무");
  });
});
