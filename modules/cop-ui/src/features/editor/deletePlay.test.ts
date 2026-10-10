import { describe, expect, it } from "vitest";
import { deletePlay } from "./deletePlay";

const reply = (body: unknown, status = 200) => Promise.resolve(new Response(JSON.stringify(body), { status }));

describe("deletePlay", () => {
  it("sends DELETE /plays/{id} and says the server had it", async () => {
    const seen: { url: string; init?: RequestInit }[] = [];
    const had = await deletePlay("patrol_a", (url, init) => {
      seen.push({ url, init });
      return reply([{ id: "patrol_b" }]);
    });
    expect(had).toBe(true);
    expect(seen[0].url).toBe("/plays/patrol_a");
    expect(seen[0].init?.method).toBe("DELETE");
  });
  it("treats 404 as a play that was only on screen (never saved)", async () => {
    expect(await deletePlay("new-1", () => reply({ detail: "no play new-1" }, 404))).toBe(false);
  });
  it("throws on any other failure", async () => {
    await expect(deletePlay("x", () => reply({ detail: "boom" }, 500))).rejects.toThrow("500");
    await expect(deletePlay("x", () => Promise.reject(new TypeError("fetch failed")))).rejects.toThrow();
  });
});
