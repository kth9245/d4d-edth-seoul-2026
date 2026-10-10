import { afterEach, describe, expect, it, vi } from "vitest";
import { opsRun } from "../live/opsRun";
import { fetchMavlink } from "./fetchMavlink";

describe("fetchMavlink", () => {
  afterEach(() => vi.unstubAllGlobals());
  const stub = (res: Partial<Response> | Error) => {
    const f = vi.fn(() => (res instanceof Error ? Promise.reject(res) : Promise.resolve(res as Response)));
    vi.stubGlobal("fetch", f);
    return f;
  };
  const line = "21:00:00 ugv COMMAND_LONG MAV_CMD_DO_SET_MODE(176) 1 4 0 0 0 0 0";

  it("returns the lines of GET /mavlink", async () => {
    const f = stub({ ok: true, json: () => Promise.resolve([line]) });
    expect(await fetchMavlink()).toEqual([line]);
    expect(f.mock.calls[0]).toContain("/mavlink");
  });
  it("is null when the gateway answers an error, so the window keeps its lines", async () => {
    stub({ ok: false, status: 500, json: () => Promise.resolve({ detail: "x" }) });
    expect(await fetchMavlink()).toBeNull();
  });
  it("is null when the request fails", async () => {
    stub(new Error("net"));
    expect(await fetchMavlink()).toBeNull();
  });
  it("reads the 실작전 run's lines while that screen is on (decision 0068)", async () => {
    const f = stub({ ok: true, json: () => Promise.resolve([]) });
    opsRun.set(true);
    await fetchMavlink();
    opsRun.set(false);
    expect(f.mock.calls[0]).toContain("/mavlink?run=ops");
  });
});
