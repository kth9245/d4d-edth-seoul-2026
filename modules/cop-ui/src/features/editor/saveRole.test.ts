import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { Role } from "../../contracts.gen";
import { saveRole } from "./saveRole";

const role = scenario.roles[1] as unknown as Role;
const reply = (body: unknown, status = 200) => Promise.resolve(new Response(JSON.stringify(body), { status }));

describe("saveRole", () => {
  it("POSTs the role as JSON to /roles and returns the RoleCheck", async () => {
    const seen: { url: string; init?: RequestInit }[] = [];
    const check = { ok: false, issues: [{ code: "missing_report_point", step_id: "rush", message: "m" }] };
    const got = await saveRole(role, (url, init) => {
      seen.push({ url, init });
      return reply(check);
    });
    expect(got).toEqual(check);
    expect(seen[0].url).toBe("/roles");
    expect(seen[0].init?.method).toBe("POST");
    expect(JSON.parse(String(seen[0].init?.body)).id).toBe(role.id);
  });
  it("throws with the status and detail on a non-2xx answer", async () => {
    await expect(saveRole(role, () => reply({ detail: "bad role" }, 422))).rejects.toThrow("422");
  });
  it("throws when the server cannot be reached", async () => {
    await expect(saveRole(role, () => Promise.reject(new TypeError("fetch failed")))).rejects.toThrow();
  });
});
