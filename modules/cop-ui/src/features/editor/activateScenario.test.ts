import { describe, expect, it } from "vitest";
import { activateScenario } from "./activateScenario";

const reply = (body: unknown, status = 200) => Promise.resolve(new Response(JSON.stringify(body), { status }));

describe("activateScenario", () => {
  it("POSTs to /scenarios/{id}/activate and returns the RunState", async () => {
    const seen: { url: string; init?: RequestInit }[] = [];
    const run = { status: "paused", speed: 1 };
    const got = await activateScenario("baengnyeong_24h", (url, init) => {
      seen.push({ url, init });
      return reply(run);
    });
    expect(got).toEqual(run);
    expect(seen[0].url).toBe("/scenarios/baengnyeong_24h/activate");
    expect(seen[0].init?.method).toBe("POST");
  });
  it("throws with the status on a non-2xx answer", async () => {
    await expect(activateScenario("nope", () => reply({ detail: "no scenario nope" }, 404))).rejects.toThrow("404");
  });
  it("throws when the server cannot be reached", async () => {
    await expect(activateScenario("x", () => Promise.reject(new TypeError("fetch failed")))).rejects.toThrow();
  });
});
