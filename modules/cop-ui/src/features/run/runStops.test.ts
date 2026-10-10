import { describe, expect, it } from "vitest";
import { mmss } from "./mmss";
import { nextStop, RUN_STOPS, type RunStop } from "./runStops";

const STOPS: RunStop[] = [
  { offsetMs: 60_000, label: "a" },
  { offsetMs: 120_000, label: "b" },
];

describe("nextStop", () => {
  it("is the first stop after the current offset", () => {
    expect(nextStop(0, STOPS)).toEqual(STOPS[0]);
    expect(nextStop(90_000, STOPS)).toEqual(STOPS[1]);
  });
  it("moves on once the run sits exactly on a stop (right after a jump)", () => {
    expect(nextStop(60_000, STOPS)).toEqual(STOPS[1]);
  });
  it("is null after the last stop", () => {
    expect(nextStop(120_000, STOPS)).toBeNull();
  });
  it("stops just after each fixed scene of the strike-phase order, none in the strike itself (Part1-13.1)", () => {
    expect(RUN_STOPS.map((s) => [mmss(s.offsetMs), s.label])).toEqual([
      ["16:25", "보고 카드"], ["19:05", "드론1 귀환"], ["20:00", "드론2 직접 조종"], ["23:05", "고속정 등장"],
    ]);
  });
  it("uses the demo stops by default, in time order", () => {
    expect(nextStop(0)).toEqual(RUN_STOPS[0]);
    const offsets = RUN_STOPS.map((s) => s.offsetMs);
    expect(offsets).toEqual([...offsets].sort((x, y) => x - y));
  });
});
