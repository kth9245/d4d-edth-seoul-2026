import { afterEach, describe, expect, it, vi } from "vitest";
import role from "../../../../../contracts/examples/role.json";
import type { Role } from "../../contracts.gen";
import { forSave, postDraft } from "./draftRequests";

describe("postDraft", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("posts DraftIn to /roles/draft and returns the drafted role", async () => {
    const f = vi.fn((_url: string, _init?: RequestInit) =>
      Promise.resolve({ ok: true, json: () => Promise.resolve(role) } as Response));
    vi.stubGlobal("fetch", f);
    const r = await postDraft("드론으로 북쪽 해안을 순찰해");
    expect(r).toEqual({ ok: true, role });
    const [url, init] = f.mock.calls[0];
    expect([url, init?.method]).toEqual(["/roles/draft", "POST"]);
    expect(JSON.parse(init?.body as string)).toEqual({ text: "드론으로 북쪽 해안을 순찰해" });
  });

  it("returns the status when the gateway fails, and says when it did not answer", async () => {
    vi.stubGlobal("fetch", () => Promise.resolve({ ok: false, status: 500, json: () => Promise.resolve({}) } as Response));
    expect(await postDraft("x")).toEqual({ ok: false, error: "응답 500" });
    vi.stubGlobal("fetch", () => Promise.reject(new Error("net")));
    expect(await postDraft("x")).toEqual({ ok: false, error: "서버 응답 없음" });
  });
});

describe("forSave", () => {
  const base = role as Role;

  it("marks an AI draft approved: saving after the check is the operator's approval (decision 0003)", () => {
    const draft = { ...base, origin: "ai_draft", approved: false } as Role;
    expect(forSave(draft).approved).toBe(true);
    expect(draft.approved).toBe(false); // input unchanged
  });

  it("leaves other roles as they are", () => {
    const human = { ...base, origin: "human", approved: true } as Role;
    expect(forSave(human)).toBe(human);
  });
});
