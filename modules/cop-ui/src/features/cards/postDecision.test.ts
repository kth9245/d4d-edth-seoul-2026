import { afterEach, describe, expect, it, vi } from "vitest";
import { opsRun } from "../live/opsRun";
import { postDecision } from "./postDecision";

describe("postDecision", () => {
  afterEach(() => vi.unstubAllGlobals());
  const stub = (res: Partial<Response> | Error) => {
    const f = vi.fn((_url: string, _init?: RequestInit) =>
      res instanceof Error ? Promise.reject(res) : Promise.resolve(res as Response));
    vi.stubGlobal("fetch", f);
    return f;
  };

  it("posts DecisionIn to /decisions and returns the accepted id", async () => {
    const f = stub({ ok: true, json: () => Promise.resolve({ id: "dec-1", t_ms: 1791634290000 }) });
    expect(await postDecision("rep-d1-1791634270000", "approach")).toEqual({ ok: true, id: "dec-1" });
    const [url, init] = f.mock.calls[0];
    expect(url).toBe("/decisions");
    expect(init?.method).toBe("POST");
    expect(JSON.parse(init?.body as string)).toEqual({ report_id: "rep-d1-1791634270000", choice_id: "approach" });
  });

  it("returns the server detail on 409", async () => {
    stub({ ok: false, status: 409, json: () => Promise.resolve({ detail: "report already resolved" }) });
    expect(await postDecision("r", "c")).toEqual({ ok: false, error: "409 report already resolved" });
  });

  it("returns the status when the body is not JSON (proxy 502)", async () => {
    stub({ ok: false, status: 502, json: () => Promise.reject(new Error("not json")) });
    expect(await postDecision("r", "c")).toEqual({ ok: false, error: "502" });
  });

  it("says the server is unreachable when fetch fails", async () => {
    stub(new Error("net"));
    expect(await postDecision("r", "c")).toEqual({ ok: false, error: "서버 연결 실패" });
  });

  it("goes to the 실작전 run while that screen is on (decision 0068)", async () => {
    const f = stub({ ok: true, json: () => Promise.resolve({ id: "dec-1", t_ms: 0 }) });
    opsRun.set(true);
    await postDecision("r", "c");
    opsRun.set(false);
    expect(f.mock.calls[0][0]).toBe("/decisions?run=ops");
  });
});
