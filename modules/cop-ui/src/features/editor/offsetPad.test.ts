import { describe, expect, it } from "vitest";
import { offsetPad } from "./offsetPad";

describe("offsetPad: the relative route drawing pad (Part1-40)", () => {
  it("shows at least 1 km each way around the vehicle, with a 100 m grid", () => {
    const pad = offsetPad([], 400);
    expect(pad.half).toBe(1000);
    expect(pad.grid).toBe(100);
    expect(pad.toXY({ north_m: 0, east_m: 0 })).toEqual([200, 200]);
    expect(pad.toXY({ north_m: 1000, east_m: 500 })).toEqual([300, 0]);
  });
  it("a click becomes north/east metres from the centre, in 10 m steps", () => {
    const pad = offsetPad([], 400);
    expect(pad.fromXY(300, 0)).toEqual({ north_m: 1000, east_m: 500 });
    expect(pad.fromXY(241, 264)).toEqual({ north_m: -320, east_m: 210 });
  });
  it("grows to keep typed points on the pad, with a coarser grid", () => {
    const pad = offsetPad([{ north_m: 2200, east_m: -300 }], 400);
    expect(pad.half).toBe(2500);
    expect(pad.grid).toBe(250);
    expect(pad.toXY({ north_m: 2500, east_m: -2500 })).toEqual([0, 0]);
  });
});

describe("offsetPad labels stay clear of the north mark (QA finding 4)", () => {
  it("a point near the top edge has its number below it; elsewhere above and right", () => {
    const pad = offsetPad([{ north_m: 900, east_m: 0 }, { north_m: 0, east_m: 500 }], 400); // 900 m: y = 20 px, no growth
    const [top, mid] = pad.labels;
    expect(top.textAt[1]).toBeGreaterThan(top.at[1]);
    expect(mid.textAt).toEqual([mid.at[0] + 7, mid.at[1] - 7]);
  });
  it("the north mark sits left of the vertical axis, not on it", () => {
    expect(offsetPad([], 400).north[0]).toBeLessThan(200);
  });
});
