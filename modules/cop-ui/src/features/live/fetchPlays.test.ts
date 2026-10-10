import { afterEach, describe, expect, it, vi } from "vitest";
import play from "../../../../../contracts/examples/play.json";
import { fetchPlays } from "./fetchPlays";

describe("fetchPlays", () => {
  afterEach(() => vi.unstubAllGlobals());
  const stub = (res: Partial<Response> | Error) => {
    const f = vi.fn(() => (res instanceof Error ? Promise.reject(res) : Promise.resolve(res as Response)));
    vi.stubGlobal("fetch", f);
    return f;
  };

  it("returns the plays of GET /plays", async () => {
    const f = stub({ ok: true, json: () => Promise.resolve([play]) });
    expect((await fetchPlays()).map((p) => p.id)).toEqual([play.id]);
    expect(f.mock.calls[0]).toContain("/plays");
  });
  it("is empty when the gateway fails or answers something else", async () => {
    stub({ ok: false, status: 404, json: () => Promise.resolve({ detail: "x" }) });
    expect(await fetchPlays()).toEqual([]);
    stub({ ok: true, json: () => Promise.resolve({ not: "a list" }) });
    expect(await fetchPlays()).toEqual([]);
    stub(new Error("net"));
    expect(await fetchPlays()).toEqual([]);
  });
});
