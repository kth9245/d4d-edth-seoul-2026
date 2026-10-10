import { afterEach, describe, expect, it, vi } from "vitest";
import { postRole } from "./postRole";

describe("postRole", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("asks for the role without a target, approved by the press (decision 0059)", async () => {
    const f = vi.fn((_u: string, _i?: RequestInit) =>
      Promise.resolve({ ok: true, json: () => Promise.resolve({ id: "inj-4" }) } as Response));
    vi.stubGlobal("fetch", f);
    expect(await postRole("d2", "go_home")).toEqual({ ok: true, id: "inj-4" });
    const [url, init] = f.mock.calls[0];
    expect(url).toBe("/injections");
    expect(JSON.parse(init?.body as string)).toEqual({ role_by_vehicle: { d2: "go_home" }, approve: true });
  });

  it("returns the error instead of throwing when the gateway is down", async () => {
    vi.stubGlobal("fetch", vi.fn(() => Promise.reject(new Error("net"))));
    expect(await postRole("d2", "go_home")).toEqual({ ok: false, error: "서버 연결 실패" });
  });
});
