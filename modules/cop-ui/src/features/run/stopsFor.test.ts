import { describe, expect, it } from "vitest";
import { RUN_STOPS } from "./runStops";
import { stopsFor } from "./stopsFor";

describe("stopsFor", () => {
  it("gives the night demo its scene stops", () => {
    expect(stopsFor("baengnyeong_night")).toEqual(RUN_STOPS);
  });
  it("gives any other operation, or none known, no stops", () => {
    expect(stopsFor("baengnyeong_24h")).toEqual([]);
    expect(stopsFor(null)).toEqual([]);
  });
});
