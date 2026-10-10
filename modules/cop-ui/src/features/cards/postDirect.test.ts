import { afterEach, describe, expect, it, vi } from "vitest";
import { postDirect } from "./postDirect";

describe("postDirect", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("posts DirectIn to /direct and returns the accepted id", async () => {
    const f = vi.fn((_url: string, _init?: RequestInit) =>
      Promise.resolve({ ok: true, json: () => Promise.resolve({ id: "dir-1", t_ms: 1 }) } as Response));
    vi.stubGlobal("fetch", f);
    expect(await postDirect("d2", { lat: 37.99955, lon: 124.6903 })).toEqual({ ok: true, id: "dir-1" });
    const [url, init] = f.mock.calls[0];
    expect(url).toBe("/direct");
    expect(JSON.parse(init?.body as string)).toEqual({ vehicle_id: "d2", target: { lat: 37.99955, lon: 124.6903 } });
  });
});
