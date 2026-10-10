import { afterEach, describe, expect, it, vi } from "vitest";
import op from "../../../../../contracts/examples/operation.json";
import { fetchOperation } from "./fetchOperation";

describe("fetchOperation", () => {
  afterEach(() => vi.unstubAllGlobals());
  const stub = (res: Partial<Response> | Error) => {
    const f = vi.fn((_url: string) => (res instanceof Error ? Promise.reject(res) : Promise.resolve(res as Response)));
    vi.stubGlobal("fetch", f);
    return f;
  };

  it("returns the body of GET /operation", async () => {
    const f = stub({ ok: true, json: () => Promise.resolve(op) });
    expect(await fetchOperation()).toEqual(op);
    expect(f.mock.calls[0][0]).toBe("/operation");
  });
  it("is null when the gateway answers an error", async () => {
    stub({ ok: false, status: 404, json: () => Promise.resolve({ detail: "Not Found" }) });
    expect(await fetchOperation()).toBeNull();
  });
  it("is null when the body is not JSON", async () => {
    stub({ ok: true, json: () => Promise.reject(new Error("html")) });
    expect(await fetchOperation()).toBeNull();
  });
  it("is null when the request fails", async () => {
    stub(new Error("net"));
    expect(await fetchOperation()).toBeNull();
  });
});
