import { afterEach, describe, expect, it, vi } from "vitest";
import { fetchBoardData } from "./fetchBoardData";

const reply = (body: unknown, ok = true) => Promise.resolve({ ok, json: () => Promise.resolve(body) } as Response);

describe("fetchBoardData", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("reads roles, vehicle specs and watch points", async () => {
    const data: Record<string, unknown> = { "/roles": [{ id: "watch" }], "/vehicles": [{ id: "d1" }], "/watch_points": [{ id: "landing" }] };
    vi.stubGlobal("fetch", vi.fn((u: string) => reply(data[u])));
    expect(await fetchBoardData()).toEqual({ roles: [{ id: "watch" }], vehicles: [{ id: "d1" }], watch: [{ id: "landing" }] });
  });

  it("gives empty lists for a failed, non-list or unreachable read", async () => {
    vi.stubGlobal("fetch", vi.fn((u: string) =>
      (u === "/roles" ? reply(null, false) : u === "/vehicles" ? reply({}) : Promise.reject(new Error("net")))));
    expect(await fetchBoardData()).toEqual({ roles: [], vehicles: [], watch: [] });
  });
});
