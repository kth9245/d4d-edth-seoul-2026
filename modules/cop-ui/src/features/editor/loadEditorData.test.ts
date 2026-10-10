import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import { loadEditorData } from "./loadEditorData";

const json = (body: unknown, status = 200) => Promise.resolve(new Response(JSON.stringify(body), { status }));

describe("loadEditorData", () => {
  it("uses the gateway when both calls succeed", async () => {
    const op = { ...scenario.operation, id: "op-gw" };
    const d = await loadEditorData((url) => json(url === "/operation" ? op : [scenario.plays[0]]));
    expect(d.source).toBe("gateway");
    expect(d.operation.id).toBe("op-gw");
    expect(d.plays).toHaveLength(1);
  });
  it("falls back to the example scenario on a network error", async () => {
    const d = await loadEditorData(() => Promise.reject(new TypeError("fetch failed")));
    expect(d.source).toBe("example");
    expect(d.operation.id).toBe(scenario.operation.id);
    expect(d.plays).toHaveLength(8);
  });
  it("falls back on a non-2xx answer", async () => {
    const d = await loadEditorData(() => json({ detail: "x" }, 500));
    expect(d.source).toBe("example");
  });
  it("falls back when a 200 JSON reply is not an operation and a play list", async () => {
    const d = await loadEditorData((url) => json(url === "/operation" ? null : {}));
    expect(d.source).toBe("example");
    expect(d.plays).toHaveLength(8);
  });
  it("falls back when the dev server answers index.html", async () => {
    const d = await loadEditorData(() => Promise.resolve(new Response("<!doctype html>", { status: 200 })));
    expect(d.source).toBe("example");
  });
});
