import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import { loadEditorData } from "./loadEditorData";

const json = (body: unknown, status = 200) => Promise.resolve(new Response(JSON.stringify(body), { status }));

describe("loadEditorData", () => {
  it("uses the gateway when all calls succeed", async () => {
    const op = { ...scenario.operation, id: "op-gw" };
    const body: Record<string, unknown> = { "/operation": op, "/plays": [scenario.plays[0]], "/vehicles": scenario.vehicles };
    const d = await loadEditorData((url) => json(body[url]));
    expect(d.operation.id).toBe("op-gw");
    expect(d.plays).toHaveLength(1);
    expect(d.vehicles.map((v) => v.id)).toEqual(scenario.operation.vehicle_ids);
  });
  // No example-data fallback any more (09 §4.5): without the gateway the editor says so instead of
  // showing the scenario file, where saving would fail.
  it("fails on a network error", async () => {
    await expect(loadEditorData(() => Promise.reject(new TypeError("fetch failed")))).rejects.toThrow("fetch failed");
  });
  it("fails on a non-2xx answer", async () => {
    await expect(loadEditorData(() => json({ detail: "x" }, 500))).rejects.toThrow("500");
  });
  it("fails when a 200 JSON reply is not an operation and a play list", async () => {
    await expect(loadEditorData((url) => json(url === "/operation" ? null : {}))).rejects.toThrow("shape");
  });
  it("fails when the dev server answers index.html", async () => {
    await expect(loadEditorData(() => Promise.resolve(new Response("<!doctype html>", { status: 200 })))).rejects.toThrow();
  });
});
