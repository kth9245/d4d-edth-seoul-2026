import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { Role, RoleCheck } from "../../contracts.gen";
import { batteryText, issuesByStep, saveErrorText } from "./checkView";

describe("saveErrorText", () => {
  it("shows the status the gateway answered", () => {
    expect(saveErrorText('Error: /roles answered 422: {"detail":[]}')).toBe("저장 실패: 응답 422");
    expect(saveErrorText("Error: /roles answered 500: Internal Server Error")).toBe("저장 실패: 응답 500");
  });
  it("says the server did not answer when the request itself failed", () => {
    expect(saveErrorText("TypeError: Failed to fetch")).toBe("저장 실패: 서버 응답 없음");
  });
});

const patrolA = scenario.roles[1] as unknown as Role; // steps: patrol, report

describe("issuesByStep", () => {
  it("puts issues with a known step id on that step, the rest on the role", () => {
    const check: RoleCheck = {
      ok: false,
      issues: [
        { code: "missing_report_point", step_id: "report", message: "a" },
        { code: "domain_mismatch", step_id: null, message: "b" },
        { code: "x", step_id: "gone", message: "c" },
        { code: "missing_capability", step_id: "report", message: "d" },
      ],
    };
    const v = issuesByStep(check, patrolA);
    expect(v.byStep["report"].map((i) => i.message)).toEqual(["a", "d"]);
    expect(v.byStep["patrol"]).toBeUndefined();
    expect(v.general.map((i) => i.message)).toEqual(["b", "c"]);
  });
  it("is empty for a passing check", () => {
    expect(issuesByStep({ ok: true, issues: [] }, patrolA)).toEqual({ byStep: {}, general: [] });
  });
});

describe("batteryText", () => {
  it("lists the expected battery at home per vehicle", () => {
    expect(batteryText({ d1: 53.6, d3: 51.4 })).toBe("d1 53.6% · d3 51.4%");
    expect(batteryText({ usv: 100 })).toBe("usv 100.0%");
  });
  it("is empty without estimates", () => {
    expect(batteryText(undefined)).toBe("");
  });
});
