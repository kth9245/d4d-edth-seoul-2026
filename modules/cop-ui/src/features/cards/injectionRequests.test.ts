import { afterEach, describe, expect, it, vi } from "vitest";
import { postSettle, postSwitch } from "./injectionRequests";

describe("injection requests", () => {
  afterEach(() => vi.unstubAllGlobals());
  const stub = (res: Partial<Response>) => {
    const f = vi.fn((_url: string, _init?: RequestInit) => Promise.resolve(res as Response));
    vi.stubGlobal("fetch", f);
    return f;
  };
  const ok = (id: string) => ({ ok: true, json: () => Promise.resolve({ id, label: "x", status: "pending" }) });

  it("approves with POST /injections/{id}/approve and no body", async () => {
    const f = stub(ok("inj-1"));
    expect(await postSettle("inj-1", true)).toEqual({ ok: true, id: "inj-1" });
    const [url, init] = f.mock.calls[0];
    expect([url, init?.method, init?.body]).toEqual(["/injections/inj-1/approve", "POST", undefined]);
  });

  it("rejects with POST /injections/{id}/reject", async () => {
    const f = stub(ok("inj-2"));
    await postSettle("inj-2", false);
    expect(f.mock.calls[0][0]).toBe("/injections/inj-2/reject");
  });

  it("requests a whole-operation switch by its id", async () => {
    const f = stub(ok("inj-3"));
    expect(await postSwitch({ switch_id: "all_home" })).toEqual({ ok: true, id: "inj-3" });
    const [url, init] = f.mock.calls[0];
    expect(url).toBe("/injections");
    expect(JSON.parse(init?.body as string)).toEqual({ switch_id: "all_home" });
  });

  it("requests a partial switch for chosen vehicles", async () => {
    const f = stub(ok("inj-4"));
    await postSwitch({ role_by_vehicle: { d2: "track_fast" } });
    expect(JSON.parse(f.mock.calls[0][1]?.body as string)).toEqual({ role_by_vehicle: { d2: "track_fast" } });
  });

  it("returns the server detail on failure", async () => {
    stub({ ok: false, status: 409, json: () => Promise.resolve({ detail: "injection is not pending" }) });
    expect(await postSettle("inj-1", true)).toEqual({ ok: false, error: "409 injection is not pending" });
  });
});
