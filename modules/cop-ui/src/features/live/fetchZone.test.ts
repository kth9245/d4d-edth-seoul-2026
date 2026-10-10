import { afterEach, describe, expect, it, vi } from "vitest";
import op from "../../../../../contracts/examples/operation.json";
import { fetchZone } from "./fetchZone";

describe("fetchZone", () => {
  afterEach(() => vi.unstubAllGlobals());
  const stub = (res: Partial<Response> | Error) => {
    const f = vi.fn(() => (res instanceof Error ? Promise.reject(res) : Promise.resolve(res as Response)));
    vi.stubGlobal("fetch", f);
    return f;
  };

  it("returns the zone of GET /operation", async () => {
    const f = stub({ ok: true, json: () => Promise.resolve(op) });
    expect(await fetchZone()).toEqual(op.zone);
    expect(f.mock.calls[0]).toContain("/operation");
  });
  it("is null when the gateway has no /operation yet", async () => {
    stub({ ok: false, status: 404, json: () => Promise.resolve({ detail: "Not Found" }) });
    expect(await fetchZone()).toBeNull();
  });
  it("is null when the body has no zone points", async () => {
    stub({ ok: true, json: () => Promise.resolve({ id: "op1" }) });
    expect(await fetchZone()).toBeNull();
  });
  it("is null when the request fails", async () => {
    stub(new Error("net"));
    expect(await fetchZone()).toBeNull();
  });
});
