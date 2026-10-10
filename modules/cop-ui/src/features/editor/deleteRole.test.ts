import { describe, expect, it } from "vitest";
import { deleteRole } from "./deleteRole";

const reply = (body: unknown, status = 200) => Promise.resolve(new Response(JSON.stringify(body), { status }));

describe("deleteRole", () => {
  it("sends DELETE /roles/{id} and says the server had it", async () => {
    const seen: { url: string; init?: RequestInit }[] = [];
    const had = await deleteRole("patrol_a", (url, init) => {
      seen.push({ url, init });
      return reply([{ id: "patrol_b" }]);
    });
    expect(had).toBe(true);
    expect(seen[0].url).toBe("/roles/patrol_a");
    expect(seen[0].init?.method).toBe("DELETE");
  });
  it("treats 404 as a role that was only on screen (never saved)", async () => {
    expect(await deleteRole("new-1", () => reply({ detail: "no role new-1" }, 404))).toBe(false);
  });
  it("throws on any other failure", async () => {
    await expect(deleteRole("x", () => reply({ detail: "boom" }, 500))).rejects.toThrow("500");
    await expect(deleteRole("x", () => Promise.reject(new TypeError("fetch failed")))).rejects.toThrow();
  });
});
