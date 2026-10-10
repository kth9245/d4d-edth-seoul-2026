import { describe, expect, it } from "vitest";
import info from "../../../../../contracts/examples/scenario_info.json";
import { fetchScenarios } from "./fetchScenarios";

const reply = (body: unknown, status = 200) => Promise.resolve(new Response(JSON.stringify(body), { status }));

describe("fetchScenarios", () => {
  it("returns the list from GET /scenarios", async () => {
    const urls: string[] = [];
    const got = await fetchScenarios((url) => {
      urls.push(url);
      return reply([info]);
    });
    expect(got).toEqual([info]);
    expect(urls).toEqual(["/scenarios"]);
  });
  it("is empty when the gateway answers an error", async () => {
    expect(await fetchScenarios(() => reply({ detail: "Not Found" }, 404))).toEqual([]);
  });
  it("is empty when the body is not a JSON list", async () => {
    expect(await fetchScenarios(() => Promise.resolve(new Response("<html>", { status: 200 })))).toEqual([]);
    expect(await fetchScenarios(() => reply({ id: "x" }))).toEqual([]);
  });
  it("is empty when the request fails", async () => {
    expect(await fetchScenarios(() => Promise.reject(new TypeError("fetch failed")))).toEqual([]);
  });
});
