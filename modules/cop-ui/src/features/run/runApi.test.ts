import { afterEach, describe, expect, it, vi } from "vitest";
import { postRun } from "./runApi";

describe("postRun", () => {
  afterEach(() => vi.unstubAllGlobals());
  const stub = (...res: (Partial<Response> | Error)[]) => {
    const f = vi.fn((_url: string, _init?: RequestInit) => {
      const r = res.length > 1 ? res.shift()! : res[0];
      return r instanceof Error ? Promise.reject(r) : Promise.resolve(r as Response);
    });
    vi.stubGlobal("fetch", f);
    return f;
  };
  const ok = (body: unknown) => ({ ok: true, json: () => Promise.resolve(body) });

  it("POSTs the run path and returns the RunState", async () => {
    const f = stub(ok({ status: "running", speed: 10 }));
    expect(await postRun("/run/live?speed=10")).toEqual({ ok: true, run: { status: "running", speed: 10 } });
    expect(f.mock.calls[0][0]).toBe("/run/live?speed=10");
    expect(f.mock.calls[0][1]?.method).toBe("POST");
  });

  it("returns the server detail on 422", async () => {
    stub({ ok: false, status: 422, json: () => Promise.resolve({ detail: "bad speed" }) });
    expect(await postRun("/run/live?speed=x")).toEqual({ ok: false, error: "422 bad speed" });
  });

  it("returns the status when the body is not JSON (proxy 502)", async () => {
    stub({ ok: false, status: 502, json: () => Promise.reject(new Error("not json")) });
    expect(await postRun("/run/reset")).toEqual({ ok: false, error: "502" });
  });

  it("says the server is unreachable when fetch fails", async () => {
    stub(new Error("net"));
    expect(await postRun("/run/reset")).toEqual({ ok: false, error: "서버 연결 실패" });
  });
});
