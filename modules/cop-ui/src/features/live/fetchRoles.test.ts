import { afterEach, describe, expect, it, vi } from "vitest";
import role from "../../../../../contracts/examples/role.json";
import { fetchRoles } from "./fetchRoles";

describe("fetchRoles", () => {
  afterEach(() => vi.unstubAllGlobals());
  const stub = (res: Partial<Response> | Error) => {
    const f = vi.fn(() => (res instanceof Error ? Promise.reject(res) : Promise.resolve(res as Response)));
    vi.stubGlobal("fetch", f);
    return f;
  };

  it("returns the roles of GET /roles", async () => {
    const f = stub({ ok: true, json: () => Promise.resolve([role]) });
    expect((await fetchRoles()).map((p) => p.id)).toEqual([role.id]);
    expect(f.mock.calls[0]).toContain("/roles");
  });
  it("is empty when the gateway fails or answers something else", async () => {
    stub({ ok: false, status: 404, json: () => Promise.resolve({ detail: "x" }) });
    expect(await fetchRoles()).toEqual([]);
    stub({ ok: true, json: () => Promise.resolve({ not: "a list" }) });
    expect(await fetchRoles()).toEqual([]);
    stub(new Error("net"));
    expect(await fetchRoles()).toEqual([]);
  });
});
