import { afterEach, describe, expect, it, vi } from "vitest";
import { fetchBoardData } from "./fetchBoardData";

const reply = (body: unknown, ok = true) => Promise.resolve({ ok, json: () => Promise.resolve(body) } as Response);

describe("fetchBoardData", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("reads roles, vehicle specs, watch points, enemies' roles and the operation's switch buttons", async () => {
    const data: Record<string, unknown> = { "/roles": [{ id: "watch" }], "/vehicles": [{ id: "d1" }], "/watch_points": [{ id: "landing" }],
      "/enemies": [{ id: "boat1", role_id: "enemy_boat1" }], "/operation": { switches: [{ id: "all_home", label: "전 기체 귀환", role_by_vehicle: {} }] } };
    vi.stubGlobal("fetch", vi.fn((u: string) => reply(data[u])));
    expect(await fetchBoardData()).toEqual({ roles: [{ id: "watch" }], vehicles: [{ id: "d1" }], watch: [{ id: "landing" }],
      enemyRoles: ["enemy_boat1"], switches: [{ id: "all_home", label: "전 기체 귀환", role_by_vehicle: {} }] });
  });

  it("gives empty lists for a failed, non-list or unreachable read", async () => {
    vi.stubGlobal("fetch", vi.fn((u: string) =>
      (u === "/roles" ? reply(null, false) : u === "/vehicles" ? reply({}) : u === "/operation" ? reply({ id: "op1" }) : Promise.reject(new Error("net")))));
    expect(await fetchBoardData()).toEqual({ roles: [], vehicles: [], watch: [], enemyRoles: [], switches: [] });
  });
});
