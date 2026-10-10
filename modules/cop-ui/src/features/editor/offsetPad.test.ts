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
