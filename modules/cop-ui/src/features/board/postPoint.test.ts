import { afterEach, describe, expect, it, vi } from "vitest";
import { postPoint } from "./postPoint";

describe("postPoint", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("asks for the play with the target, approved by the press (decisions 0048, 0049)", async () => {
    const f = vi.fn((_u: string, _i?: RequestInit) =>
      Promise.resolve({ ok: true, json: () => Promise.resolve({ id: "inj-3" }) } as Response));
    vi.stubGlobal("fetch", f);
    expect(await postPoint("d3", "watch", "boat2")).toEqual({ ok: true, id: "inj-3" });
    const [url, init] = f.mock.calls[0];
    expect(url).toBe("/injections");
    expect(JSON.parse(init?.body as string)).toEqual({ play_by_vehicle: { d3: "watch" }, target_by_vehicle: { d3: "boat2" }, approve: true });
  });

  it("returns the error instead of throwing when the gateway is down", async () => {
    vi.stubGlobal("fetch", vi.fn(() => Promise.reject(new Error("net"))));
    expect(await postPoint("d3", "watch", "boat2")).toEqual({ ok: false, error: "서버 연결 실패" });
  });
});
