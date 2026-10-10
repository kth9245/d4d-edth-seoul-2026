import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { Play } from "../../contracts.gen";
import { savePlay } from "./savePlay";

const play = scenario.plays[1] as unknown as Play;
const reply = (body: unknown, status = 200) => Promise.resolve(new Response(JSON.stringify(body), { status }));

describe("savePlay", () => {
  it("POSTs the play as JSON to /plays and returns the PlayCheck", async () => {
    const seen: { url: string; init?: RequestInit }[] = [];
    const check = { ok: false, issues: [{ code: "missing_report_point", step_id: "rush", message: "m" }] };
    const got = await savePlay(play, (url, init) => {
      seen.push({ url, init });
      return reply(check);
    });
    expect(got).toEqual(check);
    expect(seen[0].url).toBe("/plays");
    expect(seen[0].init?.method).toBe("POST");
    expect(JSON.parse(String(seen[0].init?.body)).id).toBe(play.id);
  });
  it("throws with the status and detail on a non-2xx answer", async () => {
    await expect(savePlay(play, () => reply({ detail: "bad play" }, 422))).rejects.toThrow("422");
  });
  it("throws when the server cannot be reached", async () => {
    await expect(savePlay(play, () => Promise.reject(new TypeError("fetch failed")))).rejects.toThrow();
  });
});
