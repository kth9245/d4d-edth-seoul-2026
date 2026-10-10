import { describe, expect, it } from "vitest";
import type { Operation, Role, VehicleSpec } from "../../contracts.gen";
import { createOperation } from "./createOperation";
import { postOperation } from "./postOperation";
import { setStartRole } from "./setStartRole";
import { startRoleOptions } from "./startRoleOptions";

const role = (id: string, domains: Role["domains"]) => ({ id, name: `이름 ${id}`, domains, steps: [], entry: "s" }) as unknown as Role;
const drone = { id: "d1", domain: "air" } as VehicleSpec;
const op = { id: "op", assign: { d1: "patrol", d2: "patrol" } } as unknown as Operation;
const reply = (body: unknown, status = 200) => Promise.resolve(new Response(JSON.stringify(body), { status }));

describe("start roles on the overview (decision 0053)", () => {
  it("offers the roles of the vehicle's domain, not the enemies' roles", () => {
    const roles = [role("patrol", ["air"]), role("boat", ["sea"]), role("enemy_fast", ["air", "sea"]), role("go_home", ["air", "sea"])];
    expect(startRoleOptions(roles, drone, ["enemy_fast"])).toEqual([
      { id: "patrol", name: "이름 patrol" },
      { id: "go_home", name: "이름 go_home" },
    ]);
  });
  it("sets or clears one vehicle's start role and leaves the others", () => {
    expect(setStartRole(op, "d1", "go_home").assign).toEqual({ d1: "go_home", d2: "patrol" });
    expect(setStartRole(op, "d1", null).assign).toEqual({ d2: "patrol" });
    expect(op.assign).toEqual({ d1: "patrol", d2: "patrol" });
  });
  it("posts the operation and returns the server's copy", async () => {
    const seen: { url: string; init?: RequestInit }[] = [];
    const back = await postOperation(op, (url, init) => (seen.push({ url, init }), reply(op)));
    expect(back).toEqual(op);
    expect(seen[0].url).toBe("/operation");
    expect(seen[0].init?.method).toBe("POST");
    expect(JSON.parse(String(seen[0].init?.body))).toEqual(op);
    await expect(postOperation(op, () => reply({ detail: "bad" }, 422))).rejects.toThrow("422");
  });
  it("creates an operation by name and purpose and returns the operation list", async () => {
    const list = [{ id: "new_op_1", name: "QA", purpose: "", active: true }];
    const seen: { url: string; init?: RequestInit }[] = [];
    expect(await createOperation("QA", "", (url, init) => (seen.push({ url, init }), reply(list)))).toEqual(list);
    expect(seen[0].url).toBe("/scenarios");
    expect(JSON.parse(String(seen[0].init?.body))).toEqual({ name: "QA", purpose: "" });
    await expect(createOperation("QA", "", () => reply({}, 500))).rejects.toThrow("500");
  });
});
