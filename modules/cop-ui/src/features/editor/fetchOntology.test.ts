import { describe, expect, it } from "vitest";
import { fetchOntology } from "./fetchOntology";

const reply = (body: unknown, status = 200) => Promise.resolve(new Response(JSON.stringify(body), { status }));

describe("fetchOntology", () => {
  it("returns the server's view", async () => {
    const view = { ontology: { groups: [], kinds: [] }, vehicles: [] };
    expect(await fetchOntology(() => reply(view))).toEqual(view);
  });
  it("fails with the server's own words, not the status code (decision 0051)", async () => {
    const none = () => reply({ detail: "이 시나리오에는 온톨로지가 없습니다" }, 404);
    await expect(fetchOntology(none)).rejects.toThrow(/^이 시나리오에는 온톨로지가 없습니다$/);
  });
});
